import os
import json
import csv
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

def write_csv(score_output, file_path): # score_output实际是要写到csv的数据
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

def calculate_avg(socres):
    sum = 0.0
    for score in socres:
        sum += score['score']
    return sum / len(socres)
