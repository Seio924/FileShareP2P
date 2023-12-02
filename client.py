import socket
import threading

# 서버 IP 주소와 포트
server_ip = '서버_IP_주소'
server_port = 12345  # 사용할 포트 번호

connecting_client_list = []

def handle_server_connection(client_socket):
    try:
        # 서버에게 메시지 전송
        message_to_server = "클라이언트에서 서버로의 메시지입니다."
        client_socket.sendall(message_to_server.encode())

        # 서버로부터 응답 수신
        response = client_socket.recv(1024)
        print(f"서버로부터의 응답: {response.decode()}")

        # 서버로부터 받은 메시지 반환
        return response.decode()

    except Exception as e:
        print(f"통신 에러: {e}")
        return None
    finally:
        # 소켓 닫기
        client_socket.close()
        print("쓰레드 종료")

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 서버에 연결
        client_socket.connect((server_ip, server_port))
        print(f"서버에 연결되었습니다. 서버 IP: {server_ip}, 포트: {server_port}")

        # 쓰레드 생성 및 시작
        thread = threading.Thread(target=handle_server_connection, args=(client_socket,))
        thread.start()

        # 쓰레드 종료 대기 및 서버로부터 받은 메시지 반환
        thread.join()
        return thread.result

    except Exception as e:
        print(f"연결 에러: {e}")
        return None

def connect_to_client(target_ip, target_port):
    target_address = (target_ip, target_port)
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect(target_address)
    return target_socket

def get_file(client_socket):
    while True:
        try:
            client_socket.sendall(message_to_server.encode())

            # 서버로부터 응답 수신
            response = client_socket.recv(1024)

        except ConnectionResetError:
            break

def give_file(client_socket):
    while True:
        try:
            client_socket.sendall(message_to_server.encode())

            # 서버로부터 응답 수신
            response = client_socket.recv(1024)

        except ConnectionResetError:
            break


def select_client():
    result_message = connect_to_server() # (주소)|(주소)

    clients_address = result_message.split("|")

    #result_message split해서 받은 모든 클라이언트의 주소 가져옴

    for i in clients_address:
        target_ip, target_port= i[1:-1].split(",")
        connecting_client_list.append(connect_to_client(target_ip, int(target_port))) # for문 돌려서 배열에 넣기

    # 메시지 전송을 위한 쓰레드 생성
    #for문 돌려서 배열 수 만큼 쓰레드 생성

    for i in connecting_client_list:
        client_thread = threading.Thread(target=handle_clients_connection, args=(i))
        client_thread.start()


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 주소와 포트 바인딩
    client_socket.bind(('localhost', 8888))

    # 연결 대기
    client_socket.listen(4)

    while True:
        try:
            count = count + 1
            conn, addr = client_socket.accept()  # 해당 소켓을 열고 대기
            
            thread1 = threading.Thread(target=get_file, args=(conn))
            thread2 = threading.Thread(target=give_file, args=(conn))
            thread1.start()
            thread2.start()

            
        except:
            exit(0)
    start_client()