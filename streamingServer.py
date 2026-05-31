import sys
import socket
from data import movies, abCDNURLs
import time
import random

encoding = sys.argv[1] 
streamingServerIP = "127.0.0.1"

with open("config.txt", "r") as f:
  for line in f:
    line = line.strip()
    if line.startswith(encoding):
      temp = line.split("=")[1].strip()
      streamingServerPort = int(temp)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((streamingServerIP, streamingServerPort))



def toTimeFormat(seconds):
  hours = int(seconds // 3600)
  minutes = int((seconds % 3600) // 60)
  secs = int(seconds % 60)
  millis = round((seconds % 1) * 1000)
  return f"{hours:02d}:{minutes:02d}:{secs:02d}:{millis:03d}"

def toSeconds(timeString):
  hours, minutes, secs, millis = map(int, timeString.split(":"))
  return hours * 3600 + minutes * 60 + secs + millis / 1000

movieChunks = {}

#서버가 시작될 때 한 번만 실행되는 준비 작업임.
## 각 abCDN 스트리밍 서버는 자신이 보유해야 하는 encoding 등급의 영상 각각에 대하여 연속된 chunk를 저장.
for num, info in movies.items():
  duration = info["duration"]
  numChunks = info[encoding]
  chunkDuration = duration / numChunks 
  # 120/"MQ에 해당하는 chunk" 를 통해서 HQ, MQ 등의 값에 해당하는 chunk당 길이를 계산
  chunks = []
  for i in range(numChunks): #chunk 0~n-1까지 반복
    t_s = toTimeFormat(i * chunkDuration) #numChunk가 시작되는 시각
    t_N = toTimeFormat((i + 1) * chunkDuration) #numChunk가 끝나는 시각
    chunks.append((t_s, t_N)) #이렇게 for문을 통해서 모든 영화의 chunk를 미리 저장함. 
  movieChunks[num] = chunks

while True :
  requestedData, clientAddr = sock.recvfrom(256)
  print(f"현재 위치 : streamingServer - {streamingServerIP}:{streamingServerPort} 수신된 데이터: {requestedData.decode()}")
  requested = requestedData.decode()
  abCDNURL, t_N = requested.split(",")
  movieNum = abCDNURL.split("/")[-1]
  requestedChunks = movieChunks[movieNum] # (chunk 시작 시각, chunk 끝 시각) 배열
  t_N_lastView = toSeconds(t_N) #client가 마지막으로 재생한 시각 
  startIdx = len(requestedChunks) #전송 시작할 chunk번호를 저장하기 위해 선언
  for i, (t_s, t_end) in enumerate(requestedChunks): #각 chunk의 시작과 끝 시각을 확인 i :chunk의 순서 번호, t_s : 해당 chunk의 시작 시각, t_end : 해당 chunk의 끝 시각
     
    #마지막으로 재생한 시각이 해당 chunk의 시작 시각보다 작거나 같으면
    if t_N_lastView <= toSeconds(t_s):
      startIdx = i #chunk 시작 번호
      break
  
  #startIdx : 전송 시작할 chunk #, len(requestedChunks) : 해당 영화의 total chunks
  for i in range(startIdx, len(requestedChunks)): 
    t_s, t_end = requestedChunks[i]
    chunkData = f"t_s={t_s},t_end={t_end}"
    sock.sendto(chunkData.encode(), clientAddr)
    print(f"현재 위치 : {streamingServerIP}:{streamingServerPort} 전송된 chunk: {chunkData}")
    time.sleep(random.uniform(0.1, 0.7)) #delay삽입