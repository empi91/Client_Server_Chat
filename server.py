import socket
import time
import errno
from message import Message

HOST = '127.0.0.1'
PORT = 65432
SERVER_VERSION = '1.0.1'


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
                "Server uptime": calc_uptime(start_time),
            }
            return uptime_dict

        case "info":
            info_dict = {
                "Server version": SERVER_VERSION,
                "Server start date": f"{start_time.tm_year}/{start_time.tm_mon}/{start_time[2]} {start_time.tm_hour}:{start_time.tm_min}:{start_time.tm_sec}"
            }
            return info_dict

        case "stop":
            shutdown = True
            return shutdown
        case _:
            error_msg = "Wrong command, try again"
            return error_msg


def calc_uptime(start):
    curr_time = time.gmtime()
    uptime = f"{curr_time[0] - start[0]} Years {curr_time[1] - start[1]} Months {curr_time[2] - start[2]} Days {curr_time[3] - start[3]} Hours {curr_time[4] - start[4]} Minutes {curr_time[5] - start[5]} Seconds"

    return uptime


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    start_time = time.gmtime()
    conn, addr = s.accept()
    with conn:
        print(f"Connected: {addr}")
        while True:
            mess = conn.recv(1024).decode("utf-8")
            if not mess:
                break
            message = Message(mess)
            command = message.decode_message(mess)
            print(command)

            try:
                answer = check_command(command)
                json_answer = message.encode_message(answer)
                conn.send(json_answer)

            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass

print(f"Connection with {addr} lost, closing server")