import json

import requests
from flask import Flask, request

from serve import do_translate, do_improve

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


if __name__ == '__main__':
    app.run(port=86)
