import json

import requests
from flask import Flask, request, jsonify
import mimetypes
from serve import do_translate, do_improve
from requests_toolbelt.multipart.encoder import MultipartEncoder

app=Flask(__name__)


@app.route('/translate', methods=['POST'])
def translate():
    message=request.get_json()
    print('translate message: ', message)
    result=dict()
    try:
        result=do_translate(message)
    except:
        print('translate unknown error!\n')
        return {
            'status': 'error',
            'message': 'server error!',
        }
    print(result)
    return result


@app.route('/improve', methods=['POST'])
def improve():
    message=request.get_json()
    print('improve message: ', message)
    result=dict()
    try:
        result=do_improve(message)
    except:
        print('improve unknown error!\n')
        return {
                'status': 'error',
                "message": "server error!"
            }
    print(result)
    return result

@app.route('/asr', methods=['POST'])
def asr():
    # 获取上传的音频文件
    audio_file = request.files.get('file')
    if not audio_file:
        return jsonify({"error": "No file part"}), 400

    # 构造边界字符串
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

    fields = {
        'file': (
            audio_file.filename,
            audio_file.read(),
            mimetypes.guess_type(audio_file.filename)[0] or 'application/octet-stream'
        ),
    }

    # 使用MultipartEncoder创建表单数据
    encoder = MultipartEncoder(fields=fields, boundary=boundary)
    
    # 设置目标API地址
    target_url = 'http://47.96.103.219:8888/asr'
    
    # 配置请求头，使用MultipartEncoder的content_type
    headers = {
        'User-Agent': 'Your/User-Agent',
        'Accept': '*/*',
        'Host': '47.96.103.219:8888',
        'Connection': 'keep-alive',
        'Content-Type': encoder.content_type
    }

    # 发送POST请求到目标API
    try:
        response = requests.post(target_url, data=encoder, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 将目标API的响应直接返回给前端
        return response.content, response.status_code, response.headers.items()
    except requests.exceptions.RequestException as e:
        # 处理请求失败的情况
        return jsonify({"error": f"Failed to forward request: {str(e)}"}), 500

# @app.route('/ocr', methods=['POST'])
# def ocr():



if __name__ == '__main__':
    app.run(port=86)
