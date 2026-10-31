"""Local, cross-worker sliding-window IP limits (no external service required)."""
from contextlib import closing
import ipaddress
import math
import sqlite3
import time

import config


class LocalIPRateLimiter:
    def __init__(self, db_path, clock=time.time):
        self.db_path = db_path
        self.clock = clock

    def check(self, ip):
        """Record an allowed request; return retry seconds, or zero if allowed."""
        with closing(sqlite3.connect(self.db_path, timeout=5)) as db, db:
            # Serialize the read/check/write across threads and Gunicorn workers.
            db.execute('BEGIN IMMEDIATE')
            now = self.clock()
            db.execute('CREATE TABLE IF NOT EXISTS rate_requests '
                       '(ip TEXT NOT NULL, requested_at REAL NOT NULL)')
            db.execute('CREATE INDEX IF NOT EXISTS rate_requests_ip_time '
                       'ON rate_requests (ip, requested_at)')
            db.execute('CREATE INDEX IF NOT EXISTS rate_requests_time '
                       'ON rate_requests (requested_at)')
            db.execute('DELETE FROM rate_requests WHERE requested_at <= ?',
                       (now - 3600,))
            timestamps = [row[0] for row in db.execute(
                'SELECT requested_at FROM rate_requests WHERE ip = ? '
                'ORDER BY requested_at', (ip,))]
            retry = 0
            if len(timestamps) >= 600:
                retry = max(retry, math.ceil(timestamps[-600] + 3600 - now))
            if retry:
                return max(1, retry)
            db.execute('INSERT INTO rate_requests VALUES (?, ?)', (ip, now))
        return 0


def client_ip(remote_addr, headers):
    # Only enable this behind a Cloudflare-only ingress that strips forged headers.
    if (config.IS_BEHIND_CLOUDFLARE or '').lower() == 'true':
        candidate = headers.get('CF-Connecting-IP')
        if candidate:
            try:
                return str(ipaddress.ip_address(candidate))
            except ValueError:
                pass
    try:
        address = ipaddress.ip_address(remote_addr or '')
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
            address = address.ipv4_mapped
        return str(address)
    except ValueError:
        return remote_addr or 'unknown'


def rate_limit_key(ip):
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    prefix_length = 24 if address.version == 4 else 48
    return str(ipaddress.ip_network(f'{address}/{prefix_length}', strict=False))


limiter = LocalIPRateLimiter(config.RATE_LIMIT_DB_PATH)
bypass_rate_limit_ip_range = set(config.BYPASS_RATE_LIMIT_IP_RANGE.split(","))


def check_request(remote_addr, headers):
    """Return a rejection (status, body, headers), or None to proceed."""
    client_ip_group = client_ip(remote_addr, headers)
    if client_ip_group in bypass_rate_limit_ip_range:
        return None
    try:
        retry = limiter.check(rate_limit_key())
    except sqlite3.Error:
        # Do not silently disable protection when local storage is unavailable.
        return 503, 'Service unavailable', {'Cache-Control': 'no-store'}
    if retry:
        return 429, 'Too many requests', {
            'Retry-After': str(retry), 'Cache-Control': 'no-store',
        }
    return None
