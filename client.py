import socket
import threading

def receive_messages(client_socket):
    message = "GET_IP|" + input("Enter index: ")
    client_socket.send(message.encode('utf-8'))
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break

            type = data.split("|")[0]

            if type == "Client":
                target_ip, msg = data.split("|")[1], data.split("|")[2]
                target_ip = target_ip[1:-1]
                target_ip1, target_ip2 = target_ip.split(",")[0], target_ip.split(",")[1]
                print(msg)
                target_socket = connect_to_client(target_ip1, target_ip2) #(127.0.0.1, 61223)
                message = "Client_recv,done"
                target_socket.send(message.encode('utf-8'))
                target_socket.close()

            elif type == "IP":
                target_ip, self_ip = data.split("|")[1], data.split("|")[2] #(원하는 아이), (요청한 아이)
                target_ip = target_ip[1:-1]
                target_ip1, target_ip2 = target_ip.split(",")[0], target_ip.split(",")[1]
                target_socket = connect_to_client('localhost', int(target_ip2))
                message = "Client|" +self_ip+ "|" + input("Enter your message: ")
                target_socket.send(message.encode('utf-8'))
                """ target_socket.close() """

            elif type == "Client_recv":
                msg = data.split("|")[1]
                print(msg)

        except ConnectionResetError:
            break


def connect_to_client(target_ip, target_port):
    target_address = (target_ip, target_port)
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect(target_address)
    return target_socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))  # Assuming the server is running on the same machine

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()


if __name__ == "__main__":
    start_client()
