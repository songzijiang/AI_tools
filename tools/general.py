import yaml
import requests
from openai import OpenAI
import json
from datetime import datetime

def load_config(file_path='config.yaml'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f'未配置{file_path}')
        return None
        # raise FileNotFoundError(f"配置文件 {file_path} 不存在！")
    except Exception as e:
        raise Exception(f"配置解析失败: {str(e)}")


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


def rerank(query, documents, url, token, model, top_n, max_chunks_per_doc):
    # 配置siliconflow API
    payload = {
        "model": model,  # 选择模型
        "query": query,
        "documents": documents,
        "top_n": top_n,  # 选择返回的文档数量
        "return_documents": True,
        "max_chunks_per_doc": max_chunks_per_doc  # 选择返回的文档的词数
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response_dict = json.loads(response.text)
    if "results" in response_dict:
        top_n_results = response_dict["results"]
        return_documents, documents_idxs = [], []
        for result in top_n_results:
            return_documents.append(result["document"]["text"])
            documents_idxs.append(result["index"])
        return documents_idxs  # 返回的排序id list
    else:
        return []


class Tools:
    def __init__(self, config, default_config, tools):
        # 再次询问
        # - 如果用户提供的信息不足，请再次询问用户以获得足够的信息
        base_url = get_config(config, default_config, ('tools', 'server'))
        token = get_config(config, default_config, ('tools', 'token'))
        self.tools = tools
        self.model = get_config(config, default_config, ('tools', 'model'))
        self.prompt = \
            '''# 现在有一些工具，请根据用户输入的信息，选择其中零个或多个工具进行使用。工具列表如下:
            {tools}
            - 请以json格式返回工具名称和工具所需要的参数。
            - 今天是{cur_date}。
            - 请直接返回json格式的数组字符串，不要使用markdown格式或者输出任何多余内容。
            - 每个返回的json有两个属性，tool和params，tool为工具名称，params为工具所需要的参数，params为数组格式。
            以下是用户输入的信息:
            {text}'''
        self.client = OpenAI(api_key=token, base_url=base_url)

    def make_prompt(self, results, text):
        prompt_result = f'''# 你是一个可以使用工具的AI助手，并且你已经根据用户的要求，使用了以下工具:
        {[{t: self.tools[t]['描述']} for t in self.tools if t in results.keys()]}
        - 上述已使用的工具的返回结果如下:
        {str(results)}
        - 用户的输入内容如下:
        {text}
        - 今天是{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。
        - 请根据用户的输入内容和工具的返回结果，生成一个新的回复内容。
        - 你需要根据用户要求和工具的返回结果选择合适、美观的回答格式，确保可读性强。
        - 除非用户要求，否则你回答的语言需要和用户提问的语言保持一致。
        - 回答一定要参考工具的返回结果，并且如果工具的返回结果中有其他要求，你需要满足这些要求。
        '''
        return prompt_result

    def select_tools(self, message):
        try:
            print(f'可用工具列表:{self.tools.keys()}')
            text = self.prompt.replace('{tools}', str(self.tools)).replace('{text}', message).replace('{cur_date}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user",
                     "content": text}
                ],
                temperature=0.6,
                max_tokens=1024,
                stream=False,
            )
            returns = response.choices[0].message.content.split('</think>')
            if len(returns) < 2:
                thinking = ''
                content = returns[0]
            else:
                thinking, content = returns
                thinking = thinking.replace('<think>', '').strip().replace('\n\n', '\n')
                print('--------------------工具选择思考链--------------------')
                print(thinking)
            content = content.strip().replace('\n', ' ').replace('```json', '').replace('```', '')
        except Exception as e:
            print(f'选择工具失败:{str(e)}')
            thinking = '选择工具失败'
            content = ''
        return thinking, json.loads(content)
