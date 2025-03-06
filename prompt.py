from datetime import datetime


def get_web_search_prompt(prompt, search_results, question):
    cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    search_answer_zh_template = prompt.replace('{search_results}', search_results) \
        .replace('{cur_date}', cur_date).replace('{question}', question)
    return search_answer_zh_template
