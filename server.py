import socket
import time
from message import Message

HOST = '127.0.0.1'
PORT = 65432
SERVER_VERSION = 1.0


def check_command(com):
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
                "Server uptime": time.time() - start_time,
            }
            return uptime_dict

        case "info":
            info_dict = {
                "Server version": SERVER_VERSION,
                "Server start date": start_time,
            }
            return info_dict

        case "stop":
            shutdown = True
            return shutdown
        case _:
            error_msg = "Wrong command, try again"
            return error_msg



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    start_time = time.time()
    conn, addr = s.accept()
    with conn:
        print(f"Connected: {addr}")
        while True:
            mess = conn.recv(1024).decode("utf-8")
            print(f"Messsage received: {mess}")
            if not mess:
                break
            message = Message(mess)
            command = message.decode_message(mess)
            print(command)

            answer = check_command(command)
            print(f"Answer before encoding: {answer}")
            json_answer = message.encode_message(answer)
            print(f"Answer after encoding: {json_answer}")
            s.send(json_answer)
            print("Answer sent successfully")


print(f"Connection with {addr} lost, closing server")