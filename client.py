# -*- coding: utf-8 -*-

import socket
import threading
import time
import os
import hashlib


#파일을 청크 단위로 나눠 리스트로 만들기 (청크 인덱스, 청크내용)
def read_file_in_chunks(file_path, chunk_size=256 * 1024):
    with open(file_path, 'rb') as file:
        chunks_list = []
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            chunks_list.append(chunk)
        return chunks_list


# 문자열 또는 바이트열을 MD5 해시로 변환하는 함수 (청크를 합쳐서 해시값 확인)
def calculate_md5(data):
    if isinstance(data, str):
        data = data.encode('utf-8')  # 문자열을 바이트열로 변환

    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.hexdigest()


def receive_messages(peer_connection): # 여기서 해당 클라이언트에게 청크 줘
    global chunks_list, update_chunks_list, result_time

    data = peer_connection.recv(256 * 1024).decode('utf-8')
    want_file_recv, want_chunk_recv = data.split("|")
    print(3)
    # 파일 보내주기
    # 클라이언트가 가지고 있는 청크 파일의 해당 경로를 알려줌
    # 예를 들어, 클라이언트1이 가지고 있는 3번 파일의 청크는 C파일의 청크 값임을 알려주는 것임
    start = time.time()

    send_chunk = update_chunks_list[int(want_file_recv)][int(want_chunk_recv)]
    peer_connection.sendall(want_file_recv.encode('utf-8'))
    peer_connection.sendall(send_chunk)
    recv_time = time.time()
    for_time = (recv_time-start) * 1000.0
    result_time += for_time
    client_file.write("{:.2f} [client {}] {}번 째 청크 전달\n".format(result_time, thread_num, want_chunk_recv))
    
    

def peer_handler(client_socket):
    global update_chunks_list, original_file_md5, client_port, thread_num, result_time
    peer_connecting_sock = []

    while True:
        update_msg = client_socket.recv(1024).decode()

        if update_msg == "Update_Complete":            
            #파일 나누고 자신한테 없는 파일들 정보 서버에게 물어보기
            
            msg = "Where_is?"
            file_compelete = 0
            # 4개의 청크 리스트 중에서 다 안채워진 리스트
            for i in range(4): 
                need_chunk = len(update_chunks_list[i])
                if need_chunk < 1954:
                    msg += "/" + str(i) + "|" + str(need_chunk)
                else:
                    file_compelete += 1

            if file_compelete == 4:
                print("업데이트 완료")
                i = 0
                client_file.write("소요시간 : {:.2f} msec".format(result_time))
                #client_socket.send(str(result_time).encode("utf-8"))
                for chunks_list in update_chunks_list:
                    result_content = b''.join(chunk for chunk in chunks_list)
                    client_hash = calculate_md5(result_content)
                    chunks_list[i] = client_hash
                    print(chunks_list[i])
                    i += 1
                if i != 4:
                    print("해시값 오류")
                break
            
            client_socket.sendall(msg.encode("utf-8")) #서버랑 소통
    
            # 연결할 클라이언트 ip랑 포트번호 받기
            data = client_socket.recv(1024).decode()

            target_client_list = data.split("/")

            target_client_list.pop(0)

            for peer_info in target_client_list:
                target_ip, target_port, want_file_recv, want_chunk_recv = peer_info.split("|")
             
                # 소켓 생성
                peer_connecting_sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
                
                make_time = time.time()

                # 다른 클라이언트랑 연결
                peer_connecting_sock[-1].connect((target_ip, client_port[int(target_port)]))
                peer_msg = want_file_recv + "|" + want_chunk_recv
                time.sleep(0.01)
                peer_connecting_sock[-1].sendall(peer_msg.encode("utf-8")) # 다른 피어랑 소통

                # time time
                send_time = time.time()
                for_time = (send_time-make_time) * 1000.0
                result_time += for_time
                client_file.write("{:.2f} [client {}] {}번 파일의 {}번 째 청크 요청.\n".format(result_time, thread_num, want_file_recv, want_chunk_recv))
                
            client_file.write("\n")

            for i in range(len(target_client_list)):

                # 다른 클라이언트에게 파일 받기
                # 여기도 for문으로 데이터 받고 for문 안에서 파일 업데이트 실시
                peer_file_num = peer_connecting_sock[i].recv(1).decode('utf-8') # 쓰레드 번호 청크
                peer_data = peer_connecting_sock[i].recv(256*1024) # 쓰레드 번호 청크

                # 여기서 (1300, djf;lfj;jfdjfkajfdjaf;jdk) 이런식으로 옴
                # 해당 청크리스트의 클라이언트 인덱스에 차례대로 청크값만 저장
                # 예를 들어, 클라이언트1의 128번째 청크 > update_chunks_list[0][127]
                update_chunks_list[int(peer_file_num)].append(peer_data)

                # time time
                update_time = time.time()
                for_time = (update_time-send_time) * 1000.0
                result_time += for_time

                client_file.write("{:.2f} [client {}] 청크 업데이트\n".format(result_time, thread_num))

                #연결했던 클라이언트와 연결 끊기
                peer_connecting_sock[i].close()

                print("청크 하나 업데이트")
            peer_connecting_sock = []
            
            msg = "Update_chunk_list?"

            for i in range(4):
                msg += "/" + str(i) + "|" + str(len(update_chunks_list[i]))
                print(str(i) + " 길이 : " + str(len(update_chunks_list[i])))
                client_file.write("{:.2f} [client {}] {} 번 파일 : {}/1954 \n".format(result_time, thread_num, str(i), str(len(update_chunks_list[i]))))
            client_file.write("\n")
            client_socket.sendall(msg.encode("utf-8")) #서버랑 소통

    
    

if __name__ == "__main__":
    
    # 서버 포트 설정
    server_host = "localhost"
    server_port = 9000

    client_port = [11111, 22222, 33333, 44444]

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # time time
    result_time = 0.0
    
    # 서버에 연결
    client_socket.connect((server_host, server_port))

    data = client_socket.recv(1024).decode()
    
    #서버에게 내 아이피 주소와 포트번호를 받음
    type_name, my_ip, thread_num = data.split("|")

    file_name = "client" + thread_num + "_log.txt"     # client log 파일 생성
    client_file = open(file_name, "w", encoding="UTF-8")
    client_file.write("{:.2f} [client {}] 서버 연결 완료\n".format(result_time, thread_num))

    
    #파일 불러와서 청크 단위로 쪼개서 리스트에 저장
    file_name = chr(int(thread_num) + 64)
    file_path = os.path.abspath(f'.\\file\\{file_name}.file')

    chunks_list = read_file_in_chunks(file_path, chunk_size=256 * 1024)
    client_file.write("{:.2f} [client {}] 청크를 제공합니다.\n".format(result_time, thread_num))

    update_chunks_list = [[], [], [], []] #내가 가진 다른 클라이언트 청크

    update_chunks_list[int(thread_num)-1] = chunks_list #타입은 바이트
    print(0)

    msg = "Update_chunk_list?"
    for i in range(4):
        msg += "/" + str(i) + "|" + str(len(update_chunks_list[i]))

    client_socket.send(msg.encode("utf-8")) #서버랑 소통
    print(1)
    #아이피 주소와 포트번호로 다른 클라이언트가 들어오는걸 대기

    peer_sock.bind((my_ip, client_port[int(thread_num)-1]))
    peer_sock.listen(4)


    thread_main = threading.Thread(target=peer_handler, args=(client_socket,))
    thread_main.start()
    print(2)
    while True:
        # Accept connection from a client
        peer_connection, peer_address = peer_sock.accept()

        # 스레드를 생성하여 receive_messages 함수 실행
        thread = threading.Thread(target=receive_messages, args=(peer_connection,))
        thread.start()
        