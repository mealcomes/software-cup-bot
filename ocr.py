import requests
import base64
from serve import get_access_token
'''
通用文字识别（高精度含位置版）
'''

request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
# 二进制方式打开图片文件
f = open("C:\\Users\\admin\\Pictures\\test\\4C847195E59B4805C6BD82E7A60E709A.jpg", 'rb')
img = base64.b64encode(f.read())

access_token = get_access_token()
print(access_token)
params = {"image":img}
# access_token = '[调用鉴权接口获取的token]'
request_url = request_url + "?access_token=" + access_token
headers = {'content-type': 'application/x-wwwrm-urlencoded'}
response = requests.post(request_url, data=params, headers=headers)
if response:
    print (response.json())
