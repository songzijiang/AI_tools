import requests
import math
from rerank import rerank
import json
from general import get_config
import os


class searxng:
    def __init__(self, config, default_config):
        # 搜索参数
        self.max_results = get_config(config, default_config, ('searxng', 'max_results'))
        self.preferences = get_config(config, default_config, ('searxng', 'preferences'))
        self.categories = get_config(config, default_config, ('searxng', 'categories'))
        self.language = get_config(config, default_config, ('searxng', 'language'))
        self.format = get_config(config, default_config, ('searxng', 'format'))
        self.results_on_new_tab = get_config(config, default_config, ('searxng', 'results_on_new_tab'))
        self.safesearch = get_config(config, default_config, ('searxng', 'safesearch'))
        self.theme = get_config(config, default_config, ('searxng', 'theme'))

        # RAG参数
        self.rag_turn_on = get_config(config, default_config, ('rag', 'turn_on'))
        self.rerank_model_url = get_config(config, default_config, ('rag', 'rerank_model_url'))
        self.rerank_model = get_config(config, default_config, ('rag', 'rerank_model'))
        self.top_n = get_config(config, default_config, ('rag', 'top_n'))
        self.max_chunks_per_doc = get_config(config, default_config, ('rag', 'max_chunks_per_doc'))
        self.tokens = get_config(config, default_config, ('rag', 'tokens'))

        ait_searxng_url = get_config(config, default_config, ('url', 'ait_searxng_url'))
        self.searxng_url = os.getenv('ait_searxng_url', ait_searxng_url)

    def get_page(self, url):
        return requests.get(url).text

    def search(self, query):
        print('start searching, searxng selected...')
        results = []
        max_pages = math.ceil(self.max_results / 10)
        for i in range(1, max_pages + 1):
            search_url = f"{self.searxng_url}/?preferences={self.preferences}"
            search_url = search_url.replace(f'q=%s',
                                            f'&pageno={i}&categories={self.categories}&language={self.language}&format=json&q={query}&results_on_new_tab={self.results_on_new_tab}&safesearch={self.safesearch}&theme={self.theme}')
            _results = requests.get(search_url).content
            results = results + json.loads(_results)['results']
        results = results[:self.max_results]
        print(f'搜索到{len(results)}条结果,以下为筛选后的内容')
        results_str = ''
        if self.rag_turn_on:
            documents = [result['content'] for result in results]
            top_n_indexs = rerank(query=query, documents=documents, url=self.rerank_model_url, tokens=self.tokens,
                                  model=self.rerank_model,
                                  top_n=self.top_n, max_chunks_per_doc=self.max_chunks_per_doc)
            results = [results[i] for i in top_n_indexs]
        for i, result in enumerate(results):
            print(f'第{i + 1}条:{result["title"]}')
            results_str += '[webpage ' + str(i + 1) + ' begin]<title>' + result['title'] + '</title><url>' + result[
                'url'] + '</url><content>' + result['content'] + '</content>[webpage ' + str(i + 1) + ' end]'
            # get_page(result['url'])
        return results_str
