import socket
import threading

# 서버 주소 및 포트
server_address = ('localhost', 5555)

def send_message():
    while True:
        print(1)
        # 사용자로부터 메시지 입력
        message = input("메시지를 입력하세요: ")
        recipient_address = input("전송할 클라이언트 주소를 입력하세요 (예: 127.0.0.1:5555): ")
        message += f",{recipient_address}"

        # 서버에 메시지 전송
        client_socket.sendall(message.encode())

def receive_messages():
    while True:
        print(2)
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            print(f"[클라이언트] 서버로부터 수신한 메시지: {data.decode()}")

        except Exception as e:
            print(f"[클라이언트] 에러 발생: {e}")
            break

# 서버에 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)
print("[클라이언트] 서버에 연결")

# 메시지 전송을 위한 쓰레드 생성
send_thread = threading.Thread(target=send_message)
send_thread.start()

# 서버로부터 메시지 수신을 위한 쓰레드 생성
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# 쓰레드 종료 대기
send_thread.join()
receive_thread.join()

# 연결 종료
print("[클라이언트] 연결 종료")
client_socket.close()
