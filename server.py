# -*- coding: utf-8 -*-

import socket
import threading
import random
import time
import math

# 스레딩 동기화를 위한 Lock 객체 생성
lock = threading.Lock()

# 청크 업데이트 되는 리스트 검사해서 4개의 클라이언트가 청크를 다 받았다면 접속 종료하라고 메시지 보내주고 클라이언트 다 종료되면 서버 종료

def client_handler(client_socket, group, thread_num):
    global count, client_ip, client_port, client_chunks, update_client_list, result_time, start

    if count == 4:
        for i, client in enumerate(group):
            msg = "All_Connected|" + client_ip[i] + "|" + str(i+1)
            client.send(msg.encode("utf-8"))
    

    while True:
        try:
            data = client_socket.recv(1024).decode()

            data_split = data.split("?")
            #Where_is?메시지
            #Update_chunk_list?메시지

            type_name = data_split.pop(0)

            # Lock을 획득하여 공유 자원에 대한 동기화 보장
            with lock:
            
                if type_name == "Update_chunk_list":
                    update_time = time.time()
                    for_time = (update_time-start) * 1000.0
                    result_time += for_time
                    print(str(thread_num) + "번 클라이언트의 파일 청크 업데이트")
                    server_file.write("{:.2f} [server] '클라이언트 {}'의 파일 청크 업데이트 \n".format(result_time, thread_num))
                    update_client_list.remove(int(thread_num))
                    update_chunk_list = data_split[0].split("/")
                    update_chunk_list.pop(0)

                    for update_chunk in update_chunk_list:
                        chunk_list_num, chunk_list_len = update_chunk.split("|")
                        client_chunks[thread_num-1][int(chunk_list_num)] = int(chunk_list_len)
                        print(chunk_list_num + "번 파일 길이 : " + chunk_list_len)
                        server_file.write("{:.2f} [server] '클라이언트 {}'의 {}번 파일 : {}/1954 \n".format(result_time, thread_num, chunk_list_num, chunk_list_len))
                    server_file.write("\n")
                    if len(update_client_list) == 0:
                        print("업데이트 완료")
                        update_client_list = [1, 2, 3, 4]
                        update_msg = "Update_Complete"
                        for c_all_send in group:
                            c_all_send.send(update_msg.encode("utf-8"))
                        #break


                elif type_name == "Where_is": # 원하는 청크 갖고 있는 애 랜덤으로 고르자
                    need_chunk_list = data_split[0].split("/")
                    need_chunk_list.pop(0)


                    target_clients_list = []
                    target_file_num_list = []
                    target_chunk_num_list = [] 
                    
                    for need_chunk in need_chunk_list:
                        file_num, chunk_num = need_chunk.split("|")
                        target_client = 0
                        target_able = []

                        #어떤 파일의 어떤 청크가 필요한지
                        #더 가까운 곳에 있는 피어 고르는 거 구현
                        for client in range(4):
                            if client_chunks[client][int(file_num)] > int(chunk_num):
                                target_able.append(client)

                        print("파일 넘버: " + file_num)
                        
                        for t in target_able:
                            if client_ip[t] == client_ip[thread_num-1]:
                                target_client = t
                                break
                        
                        if target_client == 0:
                            target_client = random.choice(target_able)
                        
                        recv_time = time.time()
                        for_time = (recv_time-update_time) * 1000.0
                        result_time += for_time
                        server_file.write("{:.2f} [server] '클라이언트 {}'(이)가 {}번 파일 요청 (선택된 클라이언트 : '{}')\n".format(result_time, str(thread_num), file_num, str(target_client+1)))
                        target_clients_list.append(target_client)
                        target_file_num_list.append(file_num)
                        target_chunk_num_list.append(chunk_num)

                        #time.sleep(0.3)

                    server_file.write("\n")
                    msg = ""
                    for target_client, target_file_num, chunk_num in zip(target_clients_list, target_file_num_list, target_chunk_num_list):
                        msg += "/" + client_ip[target_client] + "|" + str(target_client) + "|" + target_file_num + "|" + chunk_num
                    
                    client_socket.send(msg.encode("utf-8"))

        except:
            pass
    # server_sock.close()
    # server_file.write("서버 종료")
    # server_file.close()
    

if __name__ == '__main__':
    
    HOST = "0.0.0.0"  # 수신 받을 모든 IP를 의미
    PORT = 9000  # 수신받을 Port
    result_time = 0.0

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    server_sock.bind((HOST, PORT))  # 소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(4)  # 소켓 연결, 여기서 파라미터는 접속수를 의미
    
    server_file = open("server_log.txt", "w", encoding="UTF-8")    # server log 파일 생성

    group, client_ip, client_port = [], [], []
    server_file.write("서버가 {}:{} 에서 실행\n".format(HOST, PORT))
    start = time.time()
    math.factorial(100000)
    # 클라이언트가 들어오기 전에 해도 되는건지는 모르겠지만 일단 해놓음 (각 클라이언트가 가진 청크 초기)
    client_chunks = [[[] for _ in range(4)] for _ in range(4)]
    update_client_list = [1, 2, 3, 4]
 
    count = 0  # 각 클라이언트가 보유한 청크 목록 (계속 업데이트 되어야 함)    

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
            server_file.write("{:.2f} [server] '클라이언트 {}'(이)가 서버에 접속\n".format(result_time, thread_num))
            thread = threading.Thread(target=client_handler, args=(conn, group, thread_num))
            thread.start()

            
        except:
            pass
