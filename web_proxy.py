from flask import Flask, request, Response, stream_with_context
import requests
import os
import json
from tools.web_search import Searxng
from tools.mail import Mail
from datetime import datetime
from tools.general import get_config, load_config, Tools

config = load_config(file_path='config.yaml')
default_config = load_config(file_path='default_config.yaml')

# URL参数
ait_target_server = get_config(config, default_config, ('url', 'ait_target_server'))
target_server = os.getenv('ait_target_server', ait_target_server)

app = Flask(__name__)

# 注入工具类和说明
web_search = Searxng(config, default_config)
mail = Mail(config, default_config)

tools = {'websearch': web_search.description(), 'mail': mail.description()}
instance = {'websearch': web_search.search, 'mail': mail.send_mail}

tool_client = Tools(config, default_config, tools)


@app.route('/<path:dummy>', methods=['GET', 'POST'])
def proxy(dummy):
    host = request.host
    print("请求host:", host)
    # 获取请求 URL
    url = f'{target_server}/{dummy}'
    print(f"真实请求的url:{url}")
    if 'chat/completions' in url:
        print(f"参数内容:{request.json}")
        request_json = request.json
        if request_json['messages'][-1]['role'] == 'user':
            message = request_json['messages'][-1]['content']
            # 选择需要使用的工具
            reason, need_tools = tool_client.select_tools(message)
            print(f"选择的工具:{need_tools}")
            results = {}
            for tool in need_tools:
                toole_name = tool['tool']
                params = tool['params']
                results[toole_name] = {'params': str(params), 'result': instance[toole_name](*params)}
            request_json['messages'][-1]['content'] = tool_client.make_prompt(results, message)
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
