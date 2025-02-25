# AI_tools
一个AI代理脚本，专注于无感嵌入各类LLM api中

目前支持的功能：

1. 可以添加联网功能，让离线AI支持联网搜索。√
2. RAG搜寻。×
3. AI自主使用工具。×
4. 自定义知识嵌入。×

本脚本搜索仅支持searxNG搜索，默认偏好使用谷歌搜索。其他搜索引擎请和设置自行更改preferences参数

使用方法：
```
git clone https://github.com/songzijiang/AI_tools.git
cd AI_tools
pip install -r requirements.txt
cp default_config.yaml config.yaml
```
修改config.yaml中的ait_searxng_url和ait_target_server

ait_searxng_url:为searxng服务器地址，部署参考[这里](https://github.com/searxng/searxng)。setting.xml中记得添加支持json格式。如果searxng无法搜索，考虑为searxng添加代理。

ait_target_server:为原始的模型地址

启动服务：`python web_proxy.py`

- 运行以后，原本LLM模型API访问http://ip:port , 现在只需要把模型url改成http://127.0.0.1:5000 就能实现联网搜索

- 网页开启rag排序请设置rag-turn_on 为1

- 走该代理的所有请求都会进行联网查询，不想联网请使用原始的url进行访问。

##### 有新的需求，欢迎大家提issue进行讨论。
