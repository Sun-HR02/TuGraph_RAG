from read_from_db import  read_from_db
from augment_generate import generate_answer
import json
from tqdm import tqdm

options = dict()
options['k'] = 5
options['gpt-baseurl'] = 'https://api.gptapi.us/v1'
options['gpt-apikey'] = "sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3"
options['embedding-model'] = "text-embedding-ada-002"
options['chat-model'] = "gpt-4o-mini"
options['persist_directory'] = './db/xldatabase/rag'
options['f_path'] = './test/test1.jsonl' # 输入文件路径
options['answer_path'] = './output' # 回答输出路径




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


f_path = options['f_path']
f_len = count_lines_in_jsonl(f_path)

# 调用函数
answers = []
with tqdm(total=f_len) as pbar:
    for obj in read_jsonl(f_path):
        query = obj.get('input_field')
        knowledge = read_from_db(query, options['k'], options)
        out = dict()
        out['id'] = obj.get('id')
        out['output_field'] = generate_answer(query, knowledge, options)
        answers.append(out)
        pbar.update(1)

write_jsonl(answers, options['answer_path'] + '/answer.jsonl')
