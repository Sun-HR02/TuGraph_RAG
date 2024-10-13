import json
from openai import OpenAI
from tqdm import tqdm


num=0

def get_gpt_response_w_system(prompt, options):
    global system_prompt 
    s_prompt = options['system_prompt']
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['chat-model']
    try:
        client = OpenAI(
        base_url=base_url,
        api_key=api_key
        )
        completion = client.chat.completions.create(
        temperature= 0,
        model=model,
        messages=[
        {"role": "system", "content": s_prompt},
        {"role": "user", "content": prompt}
        ]
        )
        content = completion.choices[0].message.content
        return content
    except Exception as e:
        print(e)
        return content

def knowledge2str(knowledge, tokens_per_knowledge):
    knowledgeStr = ''
    for document in knowledge:
        meta = document.metadata
        header_nums = len(meta)
        header_content_cat = '-'
        if(len(document.page_content) > tokens_per_knowledge):
            document.page_content = document.page_content[:tokens_per_knowledge]
        # print(knowledge)
        # for i in range(header_nums):
        #     header_content = meta[f'Header {i+1}']
        #     # 可能对每一个header，把数字编号去掉更好? 数字编号比如1., 2.切分后就没有意义了
        #     header_content_cat += header_content
        #     header_content_cat += '--'
        knowledgeStr = header_content_cat + document.page_content
    return knowledgeStr


def generate_answer(query, knowledge, options):  
    prompt = ""
    prompt = query
    # 修改知识添加
    prompt += '以下是辅助文本：'
    prompt += knowledge2str(knowledge,options['tokens_per_knowledge'] )

    response = get_gpt_response_w_system(prompt, options)
    return response
