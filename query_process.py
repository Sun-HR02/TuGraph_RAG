from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForCausalLM
# 用大模型把复杂query拆分为多个子查询
def split_query(prompt, options):
    global system_prompt 
    s_prompt = options['query_process_prompt']
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['chat-model']
    temperature = options['temperature']
    is_api = options['is_api']
    if is_api:
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
            questions = [q.strip() for q in content.split('\n') if q.strip()]
            return questions
        except Exception as e:
            print(e)
            return content
    else:
        model_path = options['chat-model']
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        inputs = tokenizer(s_prompt + prompt, return_tensors="pt")
        generate_ids = model.generate(inputs.input_ids, max_length=30)
        return tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

def rewrite_query(prompt, options):
    global system_prompt 
    s_prompt = options['query_write_prompt']
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['chat-model']
    temperature = options['temperature']
    is_api = options['is_api']
    if is_api:
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
    else:
        model_path = options['chat-model']
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        inputs = tokenizer(s_prompt + prompt, return_tensors="pt")
        generate_ids = model.generate(inputs.input_ids, max_length=30)
        return tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0] 

def combine_answers(query, answers, options):
    global system_prompt 
    s_prompt = options['system_prompt']
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['chat-model']
    temperature = options['temperature']
    is_api = options['is_api']
    prompt = query + '以下是辅助文本： '+ answers
    if is_api:
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
    else:
        model_path = options['chat-model']
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        inputs = tokenizer(s_prompt+prompt, return_tensors="pt")
        generate_ids = model.generate(inputs.input_ids, max_length=30)
        return tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

