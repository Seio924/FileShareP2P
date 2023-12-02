import socket
import threading

# 서버 IP 주소와 포트
server_ip = '127.0.0.1'
server_port = 12345  # 사용할 포트 번호
g = []

def handle_client(client_socket):
    global g
    try:
        # 클라이언트로부터 데이터 수신 및 출력
        data = client_socket.recv(1024)
        print(f"수신: {data.decode()}")

        # 클라이언트에게 응답 전송
        response = str(g[-1].getpeername()) + "|"
        client_socket.send(bytes(response.encode()))
    except Exception as e:
        print(f"에러: {e}")
    finally:
        # 소켓 닫기
        print("끝")

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)

print(f"서버가 {server_ip}:{server_port}에서 시작되었습니다.")

while True:
    # 클라이언트 연결 대기
    client_socket, client_address = server_socket.accept()
    g.append(client_socket)

    print(f"새로운 연결: {client_address}")

    # 클라이언트를 처리하는 스레드 시작
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
