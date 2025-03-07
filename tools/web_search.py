import requests
import math
from tools.general import rerank, get_config
import json
import os
from datetime import datetime


def get_web_search_prompt(prompt, search_results):
    search_answer_zh_template = prompt.replace('{search_results}', search_results)
    return search_answer_zh_template


class Searxng:
    def description(self):
        return {'参数数量': 1, '描述': '使用搜索引擎进行搜索,param1为对用户信息提炼后需要搜索的内容'}

    def get_parameters(self):
        return 'query'

    def __init__(self, config, default_config):
        # 搜索参数
        self.max_page = get_config(config, default_config, ('searxng', 'max_page'))
        self.preferences = get_config(config, default_config, ('searxng', 'preferences'))
        self.categories = get_config(config, default_config, ('searxng', 'categories'))
        self.language = get_config(config, default_config, ('searxng', 'language'))
        self.format = get_config(config, default_config, ('searxng', 'format'))
        self.results_on_new_tab = get_config(config, default_config, ('searxng', 'results_on_new_tab'))
        self.safesearch = get_config(config, default_config, ('searxng', 'safesearch'))
        self.theme = get_config(config, default_config, ('searxng', 'theme'))
        self.prompt = get_config(config, default_config, ('prompt',))

        # RAG参数
        self.rag_turn_on = get_config(config, default_config, ('rag', 'turn_on'))
        self.rerank_model_url = get_config(config, default_config, ('rag', 'server'))
        self.rerank_model = get_config(config, default_config, ('rag', 'model'))
        self.top_n = get_config(config, default_config, ('rag', 'top_n'))
        self.max_chunks_per_doc = get_config(config, default_config, ('rag', 'max_chunks_per_doc'))
        self.token = get_config(config, default_config, ('rag', 'token'))

        ait_searxng_url = get_config(config, default_config, ('url', 'ait_searxng_url'))
        self.searxng_url = os.getenv('ait_searxng_url', ait_searxng_url)

    def get_page(self, url):
        return requests.get(url).text

    def search(self, query):
        print(f'start searching {query}...')
        results = []
        for i in range(1, self.max_page + 1):
            search_url = f"{self.searxng_url}/?preferences={self.preferences.replace('preferences=', '').replace('/', '')}"
            search_url = search_url.replace(f'q=%s',
                                            '') + f'&pageno={i}&categories={self.categories}&language={self.language}&format=json&q={query}&results_on_new_tab={self.results_on_new_tab}&safesearch={self.safesearch}&theme={self.theme}'
            print(f'搜索第{i}页,搜索链接为:{search_url}')
            _results = requests.get(search_url).content
            results = results + json.loads(_results)['results']
        print(f'搜索到{len(results)}条结果,以下为筛选后的内容')
        results_str = ''
        if self.rag_turn_on:
            documents = [result['content'] for result in results]
            top_n_indexs = rerank(query=query, documents=documents, url=self.rerank_model_url, token=self.token,
                                  model=self.rerank_model,
                                  top_n=self.top_n, max_chunks_per_doc=self.max_chunks_per_doc)
            results = [results[i] for i in top_n_indexs]
        for i, result in enumerate(results):
            print(f'第{i + 1}条:{result["title"]}')
            results_str += '[webpage ' + str(i + 1) + ' begin]<title>' + str(
                result['title']) + '</title><url>' + str(
                result[
                    'url']) + '</url><content>' + str(result['content']) + '</content>[webpage ' + str(
                i + 1) + ' end]'
        # get_page(result['url'])

        return get_web_search_prompt(self.prompt, results_str)
