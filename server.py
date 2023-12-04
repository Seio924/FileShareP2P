# -*- coding: utf-8 -*-

import socket
import threading
import random


def client_handler(client_socket, group):
    global count, client_ip, client_port

    client_id = count

    c_list = [1, 2, 3, 4]

    while True:
        if count == 4:
            for client in group:
                msg = "All_Connected" + "|" + client_ip[client_ip-1] + "|" + str(client_port[client_ip-1])
                client.send(msg.encode("utf-8"))
            break
    
    while True:
        try:
            data = conn.recv(1024).decode()
            
            if data == "Where_is":
                target_num = random.choice(c_list)
                if target_num != client_id:
                    break
                print(str(target_num) + "번 클라이언트 선택")

                msg = client_ip[target_num-1] + "|" + str(client_port[target_num-1])
                client_socket.send(msg.encode("utf-8"))
                
        except:
            pass

    

if __name__ == '__main__':
    
    HOST = "0.0.0.0"  # 수신 받을 모든 IP를 의미
    PORT = 9000  # 수신받을 Port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    server_sock.bind((HOST, PORT))  # 소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(5)  # 소켓 연결, 여기서 파라미터는 접속수를 의미

    group, client_ip, client_port = [], [], []
    count = 0
    

    while True:
        try:
            count = count + 1
            conn, addr = server_sock.accept()  # 해당 소켓을 열고 대기
            
            group.append(conn) #연결된 클라이언트의 소켓정보
            ip, port = addr
            
            client_ip.append(ip)
            
            client_port.append(port)
            
            print('Connected ' + str(addr))

            thread = threading.Thread(target=client_handler, args=(conn, group))
            thread.start()

            
        except:
            pass