from flask import Flask, request, Response, stream_with_context
import requests
import os

from web import searxng
from prompt import get_web_search_prompt
from general import get_config, load_config

config = load_config(file_path='config.yaml')
default_config = load_config(file_path='default_config.yaml')

# URL参数
ait_target_server = get_config(config, default_config, ('url', 'ait_target_server'))
target_server = os.getenv('ait_target_server', ait_target_server)

app = Flask(__name__)

web_search = searxng(config, default_config)


@app.route('/<path:dummy>', methods=['GET', 'POST'])
def proxy(dummy):
    host = request.host
    print("请求host:", host)
    # 获取请求 URL
    url = f'{target_server}/{dummy}'
    print(f"真实请求的url:{url}")
    if 'chat/completions' in url:
        print(f"参数内容:{request.json}")
        json = request.json
        if json['messages'][-1]['role'] == 'user' and '查询' in json['messages'][-1]['content']:
            message = json['messages'][-1]['content']
            message.replace('查询', '')
            search_result = web_search.search(message)
            json['messages'][-1]['content'] = get_web_search_prompt(config['prompt'], search_result, message)
        response = requests.request(
            headers=request.headers,
            method=request.method,
            url=url,
            params=request.args,
            data=dict(request.form),
            json=request.json,
            stream=True
        )
        # 将目标服务器的响应返回给客户端
        print(f"真实响应status_code: {response.status_code}")
        return Response(stream_with_context(response.iter_content()), content_type=response.headers['Content-Type'],
                        status=response.status_code)
    else:
        response = requests.request(
            headers=request.headers,
            method=request.method,
            url=url,
            params=request.args,
            data=dict(request.form)
        )
        # 将目标服务器的响应返回给客户端
        print(f"真实响应status_code: {response.status_code}")
        return Response(response.content, content_type=response.headers['Content-Type'],
                        status=response.status_code)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv('ait_port', '5000')), debug=False)
