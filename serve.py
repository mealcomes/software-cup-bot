import erniebot
import requests
import json
import re
import settings

client_id="OTGggznGU2EfWbE8C98rgErR"
client_secret="LL4C8YBYLBO5oh4uSwZ6RKQLmhKCxXOo"

erniebot.api_type="aistudio"
erniebot.access_token="337f3cc0d25a120206c7003fc793e0c6ae8dbc99"

prompt_translate=("你是一个翻译官，工作是翻译、拼写纠正者和改进。"
                  "我将用任何语言与你交谈，你将检测语言，并在我的文本的更正和改进版本中用我要的语言回答。"
                  "保持意思不变，但让它们更有文学性。"
                  "你只回答更正，改进，而不是其他内容，不要写任何解释。"
                  # "如果我用的语言与我要的语言相同，那么直接重复我的话即可。"
                  "我发给你的内容的格式是：“我要的语言是：target。需要翻译的内容：content”，"
                  "其中target和content会被我替换成相应的文字")
prompt_improve=("你是一个文字美化工作者，工作是对所有内容进行语法纠错以及内容美化。"
                "请用简洁明了的语言，修改我给你的所有内容。"
                "如果内容存在语法错误，则仅仅修改语法即可，如果没有，则美化这段文字。"
                "我要你修改和美化，不要做任何解释。"
                "必须以中文作答。"
                "请务必保持文章的原意，")


def do_translate(data: dict):
    url="https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token=" + get_access_token(settings.translate_client_id, settings.translate_client_secret)

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
                "message": response['error_msg'],
            }
    else:
        return {
            'status': 'error',
            'message': 'service error!',
        }


def get_access_token(id, secret):
    url="https://aip.baidubce.com/oauth/2.0/token"
    params={"grant_type": "client_credentials", "client_id": id, "client_secret": secret}
    return str(requests.post(url, params=params).json().get("access_token"))


# def do_translate(data: dict):
#     content="我希望翻译成的语言是：{" + data['target'] + '}。需要翻译的内容是：{' + data['content'] + '}'
#     print("translate content: ", content)
#     response=erniebot.ChatCompletion.create(
#         model="ernie-3.5",
#         messages=[{
#             "role": "user",
#             "content": content
#         }],
#         system=prompt_translate,
#         disable_search=False,
#         top_p=0.8)
#     return response.get_result()


def do_improve(data: dict):
    content="{" + data['content'] + "}"
    response=erniebot.ChatCompletion.create(
        model="ernie-3.5",
        messages=[{
            "role": "user",
            "content": content
        }],
        system=prompt_improve,
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


def do_ocr(image_base64):
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + get_access_token(settings.ocr_client_id, settings.ocr_client_secret)

    payload=f"image={image_base64}&detect_direction=true&paragraph=false&probability=false"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    status=response.status_code
    response=json.loads(response.text)
    if status == 200:
        if 'words_result' in response:
            return {
                'status': 'ok',
                'message': response["words_result"]
            }
        else:
            return {
                'status': 'error',
                "message": response['error_msg'],
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
        system=prompt_mindmap,
        disable_search=False,
        top_p=0.95)
    # 提取```python\n(.*?)\n```
    pattern = r'```dot([\s\S]*?)```'

    mindmap_code = re.findall(pattern, response.get_result())[0]
    # mindmap_code = mindmap_code + '\nprint(buffered_image)'
    # print("mindmap_code: ", mindmap_code)
    # exec(mindmap_code)
    # print(locals())
    print(mindmap_code)
    # bi = locals()['buffered_image']

    return mindmap_code


if __name__ == '__main__':
    # print(do_translate({
    #     "target": "en",
    #     "content": "“我要的语言是中文” 现在回答我深圳有哪些地方比较好玩"
    # }))
    # for i in range(0, 10):
    print(do_improve({
        "content": "这句话用英文回答"
    }))
