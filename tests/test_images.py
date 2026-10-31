import io
import unittest
from unittest.mock import Mock, patch

import boto3
from botocore.exceptions import ClientError
from PIL import Image

# Isolate module-level S3 initialization: never use credentials or contact B2.
with patch.object(boto3, 'resource'):
    import upload.backblaze as backblaze
    from agents.img import ImageAgent
    from agents.env import EnvironmentAgent

import config


class ImageTests(unittest.TestCase):
    def test_b2_key_url_and_environment_inheritance(self):
        with patch.object(config, 'B2_ASSET_DIR', 'assets'), patch.object(
                config, 'B2_BASEURL', 'https://cdn.example/bucket'):
            agent = ImageAgent('img_card_123.webp')
            self.assertEqual(agent.asset_path, 'assets/img/card/123.webp')
            self.assertEqual(agent.generate_url(), 'https://cdn.example/bucket/assets/img/card/123.webp')
            self.assertEqual(EnvironmentAgent('env_room_123').asset_path, 'assets/env/room/123.webp')

    def test_exists_check_and_upload_use_identical_webp_key(self):
        agent = ImageAgent('img_card_123')
        with patch('agents.img.exists_file', return_value=True) as exists:
            self.assertFalse(agent.shall_upload())
            exists.assert_called_once_with(agent.asset_path)
        with patch('agents.img.exists_file', return_value=False):
            self.assertTrue(agent.shall_upload())
        with patch('agents.img.upload_file') as upload:
            agent.upload_object(Image.new('RGBA', (2, 2), 'red'))
            data, key, content_type = upload.call_args.args
            self.assertEqual(key, agent.asset_path)
            self.assertEqual(content_type, 'image/webp')
            self.assertEqual(Image.open(io.BytesIO(data)).format, 'WEBP')

    def test_head_missing_vs_errors(self):
        with patch.object(backblaze, 'bucket') as bucket:
            obj = bucket.Object.return_value
            self.assertTrue(backblaze.exists_file('image.webp'))
            for code in ('404', 'NoSuchKey', 'NotFound'):
                obj.load.side_effect = ClientError({'Error': {'Code': code}}, 'HeadObject')
                self.assertFalse(backblaze.exists_file('image.webp'))
            obj.load.side_effect = ClientError({'Error': {'Code': '403'}}, 'HeadObject')
            with self.assertRaises(ClientError):
                backblaze.exists_file('image.webp')
            obj.load.side_effect = OSError('network')
            with self.assertRaises(OSError):
                backblaze.exists_file('image.webp')

    def test_upload_sets_content_type(self):
        with patch.object(backblaze, 'bucket') as bucket:
            backblaze.upload_file(b'webp', 'assets/img/test.webp', 'image/webp')
            bucket.put_object.assert_called_once_with(
                Body=b'webp', Key='assets/img/test.webp', ContentType='image/webp')


if __name__ == '__main__':
    unittest.main()
