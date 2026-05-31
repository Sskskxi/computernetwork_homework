# localDNSServer에서 해야되는 것
# net+ web server로 부터 받은 인덱스를 '질의'로 
# 4. query(예 : https://~)fmf net+ DNS 서버에 보내며
# 5. 실제 영화가 저장된 abCDN주소를 localDNS서버에 알림
# 6. 실제 영화가 저장된 abCDN의 주소를 local DNS 서버에 알림
# -> 글면 localDNS서버는 query를 abCDN DNS서버에 보냄
# 7. 실제 영화가 저장된 위치의 IP 주소를 포함한 답을 manifest 파일 형태로 얻음. 
# 를 거쳐 클라이언트에게 전달

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
sock.bind((localDNSServerIP, localDNSServerPort))

while True : 
  ClientData, ClientAddr = sock.recvfrom(256)
  indexURL = ClientData.decode()
  print(f"현재 위치 : localDNSServer - {localDNSServerIP} 받은 주체 : {ClientAddr} 받은 indexURL : {indexURL}")
  #여기서 netplusDNSServer에 indexURL를 보냄
  sock.sendto(indexURL.encode(), (netplusDNSServerIP, netplusDNSServerPort))
  #이후에 netplusDNSServer에서 indexURL에 해당하는 abCDN주소를 받아옴.
  abCDNdata, abCDNaddr = sock.recvfrom(256)
  abCDNUrl = abCDNdata.decode()
  print(f"현재 위치 : localDNSServer - {localDNSServerIP} 받은 주체 : {abCDNaddr} 받은 abCDN URL : {abCDNUrl}")
  sock.sendto(abCDNUrl.encode(), (abCDNDNSServerIP, abCDNDNSServerPort))
  # abCDN DNS 서버로부터 manifest 파일 수신
  manifestData, abCDNDNSAddr = sock.recvfrom(4096)
  manifest = manifestData.decode()
  print(f"현재 위치 : localDNSServer - {localDNSServerIP} 받은 주체 : {abCDNDNSAddr} 받은 manifest : {manifest}")
  # 클라이언트에게 manifest 전달
  sock.sendto(manifest.encode(), ClientAddr)
  print(f"현재 위치 : localDNSServer - {localDNSServerIP} 받은 주체 : {ClientAddr} 보낸 manifest : {manifest}")
