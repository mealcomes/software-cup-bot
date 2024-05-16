import erniebot
import requests
import json
import re
import settings

erniebot.api_type="aistudio"
erniebot.access_token="92bbaa431fa5b7696620b9825ada369a6b9d792f"


def get_access_token(id, secret):
    url="https://aip.baidubce.com/oauth/2.0/token"
    params={"grant_type": "client_credentials", "client_id": id, "client_secret": secret}
    return str(requests.post(url, params=params).json().get("access_token"))


def do_translate(data: dict):
    url="https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token=" + get_access_token(
        settings.translate_client_id, settings.translate_client_secret)

    payload=json.dumps({
        "q": data['content'],
        "from": "auto",
        "to": data['target']
    })
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response=requests.request("POST", url, headers=headers, data=payload)
    status=response.status_code
    response=json.loads(response.text)
    if status == 200:
        if 'result' in response:
            return {
                'status': 'ok',
                'message': response["result"]["trans_result"][0]["dst"]
            }
        else:
            return {
                'status': 'error',
                "message": 'server error!',
            }
    else:
        return {
            'status': 'error',
            'message': 'service error!',
        }


def do_improve(data: dict):
    content="{" + data['content'] + "}"
    response=erniebot.ChatCompletion.create(
        model="ernie-3.5",
        messages=[{
            "role": "user",
            "content": content
        }],
        system=settings.prompt_improve,
        # disable_search=False,
        top_p=0.85)
    if response.rcode == 200:
        if 'result' in response:
            return {
                'status': 'ok',
                'message': response["result"]
            }
        else:
            return {
                'status': 'error',
                "message": erniebot.api_type + ' error'
            }


def do_ocr(file_base64, file_type):
    url="https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + get_access_token(
        settings.ocr_client_id, settings.ocr_client_secret)

    payload=f"{file_type}={file_base64}&detect_direction=true&paragraph=false&probability=false"
    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response=requests.request("POST", url, headers=headers, data=payload)
    status=response.status_code
    response=json.loads(response.text)
    if status == 200:
        if 'words_result' in response:
            return {
                'status': 'ok',
                'message': response["words_result"]
            }
        else:
            print('ocr: ', response['error_code'] , response['error_msg'])
            return {
                'status': 'error',
                "message": 'server error!'
            }
    else:
        return {
            'status': 'error',
            'message': 'service error!',
        }


def do_chat(data: dict):
    response=erniebot.ChatCompletion.create(
        model="ernie-4.0",
        messages=[{
            "role": "user",
            "content": data['content']
        }],
        # system=prompt_improve,
        # disable_search=False,
        top_p=0.95)
    return response.get_result()


def do_generate_mindmap(data: dict):
    response=erniebot.ChatCompletion.create(
        model="ernie-4.0",
        messages=[{
            "role": "user",
            "content": data['content']
        }],
        system=settings.prompt_mindmap,
        disable_search=False,
        top_p=0.95)
    # 提取```python\n(.*?)\n```
    pattern=r'```dot([\s\S]*?)```'

    mindmap_code=re.findall(pattern, response.get_result())[0]
    print(mindmap_code)
    # bi = locals()['buffered_image']

    return mindmap_code


def do_continue(data: dict):
    content="{" + data['content'] + "}"
    response=erniebot.ChatCompletion.create(
        model="ernie-4.0",
        messages=[{
            "role": "user",
            "content": content
        }],
        system=settings.prompt_continue,
        disable_search=False,
        top_p=0.90)
    if response.rcode == 200:
        if 'result' in response:
            return {
                'status': 'ok',
                'message': response["result"]
            }
        else:
            return {
                'status': 'error',
                "message": 'server error!',
            }
    else:
        return {
            'status': 'error',
            "message": erniebot.api_type + ' error'
        }


def do_summary(data: dict):
    response=erniebot.ChatCompletion.create(
        model="ernie-4.0",
        messages=[{
            "role": "user",
            "content": data['content']
        }],
        system=settings.prompt_summary,
        disable_search=True,
        top_p=0.90)
    if response.rcode == 200:
        if 'result' in response:
            return {
                'status': 'ok',
                'message': response["result"]
            }
        else:
            return {
                'status': 'error',
                "message": 'server error!',
            }
    else:
        return {
            'status': 'error',
            "message": erniebot.api_type + ' error'
        }


if __name__ == '__main__':
    # print(do_translate({
    #     "target": "en",
    #     "content": "“我要的语言是中文” 现在回答我深圳有哪些地方比较好玩"
    # }))
    # for i in range(0, 10):
    print(do_improve({
        "content": "这句话用英文回答"
    }))