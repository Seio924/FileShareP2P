import socket
import threading

# 서버 IP 주소와 포트
server_ip = '127.0.0.1'
server_port = 12345  # 사용할 포트 번호
all_address = []

def handle_server_connection(client_socket):
    try:
        msg = "클라이언트에서 서버로의 메시지입니다."
        client_socket.send(bytes(msg.encode()))

        response = client_socket.recv(1024)
        print(f"서버로부터의 응답: {response.decode()}")

        return response.decode()

    except Exception as e:
        print(f"통신 에러: {e}")
        return None


def connect_to_server(client_socket):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 서버에 연결
        client_socket.connect((server_ip, server_port))
        print(f"서버에 연결되었습니다. 서버 IP: {server_ip}, 포트: {server_port}")

        return handle_server_connection(client_socket)

    except Exception as e:
        print(f"연결 에러: {e}")
        return None
    
def select_client(client_socket):
    global all_address
    connecting_client_list = []

    result_message = connect_to_server(client_socket) # (주소)|(주소)

    clients_address = result_message.split("|") # ("127.0.0.1", 34521)
    all_address.append(clients_address)

    #result_message split해서 받은 모든 클라이언트의 주소 가져옴
    if len(all_address) == 4:
        for target in all_address:
            for i in target:
                target_ip, target_port= i[1:-1].split(",")
                response = connect_to_client(target_ip, int(target_port))
                connecting_client_list.append(response) # for문 돌려서 배열에 넣기
        
    return connecting_client_list

def connect_to_client(target_ip, target_port):
    try:
        target_ip = target_ip[1:-1]
        target_address = (target_ip, target_port)
        print(target_address)
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect(target_address) # 여기서 대상 컴퓨터 거부 오류
        return target_socket
    except Exception as e:
        print(f"Error in connect_to_client: {e}")
        return None

def get_file(client_socket):
    connecting_client_list = select_client(client_socket)

    for client in connecting_client_list:
        msg = "Give_file" #파일의 어느부분 달라고 하는지 정보 보내야함
        client.send(bytes(msg.encode()))

    if connecting_client_list:  # connecting_client_list가 비어있지 않은 경우에만 while 루프 실행
        client = connecting_client_list[0]  # 첫 번째 클라이언트를 사용

        while True:
            try:
                response = client.recv(1024) #어떤 클라이언트에게 뭐가 왔는지 메시지에 있어야함
                #connecting_client_list와 비교해서 모든 클라이언트에게 받았으면 종료
                break
            except ConnectionResetError:
                break
    
    

def give_file(conn, client_socket):
    while True:
        try:
            response = client_socket.recv(1024)

            print(response)

            msg = "here is the file"
            conn.send(bytes(msg.encode()))

        except ConnectionResetError:
            break


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    thread1 = threading.Thread(target=get_file, args=(client_socket,))
    thread1.start()

    while True:
        try:
            count = count + 1
            conn, addr = client_socket.accept()  # 해당 소켓을 열고 대기
            
            thread2 = threading.Thread(target=give_file, args=(conn, client_socket))
            
            thread2.start()

            
        except:
            exit(0)