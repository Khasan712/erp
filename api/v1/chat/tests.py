from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from channels.testing import HttpCommunicator
from api.v1.chat.consumers import ChatConsumer


class MyTests(TestCase):
    async def test_my_consumer(self):
        communicator = HttpCommunicator(ChatConsumer.as_asgi(), "connect", "/test/")
        response = await communicator.get_response()
        self.assertEqual(response["body"], b"test response")
        self.assertEqual(response["status"], 200)

    