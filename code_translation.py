import pickle
from openai import OpenAI
from langchain_core.documents import Document

def read_src_code(repo_path):
    global counter
    print('Reading src code...')
    with open(repo_path,'rb') as f:
        repo_documents = pickle.load(f)
    # repo[i].text取出代码片段, repo[i].metadata['file_path']得到文件路径,repo[i].metadata['file_name]得到文件名
    repo_knowledges = []
    print('共 {} 块'.format(len(repo_documents)))
    for i in range(len(repo_documents)):
        counter += 1
        print(counter, '块翻译中....')
        document = Document(
                page_content=get_gpt_response_w_system(repo_documents[i].metadata['file_path']+'/ '+repo_documents[i].text),
                metadata=repo_documents[i].metadata
            )
        repo_knowledges.append(document)
    print('Reading src code done!')
    return repo_knowledges

def get_gpt_response_w_system(prompt):
    global system_prompt 
    s_prompt = '你是一个代码阅读专家，阅读给定代码碎片，给出代码相应功能的解释。对于函数定义、函数声明和函数调用，解释使用的参数和返回值。'
    base_url = 'https://api.gptapi.us/v1'
    api_key = "sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3"
    model = 'gpt-4o-mini'
    temperature = 0.1
    try:
        client = OpenAI(
        base_url=base_url,
        api_key=api_key
        )
        completion = client.chat.completions.create(
        temperature= temperature,
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

repo_path = '../repo.pickle'
counter = 0
processed = read_src_code(repo_path)
with open('./repo_processed.pickle','wb') as f:
    pickle.dump(processed,f)
