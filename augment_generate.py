import json
from openai import OpenAI
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from query_process import split_query



num=0

def get_gpt_response_w_system(prompt, options):
    global system_prompt 
    s_prompt = options['system_prompt']
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['chat-model']
    temperature = options['temperature']
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

def knowledge2str(knowledge, tokens_per_knowledge):
    knowledgeStr = ''
    for document in knowledge:
        meta = document.metadata
        if(len(document.page_content) > tokens_per_knowledge):
            document.page_content = document.page_content[:tokens_per_knowledge]
        knowledgeStr +=  document.page_content + ' '
    return knowledgeStr

def get_response_from_llm(prompt, options):
    model_path = options['chat-model']
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    inputs = tokenizer(prompt, return_tensors="pt")
    generate_ids = model.generate(inputs.input_ids, max_length=30)
    return tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

def generate_answer(query, knowledge, options):  
    prompt = ""
    prompt = query
    is_api = options['is_api']
    # 修改知识添加
    prompt += '以下是辅助文本：'
    prompt += knowledge2str(knowledge,options['tokens_per_knowledge'] )
    if is_api:
        response = get_gpt_response_w_system(prompt, options)
    else :
        response = get_response_from_llm(prompt,options)

    return response
