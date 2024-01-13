from server import Server

HOST = '127.0.0.1'
PORT = 65432

server = Server(HOST, PORT)
server.start_server()


