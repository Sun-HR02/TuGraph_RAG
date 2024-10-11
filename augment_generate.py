import json
from openai import OpenAI
from tqdm import tqdm


num=0

def get_gpt_response_w_system(prompt, options):
    global system_prompt
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['chat-model']
    try:
        client = OpenAI(
        base_url=base_url,
        api_key=api_key
        )
        completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": '你是一个问答助手，需要为用户解答关于TuGraph数据库的相关知识，并且你会得到一些知识辅助，请忽略没有帮助的知识，结合有用的部分以及你的知识，给出合适答案。'},
        {"role": "user", "content": prompt}
        ]
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(e)
        return content

def knowledge2str(knowledge):
    knowledgeStr = ''
    for document in knowledge:
        meta = document.metadata
        header_nums = len(meta)
        header_content_cat = ''
        for i in range(header_nums):
            header_content = meta[f'Header {i+1}']
            # 可能对每一个header，把数字编号去掉更好? 数字编号比如1., 2.切分后就没有意义了
            header_content_cat += header_content
            header_content_cat += '--'
        knowledgeStr = header_content_cat + document.page_content
    return knowledgeStr


def generate_answer(query, knowledge, options):
    prompt = ""
    prompt = query
    prompt += '你可能会用到以下知识：'
    prompt += knowledge2str(knowledge)
    # with open(sys_path, 'r') as f:
    #     for line in f.readlines():
    #         system_prompt += line

    # retrieval_prompt = ""
    # with open(aug_path, 'r') as f:
    #     for line in f.readlines():
    #         retrieval_prompt += line

    response = get_gpt_response_w_system(prompt, options)
    return response
