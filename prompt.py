from datetime import datetime

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
