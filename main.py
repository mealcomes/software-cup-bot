import base64
import mimetypes
import urllib.parse
from io import BytesIO

import requests
from PIL import Image
from flask import Flask, request, jsonify
from requests_toolbelt.multipart.encoder import MultipartEncoder

from render import render_mindmap
from serve import do_translate, do_improve, do_chat, do_ocr, do_generate_mindmap, do_continue

app=Flask(__name__)


@app.route('/translate', methods=['POST'])
def translate():
    message=request.get_json()
    print('translate message: ', message)
    try:
        result=do_translate(message)
        print(result)
        return result
    except Exception as e:
        print(e)
        print('translation unknown error!\n')
        return {
            'status': 'error',
            'message': 'server error!',
        }


@app.route('/improve', methods=['POST'])
def improve():
    message=request.get_json()
    print('improve message: ', message)
    try:
        result=do_improve(message)
        print(result)
        return result
    except Exception as e:
        print(e)
        print('improvement unknown error!\n')
        return {
            'status': 'error',
            "message": "server error!"
        }


@app.route('/ocr', methods=['POST'])
def ocr():
    image=request.files['image']
    print('recognize message: ', image)

    image_base64=base64.b64encode(image.stream.read())
    image_base64=urllib.parse.quote_from_bytes(image_base64)
    try:
        result=do_ocr(image_base64)
    except Exception as e:
        print(e)
        print('ocr unknown error')
        return {
            'status': 'error',
            "message": "server error!"
        }
    print(result)
    return result


@app.route('/asr', methods=['POST'])
def asr():
    # 获取上传的音频文件
    audio_file=request.files.get('file')
    if not audio_file:
        return jsonify({"error": "No file part"}), 400

    # 构造边界字符串
    boundary='wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

    fields={
        'file': (
            audio_file.filename,
            audio_file.read(),
            mimetypes.guess_type(audio_file.filename)[0] or 'application/octet-stream'
        ),
    }

    # 使用MultipartEncoder创建表单数据
    encoder=MultipartEncoder(fields=fields, boundary=boundary)

    # 设置目标API地址
    target_url='http://47.96.103.219:8888/asr'

    # 配置请求头，使用MultipartEncoder的content_type
    headers={
        'User-Agent': 'Your/User-Agent',
        'Accept': '*/*',
        'Host': '47.96.103.219:8888',
        'Connection': 'keep-alive',
        'Content-Type': encoder.content_type
    }

    # 发送POST请求到目标API
    try:
        response=requests.post(target_url, data=encoder, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 将目标API的响应直接返回给前端
        return response.content, response.status_code, response.headers.items()
    except requests.exceptions.RequestException as e:
        # 处理请求失败的情况
        return jsonify({"error": f"Failed to forward request: {str(e)}"}), 500


@app.route('/mindmap', methods=['GET'], )
def mindmap():
    text=request.args.get('text')
    print('mindmap message: ', text)
    try:
        buffered_image=do_generate_mindmap({
            'content': text
        })
        img=render_mindmap(buffered_image)
    except Exception as e:
        print(e)
        print('mindmap unknown error')
        return {
            'status': 'error',
            "message": "server error!"
        }
    img_base64=base64.b64encode(img).decode('utf-8')
    img=Image.open(BytesIO(img))
    width, height=img.size

    # 构造Base64编码的Data URI Scheme，用于直接在HTML中展示图像
    data_uri=f"data:image/png;base64,{img_base64}"
    response_data={
        'image_data_uri': data_uri,
        'width': width,
        'height': height
    }
    print(response_data)

    # 直接返回Base64编码的字符串，或者根据实际需求调整返回内容和类型
    return response_data


@app.route('/continuation', methods=['POST'])
def continuation():
    message=request.get_json()
    print('continuation message: ', message)
    try:
        result=do_continue(message)
        print(result)
        return result
    except Exception as e:
        print(e)
        print('continuation unknown error!\n')
        return {
            'status': 'error',
            'message': 'server error!',
        }


@app.route('/chat', methods=['GET'], )
def chat():
    param=request.args.get('content')
    res=do_chat({
        'content': param
    })
    return "<p style=\"color: red\">" + res + "</p>"


if __name__ == '__main__':
    app.run(port=86)
