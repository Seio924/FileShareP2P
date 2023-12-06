# -*- coding: utf-8 -*-

import socket
import threading
import time
import os
import hashlib

# 원본 파일 해시값
def file_calculate_md5(file_path):
    # 파일이 존재하는지 확인
    if not os.path.exists(file_path):
        print("파일이 존재하지 않습니다.")
        return None

    # 파일이 존재하면 MD5 해시값 계산
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()

#파일을 청크 단위로 나눠 리스트로 만들기 (청크 인덱스, 청크내용)
def read_file_in_chunks(file_path, chunk_size=256 * 1024):
    with open(file_path, 'rb') as file:
        index = 0
        chunks_list = []
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            chunks_list.append((index, chunk))
            index += 1
        return chunks_list


# 문자열 또는 바이트열을 MD5 해시로 변환하는 함수 (청크를 합쳐서 해시값 확인)
def calculate_md5(data):
    if isinstance(data, str):
        data = data.encode('utf-8')  # 문자열을 바이트열로 변환

    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.hexdigest()


def receive_messages(peer_connection, thread_num): # 여기서 해당 클라이언트에게 청크 줘
    global chunks_list
    try:
        data = peer_connection.recv(1024).decode()
        want_client, want_index_recv = data.split("|") # 내 것의 청크를 원하는 클라이언트, 원하는 청크인덱스
        print(data)
    except Exception as e:
        print(f"Error receiving data: {e}")

    # 파일 보내주기
    # 몇번 클라이언트의 청크인지 보내야함. 내가 몇번인지 말고 (수정)
    print(thread_num + "번이 파일을 보냈습니다.")
    msg = thread_num + chunks_list[int(want_index_recv)] # 친구가 원하는 청크 보내준다.
    peer_connection.send(msg.encode("utf-8"))
    
    

def peer_handler(client_socket, thread_num):
    global update_chunks_list, original_file_md5
    peer_connecting_sock = []

    while True:
        print(1)
        update_complete = client_socket.recv(1024).decode()
        print(update_complete)
        
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
            i = 0
            for chunks_list in update_chunks_list:
                result_content = b''.join(chunk for index, chunk in chunks_list)
                client_hash = calculate_md5(result_content)
                if client_hash == original_file_md5[i]:
                    i += 1
            if i != 4:
                print("해시값 오류")
            break

        client_socket.send(msg.encode("utf-8")) #서버랑 소통

        # 연결할 클라이언트 ip랑 포트번호 받기
        data = client_socket.recv(1024).decode()
        print(data)

        target_client_list = data.split("/")

        target_client_list.pop(0)

        for peer_info in target_client_list:
            target_ip, target_port, want_index_recv = peer_info.split("|")
            # 소켓 생성
            peer_connecting_sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

            time.sleep(0.03)
            # 다른 클라이언트랑 연결
            peer_connecting_sock[-1].connect((target_ip, int(target_port)))

            peer_msg = thread_num + "|" + want_index_recv # (thread_num)번이 (want_index_recv)번 청크를 요청했습니다."
            peer_connecting_sock[-1].send(peer_msg.encode("utf-8")) # 다른 피어랑 소통

        for i in range(len(target_client_list)):

            # 다른 클라이언트에게 파일 받기
            # 여기도 for문으로 데이터 받고 for문 안에서 파일 업데이트 실시
            peer_data = peer_connecting_sock[i].recv(1024).decode() # 파일 청크
            send_client = peer_data[0] # 청크를 보낸 친구

            peer_data = peer_data[1:] # 튜플 모양새 문자열만 추출
            peer_chunk = peer_data.split(",")[1]

            # 여기서가 문제 왜냐면 (1300, djf;lfj;jfdjfkajfdjaf;jdk) 이런식으로 올거야.
            # 해당 청크리스트의 클라이언트 인덱스에 차례대로 청크값만 저장
            # 예를 들어, 클라이언트1의 128번째 청크 > update_chunks_list[0][127]
            
            update_chunks_list[int(send_client)-1].append(peer_chunk)

            time.sleep(0.01)

            #연결했던 클라이언트와 연결 끊기
            peer_connecting_sock[i].close()
            print("연결 끊음")
            time.sleep(0.01)
        peer_connecting_sock = []

        msg = "Update_chunk_list?"

        for i in range(4):
            msg += "/" + str(i) + "|" + str(len(update_chunks_list[i]))

        client_socket.send(msg.encode("utf-8")) #서버랑 소통

if __name__ == "__main__":
    
    # 서버 포트 설정
    server_host = "localhost"
    server_port = 9000

    client_port = [11111, 22222, 33333, 44444]

    # 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 서버에 연결
    client_socket.connect((server_host, server_port))

    data = client_socket.recv(1024).decode()
    print(data)

    #서버에게 내 아이피 주소와 포트번호를 받음
    type, my_ip, thread_num = data.split("|")

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

    print(len(chunks_list)) #1954개? 나옴

    update_chunks_list = [[], [], [], []] #내가 가진 다른 클라이언트의 청크

    update_chunks_list[int(thread_num)-1] = chunks_list

    #print(len(update_chunks_list[int(thread_num)-1]))
    msg = "Update_chunk_list?"
    print(msg)
    for i in range(4):
        msg += "/" + str(i) + "|" + str(len(update_chunks_list[i]))

    client_socket.send(msg.encode("utf-8")) #서버랑 소통

    #아이피 주소와 포트번호로 다른 클라이언트가 들어오는걸 대기
    peer_sock.bind((my_ip, client_port[int(thread_num)-1]))
    peer_sock.listen(4)


    thread_main = threading.Thread(target=peer_handler, args=(client_socket, thread_num))
    thread_main.start()

    while True:
        # Accept connection from a client
        peer_connection, peer_address = peer_sock.accept()

        # 스레드를 생성하여 receive_messages 함수 실행
        thread = threading.Thread(target=receive_messages, args=(peer_connection, thread_num))
        thread.start()
        