import base64
import mimetypes
import urllib.parse
from io import BytesIO
import io

import requests
from PIL import Image
from flask import Flask, request, jsonify, Response
from requests_toolbelt.multipart.encoder import MultipartEncoder

from render import render_mindmap
from serve import do_translate, do_improve, do_chat, do_ocr, do_generate_mindmap, do_continue, do_summary

app=Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    message=request.get_json()
    # if not message['content']:
    #     return {
    #         'status': 'error',
    #         'message': 'content can\'t be null!'
    #     }
    print('chat message: ', message)
    try:
        return Response(do_chat(message))
    except Exception as e:
        print('chat error: ', e)
        return {
            'status': 'error',
            'message': 'server error!',
        }


@app.route('/translate', methods=['POST'])
def translate():
    message=request.get_json()
    if not message['content']:
        return {
            'status': 'error',
            'message': 'content can\'t be null!'
        }
    print('translate message: ', message)
    try:
        result=do_translate(message)
        print('translate: ', result)
        return result
    except Exception as e:
        print('translate error: ', e)
        return {
            'status': 'error',
            'message': 'server error!',
        }


@app.route('/improve', methods=['POST'])
def improve():
    message=request.get_json()
    if not message['content']:
        return {
            'status': 'error',
            'message': 'content can\'t be null!'
        }
    print('improve message: ', message)
    try:
        result=do_improve(message)
        print('improve: ', result)
        return result
    except Exception as e:
        print('improve error: ', e)
        return {
            'status': 'error',
            "message": "server error!"
        }


@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' in request.files:
        target=request.files['image']
        file_type='image'
    else:
        target=request.files['pdf_file']
        file_type='pdf_file'
    print('recognize message: ', target)

    tmp=base64.b64encode(io.BytesIO(target.read()).getvalue())
    image_base64=urllib.parse.quote_from_bytes(tmp)
    try:
        result=do_ocr(image_base64, file_type)
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
        return jsonify({
            "message": "No file part",
            "status": "error"
        })

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
        return {
            "status": "ok",
            "message": eval(response.content.decode("utf-8")).get("result")
        }
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to forward request: {str(e)}"
        })


@app.route('/mindmap', methods=['GET'], )
def mindmap():
    text=request.args.get('text')
    if not text:
        return {
            'status': 'error',
            'message': 'content can\'t be null!'
        }
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
    if not message['content']:
        return {
            'status': 'error',
            'message': 'content can\'t be null!'
        }
    print('continuation message: ', message)
    try:
        result=do_continue(message)
        print('continuation: ', result)
        return result
    except Exception as e:
        print('continuation error: ', e)
        return {
            'status': 'error',
            'message': 'server error!',
        }


@app.route('/summary', methods=['POST'])
def summary():
    message=request.get_json()
    if not message['content']:
        return {
            'status': 'error',
            'message': 'content can\'t be null!'
        }
    print('summary message: ', message)
    try:
        result=do_summary(message)
        print(result)
        return result
    except Exception as e:
        print('summary error: ', e)
        return {
            'status': 'error',
            'message': 'server error!',
        }


@app.route('/chat', methods=['GET'], )
def chatTest():
    param=request.args.get('content')
    res=do_chat({
        'content': param
    })
    return "<p style=\"color: red\">" + res + "</p>"


if __name__ == '__main__':
    app.run(port=86)
    # socketio.run(app, host='0.0.0.0', port=86, allow_unsafe_werkzeug=True)
