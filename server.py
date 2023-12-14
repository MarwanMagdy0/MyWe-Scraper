import socket

HOST = "127.0.0.1"
PORT = 9090
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
while True:
    commu, addr = server.accept()
    message = commu.recv(1024).decode("utf-8")
    print(message)
