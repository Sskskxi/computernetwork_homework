with open("config.txt", "r") as f:
  for line in f :
    line = line.strip()
    if line.startswith("abCDNDNSServer"):
      temp = line.split("=")[1].strip()
      abCDNDNSServerIP, abCDNDNSServerPort = temp.split(":")
      abCDNDNSServerPort = int(abCDNDNSServerPort)

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((abCDNDNSServerIP, abCDNDNSServerPort))

from data import abCDNURLs

while True :
  requestedURL, localDNSAddr = sock.recvfrom(256)
  print(f"현재 위치 : {abCDNDNSServerIP} 받은 주체 : {localDNSAddr} 받은 requestedURL : {requestedURL.decode()}")
  if (requestedURL.decode() in abCDNURLs.values()):
    manifest = "HQ=127.0.0.1:9111,MQ=127.0.0.1:9222,LQ=127.0.0.1:9333"
    sock.sendto(manifest.encode(), localDNSAddr)
    print(f"현재 위치 : {abCDNDNSServerIP} 보낸 주체 : {localDNSAddr} 보낸 manifestFile : {manifest}")