from read_from_db import  read_from_db
from augment_generate import generate_answer
import json
from tqdm import tqdm
from openai import OpenAI

def read_jsonl(file_path):
    """
    从指定的.jsonl文件中读取每一行作为单独的JSON对象。
    
    参数:
        file_path (str): 文件路径。
        
    返回:
        generator: 生成器，每次迭代返回一个JSON对象。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            yield json.loads(line)

def write_jsonl(data, output_file_path):
    """
    将数据写入指定的.jsonl文件中。
    
    参数:
        data (list): 要写入的数据列表。
        output_file_path (str): 输出文件路径。
    """
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(json.dumps(item, ensure_ascii=False) + '\n')

def count_lines_in_jsonl(file_path):
    # 读json文件行数
    line_count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                # 尝试将每一行转换成JSON对象
                json_obj = json.loads(line)
                line_count += 1
            except json.JSONDecodeError:
                # 如果某行不是有效的JSON，则忽略它
                continue
    return line_count

def embed(content, options):
    base_url = options['gpt-baseurl']
    api_key = options['gpt-apikey']
    model = options['embedding-model']
    client = OpenAI(base_url=base_url,
        api_key=api_key)
    response = client.embeddings.create(input=content, model=model).data[0].embedding
    return response

def similarity_score(embedding1, embedding2):
    """
    计算两个嵌入向量的相似度分数。
    
    参数:
        embedding1 (list): 第一个嵌入向量。
        embedding2 (list): 第二个嵌入向量。
        
    返回:
        float: 相似度分数。
    """
    dot_product = sum(e1 * e2 for e1, e2 in zip(embedding1,embedding2))
    return dot_product

def get_score(options):
    val_path = options['val_path'] 
    ans_path = options['val_out_path'] 
    f_len = count_lines_in_jsonl(val_path)
    val_json = []
    ans_json = []
    for obj in read_jsonl(val_path):
        val_json.append(obj)
    for obj in read_jsonl(ans_path):
        ans_json.append(obj)
    print("Embedding and Score Calculating...")
    output = []
    with tqdm(total=f_len) as pbar:
        for i in range(f_len):
            val_embedding = embed(val_json[i]['output_field'], options=options)
            ans_embedding = embed(ans_json[i]['output_field'], options=options)
            score = similarity_score(val_embedding, ans_embedding)
            obj=dict()
            obj['id'] = val_json[i]['id']
            obj['score'] = score
            obj['correct_answer'] = val_json[i]['output_field']
            obj['our_answer'] = ans_json[i]['output_field']
            output.append(obj)
            pbar.update(1)
    return output







