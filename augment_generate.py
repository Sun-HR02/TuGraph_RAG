import json
from openai import OpenAI
from tqdm import tqdm


num=0

def get_gpt_response_w_system(prompt):
    global system_prompt
    global right_n
    global num

    try:
        num+=1
        client = OpenAI(
        base_url="https://api.gptapi.us/v1/chat/completions",
        api_key="sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3"
        )
        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
        ]
        )
        content = completion.choices[0].message.content
        return content
    
    except Exception as e:
        num+=1
        print(right_n)
        print(num)
        content = "None"
        return content

# query
sys_path=
# 查询到的知识
aug_path=

system_prompt = ""
with open(sys_path, 'r') as f:
    for line in f.readlines():
        system_prompt += line

retrieval_prompt = ""
with open(aug_path, 'r') as f:
    for line in f.readlines():
        retrieval_prompt += line

response = get_gpt_response_w_system(retrieval_prompt)
