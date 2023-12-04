import socket
import threading


def receive_messages(peer_connection, thread_num):
    try:
        data = peer_connection.recv(1024).decode()
        print(data)
    except Exception as e:
        print(f"Error receiving data: {e}")

    # 파일 보내주기
    msg = thread_num + "번이 파일을 보냈습니다."
    peer_connection.send(msg.encode("utf-8"))
    
    

def peer_handler(client_socket, peer_connecting_sock, thread_num):
    #파일 나누고 자신한테 없는 파일들 정보 서버에게 물어보기
    msg = "Where_is"
    client_socket.send(msg.encode("utf-8"))

    # 연결할 클라이언트 ip랑 포트번호 받기
    data = client_socket.recv(1024).decode()
    print(data)

    target_ip, target_port = data.split("|")
    print(1)

    # 다른 클라이언트랑 연결
    peer_connecting_sock.connect((target_ip, int(target_port)))
    print(2)

    peer_msg = thread_num + "번이 파일을 요청했습니다."
    peer_connecting_sock.send(peer_msg.encode("utf-8"))
    print(3)

    peer_data = peer_connecting_sock.recv(1024).decode()
    print(peer_data)


if __name__ == "__main__":
    # 서버 포트 설정
    server_host = "localhost"
    server_port = 9000

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_connecting_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 서버에 연결
    client_socket.connect((server_host, server_port))

    
    data = client_socket.recv(1024).decode()
    
    print(data)

    #서버에게 내 아이피 주소와 포트번호를 받음
    type, my_ip, my_port, thread_num = data.split("|")

    #아이피 주소와 포트번호로 다른 클라이언트가 들어오는걸 대기
    peer_sock.bind((my_ip, int(my_port)))
    peer_sock.listen(4)


    thread_main = threading.Thread(target=peer_handler, args=(client_socket, peer_connecting_sock, thread_num))
    thread_main.start()

    while True:
        # Accept connection from a client
        peer_connection, peer_address = peer_sock.accept()

        # 스레드를 생성하여 receive_messages 함수 실행
        thread = threading.Thread(target=receive_messages, args=(peer_connection, thread_num))
        thread.start()
        