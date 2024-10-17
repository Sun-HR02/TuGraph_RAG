from read_from_db import  read_from_db
from augment_generate import generate_answer
import json
from tqdm import tqdm
from score import get_score
from reranker import rerank
import csv
from utils import write_csv, calculate_avg, count_lines_in_jsonl, write_jsonl, read_jsonl
from query_process import split_query, rewrite_query, combine_answers

options = dict()
# 可能影响性能
options['k'] = 100 # 使用向量相似度检索得到的知识个数
options['k_rerank'] = 5 # 对向量检测后的结果，再次rerank选出最前k_rerank
options['tokens_per_knowledge'] = 2048 # 为防止单个知识过长，进行截断
options['temperature'] = 0.1 # 模型温度，范围0-2
options['system_prompt'] = '你是一个蚂蚁集团的TuGraph数据库专家，\
                            擅长使用与TuGraph数据库相关的知识来回答用户的问题，\
                            针对用户的提问，你会得到一些文本材料辅助回答，如果某些辅助文本与提问关联性不强，则可以忽略，\
                            结合有用的部分以及你的知识，回答用户的提问。如果可以直接给出答案,则只回答最关键的部分,做到尽可能简洁。\
                            注意：问题中的数据库一律指代TuGraph,\
                            请仿照下面的样例答案格式进行后续的回答,给出答案.\
                            样例问题1：RPC 及 HA 服务中，verbose 参数的设置有几个级别？, 样例答案:  三个级别（0，1，2)。 \
                            样例问题2: 如果成功修改一个用户的描述，应返回什么状态码？样例答案：200 '
options['query_process_prompt'] = '请根据输入的问题， 将问题转化为三个子问题，这些子问题分别为解决原问题的一个步骤 .\
                                    比如： \
                                    样例问题："哈莉·奎因和灭霸在《复仇者联盟》中是正义的角色吗？" \
                                    样例答案：“1.哈莉·奎茵在《复仇者联盟》电影中扮演什么角色? \n2.灭霸在《复仇者联盟》电影中扮演什么角色？ ”\
                                    每个问题，都应该能独立查询和回答，不应该有模糊的代词，错误案例："这种情况","这时候”，正确案例：“当指定值缺失时”,"当添加边时"。\
                                '
options['query_write_prompt'] = '请将查询重写为一个完整的问题，以确保其结构清晰，并能够直接被理解为提问。 示例：查询：将关系型数据库数据导入图库重写为：如何将关系型数据库中的数据导入到TuGraph-DB中？ 注意：问题中的数据库一律指代TuGraph'
options['chat-model'] = "gpt-4o-mini" # 用gptapi 可以用gpt-4o-mini, 绝招是用chatgpt-4o-latest
# options['embedding-model'] = "../bge-m3"
options['embedding-model'] = "../Conan-embedding-v1"
options['reranker_model'] = '../bge-reranker-v2-m3'
# gpt调用
options['is_api'] = 1 #用本地大模型做回答就把这个关掉
options['gpt-baseurl'] = 'https://api.gptapi.us/v1'
options['gpt-apikey'] = "sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3"
# 文件路径
options['persist_directory'] = './db/xldatabase/rag'
options['test_path'] = './test/test1.jsonl' 
options['val_path'] = './test/val.jsonl'
# 输出路径
options['test_out_path'] = './result/answer_test.jsonl' 
options['val_out_path'] = './result/answer_val.jsonl'
options['score_path'] = './result/score.csv' # 得分输出
options['retrieval_path'] = './result/retrevial/' # 对检索得到的知识输出
# 功能开启，1表示开启
options['use_val'] = 0
options['use_val_score'] = 0
options['use_test'] = 1
options['save_knowledge'] = 1
options['use_split'] = 0 # 经过测试，效果很差，先不启用
options['use_rewrite'] = 0


if options['use_val']:
    print('正在对 val.jsonl 进行生成检索.....')
    answers_val = []
    if options['save_knowledge']:
        knowledge_val = []
    with tqdm(total=count_lines_in_jsonl(options['val_path'])) as pbar:
        for obj in read_jsonl(options['val_path']):
            query = obj.get('input_field')
            if options['use_rewrite']:
                query = rewrite_query(query, options)
            if options['use_split']:
                questions = split_query(query, options) # 先做问题切分
                # 三个问题分别rag，最后做拼接
                # 生成答案
                knowledges = []
                for question in questions:
                    knowledges += rerank(question,read_from_db(question, options['k'], options),options) #一共是k_rerank^2个知识
                answers_val.append(dict(id=obj.get('id'), output_field = generate_answer(query,knowledges, options)))
            else: 
                if options['save_knowledge']:
                    # 查答案并rerank
                    knowledges = rerank(query,read_from_db(query, options['k'], options),options) # a list of Documents
                    knowledge_val.append(dict(Q = query, K1 = knowledges[0], K2 = knowledges[1], K3 = knowledges[2]))
                    answers_val.append(dict(id=obj.get('id'), output_field = generate_answer(query,knowledges, options)))
                else:
                    answers_val.append(dict(id=obj.get('id'), output_field = generate_answer(query, rerank(query,read_from_db(query, options['k'], options),options), options)))
            pbar.update(1)

    write_jsonl(answers_val, options['val_out_path'] )
    if options['save_knowledge']:
        write_csv(knowledge_val, options['retrieval_path']+ 'retrieval_val.csv')
    print('val.jsonl 已生成答案！\n \n')

if options['use_val_score']:
    print('正在计算分数.....')
    score_output = get_score(options)
    write_csv(score_output, options['score_path'])
    print('分数平均为{}! \n \n'.format(calculate_avg(score_output)))

if options['use_test']:
    print('正在对 test1.jsonl 进行生成检索.....')
    answers_test = []
    if options['save_knowledge']:
        knowledge_test = []
    with tqdm(total=count_lines_in_jsonl(options['test_path'])) as pbar:
        for obj in read_jsonl(options['test_path']):
            query = obj.get('input_field')
            if options['use_rewrite']:
                query = rewrite_query(query, options) 
            if options['use_split']:
                questions = split_query(query, options) # 先做问题切分
                # 三个问题分别rag，最后做拼接
                # 生成答案
                knowledges = []
                answers = ''
                for question in questions:
                    answers += generate_answer(question, rerank(question,read_from_db(question, options['k'], options),options), options)
                    # knowledges += rerank(question,read_from_db(question, options['k'], options),options) #一共是k_rerank^2个知识
                answers_test.append(dict(id=obj.get('id'), output_field = combine_answers(query, answers, options)))
                # answers_val.append(dict(id=obj.get('id'), output_field = generate_answer(query,knowledges, options)))
            else:
                if options['save_knowledge']:
                    knowledges = rerank(query,read_from_db(query, options['k'], options),options) # a list of Documents
                    knowledge_test.append(dict(Q = query, K1 = knowledges[0], K2 = knowledges[1], K3 = knowledges[2]))
                    answers_test.append(dict(id=obj.get('id'), output_field = generate_answer(query,knowledges, options)))
                else:
                # 生成问题答案
                    answers_test.append(dict(id=obj.get('id'), output_field = generate_answer(query, rerank(query,read_from_db(query, options['k'], options),options), options)))
            pbar.update(1)

    write_jsonl(answers_test, options['test_out_path'])
    if options['save_knowledge']:
        write_csv(knowledge_test, options['retrieval_path']+ 'retrieval_test.csv')
    print('test1.jsonl 已生成答案！\n \n')


