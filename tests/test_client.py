import unittest

from unittest.mock import patch

from client import Client

class TestClient(unittest.TestCase):

    # setUp()
    def setUp(self):
        self.client = Client()

    # Testing start_client() method
    # def test_starting_client_without_host_address(self):
    #     """
    #     Test that socket cannot start without host address given
    #     """
    #     host = "127.0.0.1"
    #     port = 123456
    #     with self.assertRaises(ConnectionRefusedError):
    #         self.client.start_client(host, port)

    # TypeError

    #ConnectionRefused Errno 111





    # Testing process_user_command() method

    # Testing send_message() method (??)


if __name__ == '__main__':
    unittest.main()