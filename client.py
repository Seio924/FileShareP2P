# -*- coding: utf-8 -*-

import socket
import threading
import time
import os
import hashlib

# 스레딩 동기화를 위한 Lock 객체 생성
lock = threading.Lock()

# 원본 파일 해시값
def file_calculate_md5(file_path):
    # 파일이 존재하는지 확인
    if not os.path.exists(file_path):
        print("파일이 존재하지 않습니다.")
        return None

    # 파일이 존재하면 MD5 해시값 계산
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            md5_hash.update(chunk)

    return md5_hash.hexdigest()

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
    global chunks_list, update_chunks_list

    data = peer_connection.recv(256 * 1024).decode('utf-8')
    want_file_recv, want_chunk_recv = data.split("|")
    
    # 파일 보내주기
    # 몇번 클라이언트의 청크인지 보내야함. 내가 몇번인지 말고 (수정)
    
    send_chunk = update_chunks_list[int(want_file_recv)][int(want_chunk_recv)]

    peer_connection.sendall(want_file_recv.encode('utf-8'))
    peer_connection.sendall(send_chunk)
    
    

def peer_handler(client_socket):
    global update_chunks_list, original_file_md5, client_port
    peer_connecting_sock = []
    print(1)

    while True:
        update_msg = client_socket.recv(1024).decode()
        with lock:
            if update_msg == "Update_Complete":            
                #파일 나누고 자신한테 없는 파일들 정보 서버에게 물어보기
                
                msg = "Where_is?"
                print(2)
                file_compelete = 0
                # 4개의 청크 리스트 중에서 다 안채워진 리스트
                for i in range(4): 
                    need_chunk = len(update_chunks_list[i])
                    if need_chunk < 1954:
                        msg += "/" + str(i) + "|" + str(need_chunk)
                    else:
                        file_compelete += 1
                print(3)
                if file_compelete == 4:
                    i = 0
                    for chunks_list in update_chunks_list:
                        print(len(chunks_list))
                        result_content = b''.join(chunk for chunk in chunks_list)
                        client_hash = calculate_md5(result_content)
                        print("야야야야야야야야야야")
                        if client_hash == original_file_md5[i]:
                            print("client_hash : " + client_hash)
                            print("original : " + original_file_md5[i])
                            i += 1
                    if i != 4:
                        print("해시값 오류")
                    break
                
                print(4)
                print(msg)
                client_socket.sendall(msg.encode("utf-8")) #서버랑 소통
                print(5)
                # 연결할 클라이언트 ip랑 포트번호 받기
                data = client_socket.recv(1024).decode()
                print(6)

                target_client_list = data.split("/")

                target_client_list.pop(0)
                print(7)

                for peer_info in target_client_list:
                    print(8)
                    target_ip, target_port, want_file_recv, want_chunk_recv = peer_info.split("|")
                    # 소켓 생성
                    print(target_port)
                    peer_connecting_sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

                    #time.sleep(0.03)
                    # 다른 클라이언트랑 연결
                    peer_connecting_sock[-1].connect((target_ip, client_port[int(target_port)]))
                    print(9)
                    peer_msg = want_file_recv + "|" + want_chunk_recv 
                    #client_file.write("{} [client {}] {} 번 파일의 청크를 요청했습니다.\n".format(system_clock_formating, want_file_recv, want_chunk_recv))
                    peer_connecting_sock[-1].sendall(peer_msg.encode("utf-8")) # 다른 피어랑 소통
                
                print(10)
                for i in range(len(target_client_list)):

                    # 다른 클라이언트에게 파일 받기
                    # 여기도 for문으로 데이터 받고 for문 안에서 파일 업데이트 실시
                    print(11)
                    peer_file_num = peer_connecting_sock[i].recv(1).decode('utf-8') # 쓰레드 번호 청크
                    print(12)
                    peer_data = peer_connecting_sock[i].recv(256*1024) # 쓰레드 번호 청크



                    # 여기서 (1300, djf;lfj;jfdjfkajfdjaf;jdk) 이런식으로 옴
                    # 해당 청크리스트의 클라이언트 인덱스에 차례대로 청크값만 저장
                    # 예를 들어, 클라이언트1의 128번째 청크 > update_chunks_list[0][127]
                    print(13)
                    print(peer_file_num + "파일 번호")
                    update_chunks_list[int(peer_file_num)].append(peer_data)

                    #time.sleep(0.02)
                    print(14)
                    #연결했던 클라이언트와 연결 끊기
                    peer_connecting_sock[i].close()
                    print(15)
                    print("연결 끊음")
                    #time.sleep(0.01)
                peer_connecting_sock = []
                print(16)

                msg = "Update_chunk_list?"

                for i in range(4):
                    msg += "/" + str(i) + "|" + str(len(update_chunks_list[i]))
                    print(str(i) + " 길이 : " + str(len(update_chunks_list[i])))
                print(17)
                client_socket.sendall(msg.encode("utf-8")) #서버랑 소통

if __name__ == "__main__":
    
    # 서버 포트 설정
    server_host = "localhost"
    server_port = 2222

    client_port = [11111, 22222, 33333, 44444]

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server_file = open("server_log.txt", "w", encoding="UTF-8")

    # 서버에 연결
    client_socket.connect((server_host, server_port))

    data = client_socket.recv(1024).decode()
    
    #서버에게 내 아이피 주소와 포트번호를 받음
    type_name, my_ip, thread_num = data.split("|")

    #file_name = "client" + thread_num + "_log.txt"     # client log 파일 생성
    #client_file = open(file_name, "w", encoding="UTF-8")
    #client_file.write("{} [client {}] 서버에 연결되었습니다.\n".format(system_clock_formating, thread_num))

    
    #파일 불러와서 청크 단위로 쪼개서 리스트에 저장
    file_name = chr(int(thread_num) + 64)
    file_path = os.path.abspath(f'.\\file\\{file_name}.file')

    # 모든 파일의 md5 값 저장해놓음
    original_file_md5 = []
    for i in range(4):
        original_file_name = chr(i + 65)
        original_file_path = os.path.abspath(f'.\\file\\{file_name}.file')
        original_file_md5.append(file_calculate_md5(file_path)) # 원본 파일의 md5 값

    chunks_list = read_file_in_chunks(file_path, chunk_size=256 * 1024)
    #client_file.write("{} [client {}] 청크를 제공합니다.\n")
    #client_file.write()
    int(len(chunks_list)) #1954개? 나옴

    update_chunks_list = [[], [], [], []] #내가 가진 다른 클라이언트의 청크

    update_chunks_list[int(thread_num)-1] = chunks_list #타입은 바이트

    #print(len(update_chunks_list[int(thread_num)-1]))
    msg = "Update_chunk_list?"
    for i in range(4):
        msg += "/" + str(i) + "|" + str(len(update_chunks_list[i]))

    client_socket.send(msg.encode("utf-8")) #서버랑 소통

    #아이피 주소와 포트번호로 다른 클라이언트가 들어오는걸 대기

    peer_sock.bind(('localhost', client_port[int(thread_num)-1]))
    peer_sock.listen(4)


    thread_main = threading.Thread(target=peer_handler, args=(client_socket,))
    thread_main.start()

    while True:
        # Accept connection from a client
        peer_connection, peer_address = peer_sock.accept()

        # 스레드를 생성하여 receive_messages 함수 실행
        thread = threading.Thread(target=receive_messages, args=(peer_connection,))
        thread.start()
        