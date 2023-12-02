import socket
import threading

def handle_client(client_socket, address):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            message, recipient_address = parse_message(data)
            print(f"[서버] {address}로부터 수신한 메시지: {message}, 받는 클라이언트 주소: {recipient_address}")
            print(3)
            # 특정 클라이언트에게 메시지 전송
            send_to_client(client_socket, message, recipient_address)
            print(4)
        except Exception as e:
            print(f"[서버] 에러 발생: {e}")
            continue  # 예외가 발생해도 계속해서 다음 클라이언트에게 메시지 전송을 시도

    print(f"[서버] {address}와의 연결 종료")
    client_socket.close()

def send_to_client(client_socket, message, recipient_address):
    print(5)
    print(type(recipient_address))
    recipient_ip, recipient_port = recipient_address.split(":")[0], recipient_address.split(":")[1]
    recipient_address = (recipient_ip, int(recipient_port))
    print(recipient_address)
    for client, client_address in clients:
        print(6)
        print(client_address)
        if client_address == recipient_address:
            try:
                print(7)
                client.sendall(message.encode())
            except Exception as e:
                print(f"[서버] 에러 발생: {e}")

def parse_message(data):
    # 메시지와 받는 클라이언트 주소를 추출
    message, recipient_address = data.decode().split(",", 1)
    return message, recipient_address

# 클라이언트 정보를 저장할 리스트
clients = []

# 서버 소켓 설정
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen()

print("[서버] 서버 시작")

while True:
    try:
        client_socket, address = server.accept()
        print(f"[서버] {address}와의 연결 수락")

        # 쓰레드 생성하여 클라이언트 핸들링
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

        # 클라이언트 정보 저장
        clients.append((client_socket, address))

    except Exception as e:
        print(f"[서버] 에러 발생: {e}")
