import base64
import urllib.parse

from flask import Flask, request

from serve import do_translate, do_improve, do_chat, do_ocr

app=Flask(__name__)


@app.route('/translate', methods=['POST'])
def translate():
    message=request.get_json()
    print('translate message: ', message)
    result=dict()
    try:
        result=do_translate(message)
    except:
        print('translation unknown error!\n')
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
    try:
        result=do_improve(message)
    except:
        print('improvement unknown error!\n')
        return {
            'status': 'error',
            "message": "server error!"
        }
    print(result)
    return result


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
        print('reorganization unknown error')
        return {
            'status': 'error',
            "message": "server error!"
        }
    print(result)
    return result


@app.route('/chat', methods=['GET'], )
def chat():
    param=request.args.get('content')
    res=do_chat({
        'content': param
    })
    return "<p style=\"color: red\">" + res + "</p>"


if __name__ == '__main__':
    app.run(port=86)
