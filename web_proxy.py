import math

from flask import Flask, request, Response, stream_with_context
from datetime import datetime
import requests
import json
import os
import yaml
from rerank import rerank


def load_config(file_path='config.yaml'):
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f'未配置{file_path}')
        return None
        # raise FileNotFoundError(f"配置文件 {file_path} 不存在！")
    except Exception as e:
        raise Exception(f"配置解析失败: {str(e)}")


config = load_config(file_path='config.yaml')
default_config = load_config(file_path='default_config.yaml')


def get_config(config, default_config, key_list):
    use_config = True
    if config is not None:
        sub_config = config
        for key in key_list:
            if key in sub_config:
                sub_config = sub_config[key]
            else:
                use_config = False
                break
    else:
        use_config = False
    if use_config:
        return sub_config
    else:
        sub_config = default_config
        for key in key_list:
            sub_config = sub_config[key]
        return sub_config


# URL参数
ait_searxng_url = get_config(config, default_config, ('url', 'ait_searxng_url'))
ait_target_server = get_config(config, default_config, ('url', 'ait_target_server'))

# 搜索参数
max_results = get_config(config, default_config, ('searxng', 'max_results'))
preferences = get_config(config, default_config, ('searxng', 'preferences'))
categories = get_config(config, default_config, ('searxng', 'categories'))
language = get_config(config, default_config, ('searxng', 'language'))
format = get_config(config, default_config, ('searxng', 'format'))
results_on_new_tab = get_config(config, default_config, ('searxng', 'results_on_new_tab'))
safesearch = get_config(config, default_config, ('searxng', 'safesearch'))
theme = get_config(config, default_config, ('searxng', 'theme'))

# RAG参数
rag_turn_on = get_config(config, default_config, ('rag', 'turn_on'))
rerank_model_url = get_config(config, default_config, ('rag', 'rerank_model_url'))
rerank_model = get_config(config, default_config, ('rag', 'rerank_model'))
top_n = get_config(config, default_config, ('rag', 'top_n'))
max_chunks_per_doc = get_config(config, default_config, ('rag', 'max_chunks_per_doc'))
tokens = get_config(config, default_config, ('rag', 'tokens'))

app = Flask(__name__)

searxng_url = os.getenv('ait_searxng_url', ait_searxng_url)
target_server = os.getenv('ait_target_server', ait_target_server)


def web_search(question):
    print('start searching...')
    return searxng_search(question)


def get_page(url):
    return requests.get(url).text


def searxng_search(query):
    results = []
    max_pages = math.ceil(max_results / 10)
    for i in range(1, max_pages + 1):
        search_url = f"{searxng_url}/?preferences={preferences}"
        search_url = search_url.replace(f'q=%s',
                                        f'&pageno={i}&categories={categories}&language={language}&format=json&q={query}&results_on_new_tab={results_on_new_tab}&safesearch={safesearch}&theme={theme}')
        _results = requests.get(search_url).content
        results = results + json.loads(_results)['results']
    results = results[:max_results]
    print(f'搜索到{len(results)}条结果,以下为筛选后的内容')
    results_str = ''
    if rag_turn_on:
        documents = [result['content'] for result in results]
        top_n_indexs = rerank(query=query, documents=documents, url=rerank_model_url, tokens=tokens, model=rerank_model,
                              top_n=top_n, max_chunks_per_doc=max_chunks_per_doc)
        results = [results[i] for i in top_n_indexs]
    for i, result in enumerate(results):
        print(f'第{i + 1}条:{result["title"]}')
        results_str += '[webpage ' + str(i + 1) + ' begin]<title>' + result['title'] + '</title><url>' + result[
            'url'] + '</url><content>' + result['content'] + '</content>[webpage ' + str(i + 1) + ' end]'
        # get_page(result['url'])
    return results_str


def get_web_search_prompt(search_results, question):
    cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    search_answer_zh_template = \
        f'''# 以下内容是基于用户发送的消息的搜索结果:
        {search_results}
        在我给你的搜索结果中，每个结果都是[webpage X begin]...[webpage X end]格式的，X代表每篇文章的数字索引,<url>Y</url>标签代表每篇文章的链接。请在适当的情况下在句子末尾引用上下文。请按照引用编号<sup>[X](Y)</sup>的格式在答案中对应部分引用上下文。如果一句话源自多个上下文，请列出所有相关的引用编号，例如<sup>[3](url),[5](url)</sup>，切记不仅要将引用集中在最后返回引用编号，还要在答案对应部分列出。
        在回答时，请注意以下几点：
        - 今天是{cur_date}。
        - 并非搜索结果的所有内容都与用户的问题密切相关，你需要结合问题，对搜索结果进行甄别、筛选。
        - 对于列举类的问题（如列举所有航班信息），尽量将答案控制在10个要点以内，并告诉用户可以查看搜索来源、获得完整信息。优先提供信息完整、最相关的列举项；如非必要，不要主动告诉用户搜索结果未提供的内容。
        - 对于创作类的问题（如写论文），请务必在正文的段落中引用对应的参考编号，例如<sup>[3](url),[5](url)</sup>，不能只在文章末尾引用。你需要解读并概括用户的题目要求，选择合适的格式，充分利用搜索结果并抽取重要信息，生成符合用户要求、极具思想深度、富有创造力与专业性的答案。你的创作篇幅需要尽可能延长，对于每一个要点的论述要推测用户的意图，给出尽可能多角度的回答要点，且务必信息量大、论述详尽。
        - 对于url的引用，不要省略http或者https。所有的url都必须来自<url>标签，且不允许做任何修改。
        - 如果回答很长，请尽量结构化、分段落总结。如果需要分点作答，尽量控制在5个点以内，并合并相关的内容。
        - 对于客观类的问答，如果问题的答案非常简短，可以适当补充一到两句相关信息，以丰富内容。
        - 你需要根据用户要求和回答内容选择合适、美观的回答格式，确保可读性强。
        - 你的回答应该综合多个相关网页来回答，不能重复引用一个网页。
        - 除非用户要求，否则你回答的语言需要和用户提问的语言保持一致。
        - 在回答最后列出所有参考过的网页的title和url，以便用户查看更多信息。
        # 用户消息为：
        {question}'''
    return search_answer_zh_template


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
        if json['messages'][-1]['role'] == 'user':
            search_result = web_search(json['messages'][-1]['content'])
            json['messages'][-1]['content'] = get_web_search_prompt(search_result, json['messages'][-1]['content'])
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
