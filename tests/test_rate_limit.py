import subprocess
import sys
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import config
import rate_limit
from rate_limit import LocalIPRateLimiter, client_ip, rate_limit_key


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = os.path.join(self.directory.name, 'rate.sqlite3')
        self.now = 10000.0
        self.limiter = LocalIPRateLimiter(self.path, clock=lambda: self.now)

    def test_minute_boundary_and_independent_ips(self):
        self.assertEqual([self.limiter.check('a') for _ in range(30)], [0] * 30)
        self.assertEqual(self.limiter.check('a'), 60)
        self.assertEqual(self.limiter.check('b'), 0)
        self.now += 59.1
        self.assertEqual(self.limiter.check('a'), 1)
        self.now += 0.9
        self.assertEqual(self.limiter.check('a'), 0)

    def test_hour_limit_and_rejected_requests_not_counted(self):
        for minute in range(20):
            self.now = 10000.0 + minute * 60
            for _ in range(30):
                self.assertEqual(self.limiter.check('a'), 0)
        self.now = 11200.0
        self.assertEqual(self.limiter.check('a'), 2400)
        self.now = 13600.0
        self.assertEqual(self.limiter.check('a'), 0)

    def test_shared_database_across_instances_and_threads(self):
        def check(_):
            return LocalIPRateLimiter(self.path, clock=lambda: self.now).check('a')
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(check, range(50)))
        self.assertEqual(results.count(0), 30)
        self.assertEqual(results.count(60), 20)

    def test_shared_database_across_processes(self):
        script = (
            'import sys; from rate_limit import LocalIPRateLimiter; '
            'limiter = LocalIPRateLimiter(sys.argv[1], clock=lambda: 10000.0); '
            'print(sum(limiter.check("shared") == 0 for _ in range(15)))'
        )
        processes = [subprocess.Popen(
            [sys.executable, '-c', script, self.path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ) for _ in range(4)]
        accepted = 0
        for process in processes:
            stdout, stderr = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, stderr)
            accepted += int(stdout.strip())
        self.assertEqual(accepted, 30)

    def test_forwarded_headers_are_not_trusted_by_default(self):
        with patch.object(config, 'IS_BEHIND_CLOUDFLARE', None):
            self.assertEqual(client_ip('192.0.2.1', {
                'CF-Connecting-IP': '192.0.2.2', 'X-Forwarded-For': '192.0.2.3',
            }), '192.0.2.1')
            self.assertEqual(client_ip('::ffff:192.0.2.1', {}), '192.0.2.1')

    def test_cloudflare_opt_in_and_invalid_header(self):
        with patch.object(config, 'IS_BEHIND_CLOUDFLARE', 'true'):
            self.assertEqual(client_ip('192.0.2.1', {'CF-Connecting-IP': '2001:0db8::1'}), '2001:db8::1')
            self.assertEqual(client_ip('192.0.2.1', {'CF-Connecting-IP': 'bad'}), '192.0.2.1')

    def test_rate_limit_key_uses_ipv4_24_and_ipv6_48(self):
        self.assertEqual(rate_limit_key('192.0.2.1'), '192.0.2.0/24')
        self.assertEqual(rate_limit_key('192.0.2.254'), '192.0.2.0/24')
        self.assertEqual(rate_limit_key('192.0.3.1'), '192.0.3.0/24')
        self.assertEqual(rate_limit_key('2001:db8:1234:5678::1'), '2001:db8:1234::/48')
        self.assertEqual(rate_limit_key('2001:db8:1234:ffff::1'), '2001:db8:1234::/48')
        self.assertEqual(rate_limit_key('2001:db8:1235::1'), '2001:db8:1235::/48')
        self.assertEqual(rate_limit_key('192.0.2.1'), rate_limit_key('::ffff:192.0.2.1'))

    def test_requests_share_quota_within_subnet(self):
        with patch.object(rate_limit, 'limiter', self.limiter):
            for _ in range(30):
                self.assertIsNone(rate_limit.check_request('192.0.2.1', {}))
            self.assertEqual(rate_limit.check_request('192.0.2.254', {})[0], 429)
            self.assertIsNone(rate_limit.check_request('192.0.3.1', {}))

            for _ in range(29):
                self.assertIsNone(rate_limit.check_request('2001:db8:1234::1', {}))
            self.assertIsNone(rate_limit.check_request('2001:db8:1234:ffff::1', {}))
            self.assertEqual(rate_limit.check_request('2001:db8:1234:abcd::1', {})[0], 429)
            self.assertIsNone(rate_limit.check_request('2001:db8:1235::1', {}))

    def test_response_headers_and_database_failure(self):
        with patch.object(rate_limit, 'limiter', self.limiter):
            for _ in range(30):
                self.assertIsNone(rate_limit.check_request('192.0.2.1', {}))
            status, _, headers = rate_limit.check_request('192.0.2.1', {})
            self.assertEqual(status, 429)
            self.assertEqual(headers, {'Retry-After': '60', 'Cache-Control': 'no-store'})
        broken = LocalIPRateLimiter(os.path.join(self.path, 'missing'))
        with patch.object(rate_limit, 'limiter', broken):
            self.assertEqual(rate_limit.check_request('192.0.2.1', {})[0], 503)


if __name__ == '__main__':
    unittest.main()
