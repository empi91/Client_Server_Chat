import socket
import time
import errno
import pathlib
import json

from message import Message


class Server:
    database = {}
    start_time = 0
    SERVER_VERSION = '1.0.1'

    def __init__(self, host, port, database_path):
        self.host = host
        self.port = port
        self.database_path = database_path

    def load_database(self):
        try:
            with self.database_path.open(mode="r", encoding="utf-8") as file:
                self.database = json.load(file)
        except FileNotFoundError:
            self.database = {}
        print("Database loaded")

    def add_to_database(self, username, user_data):
        self.database[username] = user_data
        with self.database_path.open(mode="w", encoding="utf-8") as file:
            json.dump(self.database, file, indent=2)

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen()
        self.start_time = time.gmtime()
        print("Server online")

        self.load_database()
        
        conn, addr = s.accept()
        with conn:
            print(f"Client connected: {addr}")
            while True:
                received_data = conn.recv(1024).decode("utf-8")
                if not received_data:
                    break
                message = Message(received_data)
                decoded_header, decoded_message = message.decode_message(received_data)
                print(decoded_header)

                try:
                    answer = self.check_command(decoded_message)
                    json_answer = message.encode_message(answer)
                    conn.send(json_answer)

                except IOError as e:
                    if e.errno == errno.EPIPE:
                        pass
    
    def check_command(self, com):
        match com:
            case "help":
                comm_dict = {
                    "help": "Displays list of all server commands",
                    "uptime": "Returns server lifetime",
                    "info": "Returns server version and start date",
                    "stop": "Stops server and client simultaneously"
                }
                return comm_dict

            case "uptime":
                uptime_dict = {
                    "Server uptime": self.calc_uptime(),
                }
                return uptime_dict

            case "info":
                info_dict = {
                    "Server version": self.SERVER_VERSION,
                    "Server start date": f"{self.start_time.tm_year}/{self.start_time.tm_mon}/{self.start_time[2]} {self.start_time.tm_hour}:{self.start_time.tm_min}:{self.start_time.tm_sec}"
                }
                return info_dict

            case "stop":
                shutdown = True
                return shutdown
            case _:
                error_msg = "Wrong command, try again"
                return error_msg
        
    def calc_uptime(self):
        curr_time = time.gmtime()
        uptime = f"{curr_time[0] - self.start_time[0]} Years {curr_time[1] - self.start_time[1]} Months {curr_time[2] - self.start_time[2]} Days {curr_time[3] - self.start_time[3]} Hours {curr_time[4] - self.start_time[4]} Minutes {curr_time[5] - self.start_time[5]} Seconds"

        return uptime
