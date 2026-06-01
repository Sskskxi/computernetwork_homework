#파일에서 chunk시간을 자동으로 계산하도록 해야 함 -> 그 값들을 어떻게 정의..? 
## 

movie1 = {"duration": 120, "HQ": 45, "MQ": 30, "LQ": 15}
movie2 = {"duration":  60, "HQ": 24, "MQ": 16, "LQ":  8}
movie3 = {"duration": 150, "HQ": 45, "MQ": 30, "LQ": 15}
movie4 = {"duration": 240, "HQ": 60, "MQ": 40, "LQ": 20}
movie5 = {"duration": 180, "HQ": 54, "MQ": 36, "LQ": 18}
movie6 = {"duration":  90, "HQ": 27, "MQ": 18, "LQ":  9}
movie7 = {"duration": 300, "HQ": 60, "MQ": 40, "LQ": 25}
movie8 = {"duration": 120, "HQ": 36, "MQ": 24, "LQ": 12}
movie9 = {"duration": 210, "HQ": 63, "MQ": 42, "LQ": 21}


#chunk 정보
movies = {
  "1":movie1,
  "2":movie2,
  "3":movie3,
  "4":movie4,
  "5":movie5,
  "6":movie6,
  "7":movie7,
  "8":movie8,
  "9":movie9
}

#URL정보용
movieIndex = {
  "1" : "https://index.netplus.com/2emCuam",
  "2" : "https://index.netplus.com/2eacd873N",
  "3" : "https://index.netplus.com/c8a19CAJM",
  "4" : "https://index.netplus.com/099vNDJC",
  "5" : "https://index.netplus.com/98ccjndq",
  "6" : "https://index.netplus.com/xcav1e",
  "7" : "https://index.netplus.com/cUAJD9138",
  "8" : "https://index.netplus.com/acvuaNKK",
  "9" : "https://index.netplus.com/IAC1389dNE"
}

abCDNURLs = {
      "1": "https://abCDN.net/1",
      "2": "https://abCDN.net/2",
      "3": "https://abCDN.net/3",
      "4": "https://abCDN.net/4",
      "5": "https://abCDN.net/5",
      "6": "https://abCDN.net/6",
      "7": "https://abCDN.net/7",
      "8": "https://abCDN.net/8",
      "9": "https://abCDN.net/9"
}