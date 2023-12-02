import socket
import threading

# 서버 IP 주소와 포트
server_ip = '127.0.0.1'
server_port = 12345  # 사용할 포트 번호


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

def connect_to_client(target_ip, target_port):
    target_address = (target_ip, target_port)
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect(target_address)
    return target_socket

def get_file(client_socket):
    connecting_client_list = select_client(client_socket)

    for client in connecting_client_list:
        msg = "Give_file" #파일의 어느부분 달라고 하는지 정보 보내야함
        client.send(bytes(msg.encode()))

    while True:
        try:
            response = client_socket.recv(1024) #어떤 클라이언트에게 뭐가 왔는지 메시지에 있어야함
            print(response)

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


def select_client(client_socket):
    connecting_client_list = []

    result_message = connect_to_server(client_socket) # (주소)|(주소)
    print(result_message)
    clients_address = result_message.split("|") # ("127.0.0.1", 34521)

    #result_message split해서 받은 모든 클라이언트의 주소 가져옴

    for i in clients_address:
        target_ip, target_port= i[1:-1].split(",")
        connecting_client_list.append(connect_to_client(target_ip, int(target_port))) # for문 돌려서 배열에 넣기

    return connecting_client_list


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