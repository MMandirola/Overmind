from django.test import TestCase
from api.models import Replays
from django.conf import settings
import base64

# Folder where to store replay files
REPLAYS_DIR = settings.REPLAYS_DIR

class ReplaysTestCase(TestCase):
    def setUp(self):
        Replays.objects.create(title='test1', base64_file='aG9sYQ==', extra='')

    def test_replay_object(self):
        base64_file = Replays.objects.get(title='test1')
        self.assertEqual(str(base64_file), 'aG9sYQ==')

    def test_base64_to_file(self):
        base64_file = Replays.objects.get(title='test1')

        # Save base64 encoded file
        request_base64_file = str(base64_file)
        request_title = 'test1.SC2Replay'
        fullpath = REPLAYS_DIR + request_title
        replay_file = open(fullpath, "wb")
        replay_file.write(base64.b64decode(request_base64_file))
        replay_file.close()

        # Open decoded file
        replay_file = open(fullpath, "r")
        file_content = replay_file.read()
        replay_file.close()

        self.assertEqual(file_content, 'hola')