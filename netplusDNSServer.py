import socket

with open("config.txt", "r") as f:
  for line in f :
      line = line.strip()
      if line.startswith("netplusDNSServer"):
          temp = line.split("=")[1].strip()
          netplusDNSServerIP, netplusDNSServerPort = temp.split(":")
          netplusDNSServerPort = int(netplusDNSServerPort)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((netplusDNSServerIP, netplusDNSServerPort))

from data import movieIndex, abCDNURLs

##indexURL을 기반으로 abCDN URL 반환하기 위함
reverseIndex = {url : num for num, url in movieIndex.items()}

while True : 
  localDNSdata, localDNSaddr = sock.recvfrom(256)
  localDNSUrl = localDNSdata.decode()
  print(f"현재 위치 : {netplusDNSServerIP} 받은 주체 : {localDNSaddr} 받은 localDNS URL : {localDNSUrl}")
  movieNum = reverseIndex[localDNSUrl]
  abCDNUrl = abCDNURLs[movieNum]
  sock.sendto(abCDNUrl.encode(), localDNSaddr)
  print(f"현재 위치 : {netplusDNSServerIP} 보낸 주체 : {localDNSaddr} 보낸 abCDN URL : {abCDNUrl}")
   