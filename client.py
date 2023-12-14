import socket
HOST = "127.0.0.1"
PORT = 9090
def send(txt):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(txt.encode("utf-8"))

send("1")
send("2")
send("3")
send("4")
