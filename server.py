# server.py 

# import socket
import errno
from message import Message
from datetime import datetime
from connection import Connection

class Server:
    start_time = 0
    SERVER_VERSION = '1.1.0'

    def __init__(self):
        self.start_time = datetime.now()

    def start_server(self):
        connection = Connection()
        with connection.create_server_connection() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((connection.host, connection.port))
            s.listen(5)
            print("Server online")
            
            conn, addr = s.accept()
            with conn:
                print(f"Client connected: {addr}")
                while True:
                    rec_mess = conn.recv(1024).decode("utf-8")
                    if not rec_mess:
                        break
                    message = Message(rec_mess)
                    header, text = message.decode_message(rec_mess)
                    print(f"Received: {text}")

                    try:
                        message.header, message.text = self.check_command(header, text)
                        json_answer = message.encode_message()
                        conn.send(json_answer)

                    except IOError as e:
                        if e.errno == errno.EPIPE:
                            pass
    
    def check_command(self, head, text):
        if head == "Command":
            match text.lower():
                case "help":
                    comm_dict = {
                        "help": "Displays list of all server commands",
                        "uptime": "Returns server lifetime",
                        "info": "Returns server version and start date",
                        "stop": "Stops server and client simultaneously"
                    }
                    return "Command", comm_dict

                case "uptime":
                    days, hours, minutes, seconds = self.calc_uptime()
                    uptime_dict = {
                        "Server uptime": f"Server is active for {days} days. {hours} hours, {minutes} minutes and {seconds} seconds"
                    }
                    return "Command", uptime_dict

                case "info":
                    info_dict = {
                        "Server version": self.SERVER_VERSION,
                        "Server start date": f"{self.start_time}"
                    }
                    return "Command", info_dict
                case "stop":
                    return "Command", "Stop"
        else:
            return "Message", text
        
    def calc_uptime(self) -> tuple[int, int, int, int]:
        now_time = datetime.now()
        uptime_delta = now_time - self.start_time
        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60
        seconds = uptime_delta.seconds

        return days, hours, minutes, seconds
