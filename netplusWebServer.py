#netplusWebServer에서 해야되는 것
## 1. 클라이언트 요청 수신 
## 2. 수신 내용 출력
## 3. 인덱스 URL 응답

import socket 

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



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((netplusWebServerIP, netplusWebServerPort))

from data import movieIndex

while True:
  clientData, ClientAddr = sock.recvfrom(256)
  movieId = clientData.decode()
  print(f"현재 위치 : {netplusWebServerIP} 받은 주체 : {ClientAddr} 받은 영화 ID : {movieId}")
  indexURL = movieIndex[movieId]
  sock.sendto(indexURL.encode(), ClientAddr)