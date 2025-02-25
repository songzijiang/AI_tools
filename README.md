# AI_tools
一个AI代理脚本，可以用来转发AI请求，并添加联网功能，让离线AI支持联网搜索。本脚本仅支持searxNG搜索，默认使用谷歌搜索。其他搜索引擎请和设置自行更改searxng_search中的preferences参数

searxng_url:为searxng服务器地址，部署参考[这里](https://github.com/searxng/searxng)。setting.xml中记得添加支持json格式

target_server:为原始的模型地址

使用方法：
```
git clone https://github.com/songzijiang/AI_tools.git
cd AI_tools
export ait_searxng_url=http://ip1:port
export ait_target_server=http://ip2:port
pip install flask
pip install requests
```

启动服务：`python web_proxy.py`

### 运行以后，原本访问http://ip2:port , 现在只需要把模型url改成http://本机IP:5000 就能实现联网搜索
### 网页检索未加入RAG，仅返回基础信息，更深一步的RAG查询可以完善searxng_search函数
### windows请使用
```
set ait_searxng_url=http://localhost:9000
set ait_target_server=https://api.siliconflow.cn
```
走该代理的所有请求都会进行联网查询，不想联网请使用原始的url进行访问。