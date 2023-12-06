# -*- coding: utf-8 -*-

import socket
import threading
import random


# 청크 업데이트 되는 리스트 검사해서 4개의 클라이언트가 청크를 다 받았다면 접속 종료하라고 메시지 보내주고 클라이언트 다 종료되면 서버 종료

def client_handler(client_socket, group, thread_num):
    global count, client_ip, client_port, client_chunks

    if count == 4:
        for i, client in enumerate(group):
            msg = "All_Connected" + "|" + client_ip[i] + "|" + str(client_port[i]) + "|" + str(i+1)
            client.send(msg.encode("utf-8"))

    print(1)

    while True:
        try:
            data = client_socket.recv(1024).decode()
            print(data)

            data_split = data.split("?")
            #Where_is?메시지
            #Update_chunk_list?메시지

            type = data_split.pop(0)

            if type == "Update_chunk_list":
                update_chunk_list = data_split.split("/")
                update_chunk_list.pop(0)

                for update_chunk in update_chunk_list:
                    chunk_list_num, chunk_list_len = update_chunk.split("|")
                    client_chunks[thread_num-1][int(chunk_list_num)] = int(chunk_list_len)
            

            elif type == "Where_is": # 원하는 청크 갖고 있는 애 랜덤으로 고르자
                need_chunk_list = data_split.split("/")
                need_chunk_list.pop(0)

                target_clients_list = []
                target_file_num_list = []
                
                for need_chunk in need_chunk_list:
                    file_num, chunk_num = need_chunk.split("|")
                    target_client = 0

                    #어떤 파일의 어떤 청크가 필요한지
                    for client in range(4):
                        if client_chunks[client][int(file_num)] >= int(chunk_num):
                            target_client = client
                            break
                    
                    #여기부터 다시 코딩
                    target_clients_list.append(target_client)
                    target_file_num_list.append(file_num)
                
                msg = ""
                for target_client, target_file_num in zip(target_clients_list, target_file_num_list):
                    msg += "/" + client_ip[target_client] + "|" + str(client_port[target_client]) + "|" + target_file_num
                
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
    
    # 클라이언트가 들어오기 전에 해도 되는건지는 모르겠지만 일단 해놓음 (각 클라이언트가 가진 청크 초기)
    client_chunks = [[[] for _ in range(4)] for _ in range(4)]


    # for i in range(4):
    #     print(client_chunks[i]) 
 
    # 각 클라이언트가 보유한 청크 목록 (계속 업데이트 되어야 함)
    count = 0
    

    while True:
        try:
            count = count + 1
            conn, addr = server_sock.accept()  # 해당 소켓을 열고 대기
            
            group.append(conn) #연결된 클라이언트의 소켓정보
            ip, port = addr
            
            client_ip.append(ip)
            
            client_port.append(port)

            thread_num = count
            
            print('Connected ' + str(addr))

            thread = threading.Thread(target=client_handler, args=(conn, group, thread_num))
            thread.start()

            
        except:
            pass


