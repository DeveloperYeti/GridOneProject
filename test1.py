import requests
key = 'I3imu+UUWxMLVLf6ImvuPB71ZXzCdIW0KAHyuRDKDtOYGK/HWZdE6TZvPjCbj3NlV2KTxUKRKGESkpXbeBSWJw=='
url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty'
params ={'serviceKey' : key, 'returnType' : 'json', 'numOfRows' : '100', 'pageNo' : '1', 'sidoName' : '서울', 'ver' : '1.0' }

response = requests.get(url, params=params)
print(response.content)