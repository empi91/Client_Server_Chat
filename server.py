import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected: {addr}")
        while True:
            header_len = int(conn.recv(2))
            print(f"Header length: {header_len}")
            data = conn.recv(header_len).decode("utf-8")
            if not data:
                break
            print(data)