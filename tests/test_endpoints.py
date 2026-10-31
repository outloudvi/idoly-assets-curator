import importlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_images import ImageAgent  # Initializes B2 under a mock, without network.
import app
import rate_limit
from rate_limit import LocalIPRateLimiter


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        limiter = LocalIPRateLimiter(str(Path(self.directory.name) / 'rate.sqlite3'), clock=lambda: 10000)
        self.patcher = patch.object(rate_limit, 'limiter', limiter)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_flask_limits_shared_across_routes_before_processing(self):
        with app.app.test_client() as client, patch.object(
                app.ImageAgent, 'process', return_value=(308, 'https://cdn.example/test.webp')) as process:
            for _ in range(600):
                self.assertEqual(client.get('/api/img/img_test').status_code, 308)
            response = client.get('/api/env/env_test')
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers['Retry-After'], '3600')
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertEqual(process.call_count, 600)
            self.assertEqual(client.get('/api/img/img_test', environ_base={'REMOTE_ADDR': '192.0.2.2'}).status_code, 308)
            self.assertEqual(client.get('/').status_code, 404)

    def test_vercel_handlers_reject_before_agent(self):
        for name in ('img', 'env'):
            module = importlib.import_module('vercel.' + name)
            handler = module.handler.__new__(module.handler)
            handler.client_address = ('192.0.2.1', 12345)
            handler.headers = {}
            handler.path = '/api/' + name + '/' + name + '_test'
            handler.wfile = io.BytesIO()
            with patch.object(module, 'check_request', return_value=(429, 'Too many requests', {
                    'Retry-After': '3600', 'Cache-Control': 'no-store'})), patch.object(
                    handler, 'send_response') as status, patch.object(
                    handler, 'send_header') as header, patch.object(handler, 'end_headers'):
                handler.do_GET()
                status.assert_called_once_with(429)
                header.assert_any_call('Retry-After', '3600')
                self.assertEqual(handler.wfile.getvalue(), b'Too many requests')

    def test_storage_hit_without_flask_context(self):
        agent = ImageAgent('img_card_123')
        with patch.object(agent, 'shall_upload', return_value=False), patch.object(
                agent, 'generate_url', return_value='https://cdn.example/image.webp'):
            cache = set()
            self.assertEqual(agent.process(cache)[0], 308)
            self.assertEqual(agent.process(cache)[0], 308)


if __name__ == '__main__':
    unittest.main()
