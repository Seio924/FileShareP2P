import socket
import threading

def connect_to_server(server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('localhost', server_port))
    threading.Thread(target=receive_peer_info, args=(server_socket,)).start()

def connect_to_peer(peer_id, peer_port):
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_sock.connect(('localhost', peer_port))
    threading.Thread(target=receive_messages, args=(peer_sock,)).start()

def receive_peer_info(server_socket):
    peer_info = server_socket.recv(1024).decode('utf-8')
    peer_ports, client_number = eval(peer_info)
    print(f"Received peer info: {peer_ports}, {client_number}")

    # 현재 클라이언트 번호에 해당하는 포트로 피어 설정
    peer_port = peer_ports[client_number - 1]
    print(f"Setting peer port to {peer_port}")
    threading.Thread(target=connect_to_peer, args=(peer_id, peer_port)).start()

def receive_messages(peer_sock):
    while True:
        msg = peer_sock.recv(1024)
        if not msg:
            print("피어와의 연결이 끊어졌습니다.")
            peer_sock.close()
            break
        print(f"피어로부터 받은 메시지: {msg.decode('utf-8')}")

if __name__ == "__main__":
    # 서버 포트 설정
    server_port = 9000

    # 클라이언트 생성 및 서버에 연결
    connect_to_server(server_port)
