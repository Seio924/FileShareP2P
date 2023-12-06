import random
import os

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

file_path = os.path.abspath('.\\file\\A.file')
chunks_list = read_file_in_chunks(file_path, chunk_size=256 * 1024)

# 랜덤 청크 하나 출력해보기
ran = random.randint(0, len(chunks_list) - 1)
data = chunks_list[ran][1]

print(data)

print()

# 바이트 데이터를 문자열로 변환하고 다시 바이트로 변환
data_s = str(data[2:])

byte_data_s = bytes(data_s, 'utf-8')  # 인코딩을 지정하여 바이트로 변환

print(byte_data_s)

# 청크 단위로 분리한 것 다시 파일로 만들기
result_content = b''.join(chunk for index, chunk in chunks_list)
