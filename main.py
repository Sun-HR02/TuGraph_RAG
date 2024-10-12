from read_from_db import  read_from_db
from augment_generate import generate_answer
import json
from tqdm import tqdm
from score import get_score
import csv

options = dict()
# 可能影响性能
options['k'] = 3
options['system_prompt'] = '你是一个蚂蚁集团的TuGraph数据库专家，\
                            擅长使用TuGraph数据库的相关知识来回答用户的问题，\
                            针对用户的提问，你会得到一些知识辅助，请忽略没有帮助的知识，\
                            结合有用的部分以及你的知识，尽可能简洁地直接给出答案，不需要任何解释。\
                            注意：问题中的数据库一律指代TuGraph,如果遇到不清楚的问题，请直接回答不知道。'
options['chat-model'] = "gpt-4o-mini"
options['embedding-model'] = "text-embedding-3-large"
# gpt调用
options['gpt-baseurl'] = 'https://api.gptapi.us/v1'
options['gpt-apikey'] = "sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3"
# 文件路径
options['persist_directory'] = './db/xldatabase/rag'
options['test_path'] = './test/test1.jsonl' 
options['val_path'] = './test/val.jsonl'
# 输出路径
options['test_out_path'] = './result/answer_test.jsonl' 
options['val_out_path'] = './result/answer_val.jsonl'
options['score_path'] = './result/score.csv'
# 功能开启，1表示开启
options['use_val'] = 0
options['use_val_score'] = 1
options['use_test'] = 0


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

def write_csv(score_output, file_path):
    # 确定表头（即字典的键）
    if score_output:
        fieldnames = score_output[0].keys()
    else:
        fieldnames = []

    # 打开CSV文件
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # 创建一个DictWriter对象
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 写入表头
        writer.writeheader()
        # 写入数据行
        writer.writerows(score_output)

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


if options['use_val']:
    print('正在对 val.jsonl 进行生成检索.....')
    f_len = count_lines_in_jsonl(options['val_path'])
    answers_val = []
    with tqdm(total=f_len) as pbar:
        for obj in read_jsonl(options['val_path']):
            query = obj.get('input_field')
            knowledge = read_from_db(query, options['k'], options)
            out = dict()
            out['id'] = obj.get('id')
            out['output_field'] = generate_answer(query, knowledge, options)
            answers_val.append(out)
            pbar.update(1)

    write_jsonl(answers_val, options['val_out_path'] )

if options['use_val_score']:
    print('正在计算分数.....')
    score_output = get_score(options)
    write_csv(score_output, options['score_path'])
    # write_jsonl(score_output, options['score_path'])

if options['use_test']:
    print('正在对 test1.jsonl 进行生成检索.....')
    f_len = count_lines_in_jsonl(options['test_path'])
    answers_test = []
    with tqdm(total=f_len) as pbar:
        for obj in read_jsonl(options['test_path']):
            query = obj.get('input_field')
            knowledge = read_from_db(query, options['k'], options)
            out = dict()
            out['id'] = obj.get('id')
            out['output_field'] = generate_answer(query, knowledge, options)
            answers_test.append(out)
            pbar.update(1)

    write_jsonl(answers_test, options['test_out_path'])



