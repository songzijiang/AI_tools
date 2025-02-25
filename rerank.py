import requests
import json

def rerank(query, documents, url, tokens, model, top_n, max_chunks_per_doc):
    # 配置siliconflow API
    payload = {
        "model": model, # 选择模型
        "query": query,
        "documents": documents,
        "top_n": top_n, # 选择返回的文档数量
        "return_documents": True,
        "max_chunks_per_doc": max_chunks_per_doc # 选择返回的文档的词数
    }

    headers = {
        "Authorization": f"Bearer {tokens}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response_dict = json.loads(response.text)
    top_n_results = response_dict["results"]
    return_documents, documents_idxs = [], []
    for result in top_n_results:
        return_documents.append(result["document"]["text"])
        documents_idxs.append(result["index"])
    return documents_idxs # 返回的排序id list
