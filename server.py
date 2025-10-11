"""Server module for handling client connections and requests.

This module provides the Server class that manages client connections,
processes various types of messages, and coordinates with the database
for user management and message storage.
"""

import errno
from argon2 import PasswordHasher       # pip install argon2-cffi
from argon2.exceptions import VerifyMismatchError
from message import Message
from datetime import datetime
from connection import Connection
from db import DbHelper
from config import config


class Server:
    """Socket server for handling client connections and requests.

    Manages client connections, processes various message types including
    commands, authentication, and user messages. Coordinates with database
    for data persistence.
    """

    def __init__(self):
        """Initialize server with start time and database helper."""
        self.start_time = datetime.now()
        self.db_helper = DbHelper()
        self.server_host = config.network.HOST
        self.server_port = config.network.PORT

    def start_server(self):
        """Start the server and listen for client connections.

        Creates socket connection, binds to address, and handles
        incoming client connections and messages.
        """
        connection = Connection()
        with connection.create_connection(is_server=True) as s:
            s.bind((self.server_host, self.server_port))
            s.listen(config.network.MAX_CONNECTIONS)
            print("Server online")

            conn, addr = s.accept()
            with conn:
                print(f"Client connected: {addr}")
                while True:
                    rec_mess = conn.recv(
                        config.network.BUFFER_SIZE).decode("utf-8")
                    if not rec_mess:
                        break
                    recv_message = Message()
                    recv_message.decode_message(rec_mess)

                    try:
                        sending_msg = self.process_message(
                            recv_message, connection)
                        json_answer = sending_msg.encode_message()
                        conn.send(json_answer)

                    except IOError as e:
                        if e.errno == errno.EPIPE:
                            print("[ERROR] Broken pipe error")
                            break

    def process_message(
            self,
            message: Message,
            connection: Connection) -> Message:
        """Process incoming messages and generate appropriate responses.

        Routes different message types to appropriate handlers and returns
        the corresponding response message.

        Args:
            message: The incoming message to process.
            connection: The connection object for server details.

        Returns:
            A response Message object.
        """
        if message.header == "Command":
            return self.handle_command(message, connection)

        elif message.header == "Authentication":
            return self.handle_authentication(message, connection)

        elif message.header == "Acc_type":
            return self.handle_account_type(message, connection)

        elif message.header == "Message":
            return self.handle_sending_message(message, connection)

        else:
            message = Message(
                "Error",
                "Invalid message header",
                self.server_host,
                message.sender)
            return message

    def handle_command(
            self,
            message: Message,
            connection: Connection) -> Message:
        """Handle server commands from clients.

        Processes commands like help, uptime, info, inbox, stop,
        and message sending. Returns appropriate responses.
        """
        match message.text.lower():
            case "help":
                comm_dict = {
                    "HELP": config.ui.HELP_TEXT,
                }

                return Message(
                    "Command",
                    comm_dict,
                    self.server_host,
                    message.sender)

            case "uptime":
                days, hours, minutes, seconds = self.calc_uptime()
                uptime_dict = {
                    "Server uptime": f"Server is active for {days} days. {hours} hours, {minutes} minutes and {seconds} seconds"}
                return Message(
                    "Command",
                    uptime_dict,
                    self.server_host,
                    message.sender)

            case "info":
                info_dict = {
                    "Server version": config.server.SERVER_VERSION,
                    "Server start date": f"{self.start_time}"
                }

                return Message(
                    "Command",
                    info_dict,
                    self.server_host,
                    message.sender)

            case "inbox":
                messages = self.db_helper.get_msg_from_inbox(message.sender)

                for msg in messages:
                    if msg["Text"] == "EMPTY":
                        return Message(
                            "Error",
                            "Inbox empty",
                            self.server_host,
                            msg["Sender"])
                    else:
                        return Message(
                            "Inbox_message",
                            messages,
                            self.server_host,
                            message.sender)

            case "stop":
                return Message(
                    "Stop",
                    "Stop",
                    self.server_host,
                    message.sender)

    def handle_authentication(
            self,
            message: Message,
            connection: Connection) -> Message:
        """Handle user authentication and registration.

        Verifies user credentials or registers new users with hashed passwords.

        Args:
            message: The incoming authentication message.

        Returns:
            A response Message object with authentication status.
        """
        authenticator = UserAuthenticator(message.text)
        auth_dict = authenticator.verify_login()

        message = Message(
            "Authentication_answer",
            auth_dict,
            self.server_host,
            message.sender)
        return message

    def handle_account_type(
            self,
            message: Message,
            connection: Connection) -> Message:
        """Handle account type updates for users.

        Updates the account type for a user based on the provided message.

        Args:
            message: The incoming message containing account type information.

        Returns:
            A response Message object with the update status.
        """
        update_status = self.db_helper.add_account_type(message.text)
        acc_update_dict = {
            "update_status": update_status,
        }

        message = Message(
            "Account_type_update",
            acc_update_dict,
            self.server_host,
            message.sender)
        return message

    def handle_sending_message(
            self,
            message: Message,
            connection: Connection) -> Message:
        """Handle sending messages between users.

        Checks if the receiver exists and if their inbox is not full,
        then stores the message in the database.

        Args:
            message: The incoming message containing sender, receiver, and text.

        Returns:
            A response Message object with the status of the operation.
        """
        if self.db_helper.check_if_registered(message.receiver):
            if self.db_helper.check_recv_inbox(message.receiver):
                status = self.db_helper.add_msg_to_db(
                    message.receiver, message.sender, message.text)

                message = Message(
                    "Status",
                    status,
                    self.server_host,
                    message.sender)
                return message
            else:
                status = "Receiver inbox is full"

                message = Message(
                    "Error",
                    status,
                    self.server_host,
                    message.sender)
                return message
        else:
            status = "Receiver not existing in database"

            message = Message(
                "Error",
                status,
                self.server_host,
                message.sender)
            return message

    def calc_uptime(self) -> tuple[int, int, int, int]:
        """Calculate server uptime since startup.

        Returns:
            A tuple containing (days, hours, minutes, seconds) of uptime.
        """
        now_time = datetime.now()
        uptime_delta = now_time - self.start_time
        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60
        seconds = uptime_delta.seconds

        return days, hours, minutes, seconds


class UserAuthenticator():
    """Handles user authentication and password verification.

    Manages user login verification, password hashing, and new user
    registration with secure password storage.
    """

    def __init__(self, message):
        self.text = message
        self.db_helper = DbHelper()

    def verify_login(self) -> dict:
        """Verify user login credentials or register new user.

        Checks if user exists and verifies password, or registers
        new user with hashed password if not found.

        Returns:
            Dictionary containing authentication status information.
        """
        if self.db_helper.check_if_registered(self.text["login"]):
            stored_password = self.db_helper.get_stored_password(
                self.text["login"])
            if self.verify_password(self.text["password"], stored_password):
                answer = {
                    "is_registered": True,
                    "login_successfull": True,
                }
            else:
                answer = {
                    "is_registered": True,
                    "login_successfull": False,
                }
        else:
            hashed_password = self.hash_password(self.text["password"])
            self.db_helper.register_new_user(
                self.text["login"], hashed_password)
            answer = {
                "is_registered": False,
                "login_successfull": True,
            }

        return answer

    def verify_password(self, input_pass: str, stored_pass: str) -> bool:
        """Verify password against stored hash.

        Args:
            input_pass: The plaintext password to verify.
            stored_pass: The stored password hash.

        Returns:
            True if password matches, False otherwise.
        """
        ph = PasswordHasher()
        try:
            ph.verify(stored_pass, input_pass)
            return True
        except VerifyMismatchError:
            return False
        # if stored_pass == input_pass:
        #     return True
        # return False

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2.

        Args:
            password: The plaintext password to hash.

        Returns:
            The hashed password string.
        """
        ph = PasswordHasher()  # removing argon2 for iPad
        return ph.hash(password)  # removing argon2 for iPad
        # return password
