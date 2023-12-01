import socket
import threading

def handle_client(client_socket, clients):
    while True:
        data = client_socket.recv(1024).decode("utf-8")
        if not data:
            break

        print(f"Received message from {client_socket.getpeername()}: {data}")

        type = data.split(",")[0]
        # Check if the message is a request for another client's IP
        if type == "GET_IP":
            client_index = int(data.split(",")[1])
            target_ip = clients[client_index][1][0]
            print(client_socket.getpeername())
            print("클라이언트가 요청한 ip 보내주기" + target_ip)
            message = "IP," + target_ip +","+ str(client_socket.getpeername())
            client_socket.send(message.encode('utf-8'))

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(4)
    print("Server listening on port 12345")

    clients = []

    while len(clients) < 4:
        client, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        clients.append((client, addr))
        client_handler = threading.Thread(target=handle_client, args=(client, clients))
        client_handler.start()

if __name__ == "__main__":
    start_server()
