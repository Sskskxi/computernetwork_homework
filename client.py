import socket
import threading
import time

#buffer에 저장함과 꺼냄을 동시에 진행하는 과정에서 충돌 없이 이용하기 위한 lock
lock = threading.Lock()

def toSeconds(timeString):
  hours, minutes, secs, millis = map(int, timeString.split(":"))
  return hours * 3600 + minutes * 60 + secs + millis / 1000


with open("config.txt", "r") as f:
    for line in f :
        line = line.strip()
        if line.startswith("localDNSServer"):
            temp = line.split("=")[1].strip()
            localDNSServerIP, localDNSServerPort = temp.split(":")
            localDNSServerPort = int(localDNSServerPort)
        elif line.startswith("netplusWebServer"):
            temp = line.split("=")[1].strip()
            netplusWebServerIP, netplusWebServerPort = temp.split(":")
            netplusWebServerPort = int(netplusWebServerPort)
        elif line.startswith("netplusDNSServer"):
            temp = line.split("=")[1].strip()
            netplusDNSServerIP, netplusDNSServerPort = temp.split(":")
            netplusDNSServerPort = int(netplusDNSServerPort)
        elif line.startswith("abCDNDNSServer"):
            temp = line.split("=")[1].strip()
            abCDNDNSServerIP, abCDNDNSServerPort = temp.split(":")
            abCDNDNSServerPort = int(abCDNDNSServerPort)


inputMovieNumber = input("영화 번호 입력하기 (1~9): ")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(inputMovieNumber.encode(), (netplusWebServerIP, netplusWebServerPort))
indexURL, _ = sock.recvfrom(256)
print(f"현재 위치 : client 받은 indexURL : {indexURL.decode()}")
sock.sendto(indexURL, (localDNSServerIP, localDNSServerPort))
manifest, _ = sock.recvfrom(4096)
print(f"현재 위치 : client 받은 manifest : {manifest.decode()}")
HQIPAddr, HQIPPort = manifest.decode().split(",")[0].split("=")[1].split(":")
MQIPAddr, MQIPPort = manifest.decode().split(",")[1].split("=")[1].split(":")
LQIPAddr, LQIPPort = manifest.decode().split(",")[2].split("=")[1].split(":")
#sendto에서 port#는 int type이어야 함. 
HQIPPort = int(HQIPPort)
MQIPPort = int(MQIPPort)
LQIPPort = int(LQIPPort)
sock.sendto(f"https://abCDN.net/{inputMovieNumber},00:00:00:000".encode(), (HQIPAddr, HQIPPort)) 


buffer = []
switch_buffer = []
switching = False
switch_encoding = None
BUFFER_SIZE = 12
INITIAL_BUFFER_SIZE = 4

#probe를 측정하기 위해서 변수 설정
ALPHA = 0.8   
BETA = 0.5    #상향 기준
GAMMA = 0.2   #하향 기준
K = 3         #probe 횟수
active_encoding = "HQ"

def receiveChunksToBuffer() :
    while True : 
        data, addr = sock.recvfrom(4096)
        if addr[1] == HQIPPort :
            encoding = "HQ"
        elif addr[1] == MQIPPort :
            encoding = "MQ"
        elif addr[1] == LQIPPort :
            encoding = "LQ"
        with lock:
            #화질 전환 시 버퍼 관리
            if switching and encoding == switch_encoding and len(switch_buffer) < BUFFER_SIZE:
                switch_buffer.append((data, encoding))
                print(f"switch_buffer에 추가: {data.decode()}")
            #화질 전환을 하지 않은 경우
            elif not switching and encoding == active_encoding and len(buffer) < BUFFER_SIZE:
                buffer.append((data, encoding))
                print(f"buffer에 추가: {data.decode()} (현재 {len(buffer)}/{BUFFER_SIZE})")
            
            


def processBuffer() :
    global active_encoding, switching, switch_encoding
    probe = []
    R_buffer = 0.0
    current_encoding = "HQ"
    started = False
    just_switched = False  # 같은 iteration 내 연속 전환 방지
    switch_t_N = "00:00:00:000"  # 전환 요청 시 보낸 t_N 기록

    while True :
        chunk = None
        with lock:
            if (( not started and len(buffer) >= INITIAL_BUFFER_SIZE) or (started and len(buffer) > 0)):
                  chunk, chunk_encoding = buffer.pop(0)
                  started = True

        if chunk :
            # chunk의 양식은 "t_s=00:01:23:029,t_end=00:02:46:058"
            chunk = chunk.decode()
            chunkTimes = chunk.split(",")
            t_s = chunkTimes[0].split("=")[1]
            t_end = chunkTimes[1].split("=")[1]
            chunkPlayTime = toSeconds(t_end) - toSeconds(t_s)
            time.sleep(chunkPlayTime * 0.5) #chunk 재생 시간만큼 잠깐 멈추도록 설정 * 0.5
            with lock:
                buf_ratio = len(buffer) / BUFFER_SIZE  # sleep 후 측정 → 실제 버퍼 상태 반영
            print(f"재생 중 : {t_s} ~ {t_end} 현재 화질 : {chunk_encoding}, 재생 중인 버퍼 비율 : {len(buffer)}/{BUFFER_SIZE}")

            # case(i) / case(ii): chunk 재생 완료 후 switch_buffer 확인
            if switching:
                with lock:
                    if switch_buffer:
                        chunk_idx = None
                        min_t_s = float('inf')
                        switch_t_N_sec = toSeconds(switch_t_N)
                        for i, (d, _) in enumerate(switch_buffer):
                            temp_t_s_str = d.decode().split(",")[0].split("=")[1]
                            temp_t_s_sec = toSeconds(temp_t_s_str)
                            if (temp_t_s_sec >= toSeconds(t_end) and
                                    (temp_t_s_sec - switch_t_N_sec) <= 30 and
                                    temp_t_s_sec < min_t_s):
                                min_t_s = temp_t_s_sec
                                chunk_idx = i
                        if chunk_idx is not None:
                            # term(영상 공백) 계산 및 시뮬레이션
                            first_t_s = switch_buffer[chunk_idx][0].decode().split(",")[0].split("=")[1]
                            gap = toSeconds(first_t_s) - toSeconds(t_end)
                            if gap > 0:
                                print(f"영상 공백(term): {t_end} ~ {first_t_s} ({gap:.3f}초)")
                                time.sleep(gap * 0.5)
                            buffer.clear()
                            for item in switch_buffer[chunk_idx:]:
                                buffer.append(item)
                            switch_buffer.clear()
                            current_encoding = switch_encoding
                            switching = False
                            just_switched = True
                            probe.clear()
                            print(f"화질 전환 완료: → {current_encoding}, k={K}, β={BETA}, γ={GAMMA}, R_buffer={R_buffer:.4f}")

            probe.append(buf_ratio)
            if len(probe) >= K :
                avg = sum(probe) / K
                R_buffer = ALPHA * R_buffer + ( 1 - ALPHA ) * avg
                print(f"R_buffer 업데이트: {R_buffer}")

                if R_buffer >= BETA :
                    print(f"R_buffer가 BETA({BETA}) 이상입니다.")
                    if current_encoding == "MQ" and not switching and not just_switched:
                        print(f"encoding 화질을 MQ -> HQ로 전환 요청, k={K}, β={BETA}, γ={GAMMA}, R_buffer={R_buffer:.4f}")
                        switch_encoding = "HQ"
                        active_encoding = "HQ"
                        switching = True
                        switch_t_N = t_end
                        sock.sendto(f"https://abCDN.net/{inputMovieNumber},{t_end}".encode(), (HQIPAddr, HQIPPort))
                    elif current_encoding == "LQ" and not switching and not just_switched:
                        print(f"encoding 화질을 LQ -> MQ로 전환 요청, k={K}, β={BETA}, γ={GAMMA}, R_buffer={R_buffer:.4f}")
                        switch_encoding = "MQ"
                        active_encoding = "MQ"
                        switching = True
                        switch_t_N = t_end
                        sock.sendto(f"https://abCDN.net/{inputMovieNumber},{t_end}".encode(), (MQIPAddr, MQIPPort))
                elif R_buffer < GAMMA :
                    print(f"R_buffer가 GAMMA({GAMMA}) 미만입니다.")
                    if current_encoding == "HQ" and not switching and not just_switched:
                        print(f"encoding 화질을 HQ -> MQ로 전환 요청, k={K}, β={BETA}, γ={GAMMA}, R_buffer={R_buffer:.4f}")
                        switch_encoding = "MQ"
                        active_encoding = "MQ"
                        switching = True
                        switch_t_N = t_end
                        sock.sendto(f"https://abCDN.net/{inputMovieNumber},{t_end}".encode(), (MQIPAddr, MQIPPort))
                    elif current_encoding == "MQ" and not switching and not just_switched:
                        print(f"encoding 화질을 MQ -> LQ로 전환 요청, k={K}, β={BETA}, γ={GAMMA}, R_buffer={R_buffer:.4f}")
                        switch_encoding = "LQ"
                        active_encoding = "LQ"
                        switching = True
                        switch_t_N = t_end
                        sock.sendto(f"https://abCDN.net/{inputMovieNumber},{t_end}".encode(), (LQIPAddr, LQIPPort))
                probe.pop(0)
            just_switched = False  # 다음 iteration부터 전환 허용



        else:
            continue



#동시에 실행되는 코드를 작성하기 위해 스레드 활성화 
t = threading.Thread(target = receiveChunksToBuffer)
t.daemon = True 
t.start()
processBuffer()

