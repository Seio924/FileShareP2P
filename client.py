import socket
import threading

class P2PClient:
    def __init__(self, server_port):
        self.server_port = server_port
        self.server_socket = None
        self.peer_id = None

    def connect_to_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(('localhost', self.server_port))
        threading.Thread(target=self.receive_peer_info).start()

    def receive_peer_info(self):
        peer_info = self.server_socket.recv(1024).decode('utf-8')
        peer_ports, client_number = eval(peer_info)
        print(f"Received peer info: {peer_ports}, {client_number}")

        # 현재 클라이언트 번호에 해당하는 포트로 피어 설정
        self.peer_id = f"localhost:{peer_ports[client_number - 1]}"
        print(f"Setting peer id to {self.peer_id}")
        threading.Thread(target=self.connect_to_peer).start()

    def connect_to_peer(self):
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect(('localhost', self.server_port))  # 서버 포트를 사용
        threading.Thread(target=self.receive_messages, args=(peer_sock,)).start()

    def receive_messages(self, peer_sock):
        while True:
            msg = peer_sock.recv(1024)
            if not msg:
                print("피어와의 연결이 끊어졌습니다.")
                peer_sock.close()
                break
            print(f"피어로부터 받은 메시지: {msg.decode('utf-8')}")

    def send_message(self, message):
        if self.peer_id:
            full_message = f"{self.peer_id}: {message}"
            self.server_socket.send(full_message.encode('utf-8'))
        else:
            print("서버에 연결되어 있지 않거나 피어가 설정되어 있지 않습니다.")

if __name__ == "__main__":
    # 서버 포트 설정
    server_port = 9000

    # 클라이언트 생성 및 서버에 연결
    p2p_client = P2PClient(server_port)
    p2p_client.connect_to_server()

    # 클라이언트가 계속해서 메시지를 전송할 수 있도록 유지
    while True:
        message = input("메시지를 입력하세요 (끝내려면 엔터 키): ")
        if not message:
            break
        p2p_client.send_message(message)
