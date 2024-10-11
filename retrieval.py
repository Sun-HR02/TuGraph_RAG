from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter
from transformers import BertTokenizer, BertModel
import torch
from openai import OpenAI

import os
from pathlib import Path

# tokenizer = BertTokenizer.from_pretrained('../bert-base-chinese')
# model = BertModel.from_pretrained('../bert-base-chinese',ignore_mismatched_sizes=True)

markdown_files_path = './data/markdowns/zh-CN/source'

def embed(content):
    client = OpenAI(base_url="https://api.gptapi.us/v1/chat/completions",
        api_key="sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3")
    response = client.embeddings.create(input=content, model="text-embedding-ada-002").data[0].embedding
    return response

#  def embed(content):
    # inputs = tokenizer(content, return_tensors="pt", padding=True, truncation=True)
    # # 通过模型前向传递来获取编码
    # with torch.no_grad():
    #     outputs = model(**inputs)
    
    # # 获取最后隐藏状态（用于文本编码）
    # last_hidden_states = outputs.last_hidden_state
    
    # # 拼接[CLS]标记和最后一个标记的向量
    # cls_embedding = last_hidden_states[:, 0, :]  # 第一个token的输出
    # last_token_embedding = last_hidden_states[:, -1, :]  # 最后一个token的输出
    # combined_embedding = torch.cat((cls_embedding, last_token_embedding), dim=1)
    
    # # 打印和返回新的维度

    # return combined_embedding[0].tolist()

class ErnieEmbeddingFunction(EmbeddingFunction): 
    def embed_documents(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            response = embed(text)
            try:
                embedding = response 
                embeddings.append(embedding)
            except (IndexError, TypeError, KeyError) as e:
                print(f"Error processing text: {text}, Error: {e}")
        return embeddings
    def embed_query(self, input) -> Embeddings:
        response = embed(input)
        try:
            embedding = response 
        except (IndexError, TypeError, KeyError) as e:
            print(f"Error processing text: {input}, Error: {e}")
        return embedding

#向量数据库存储地方
persist_directory_chinese = "./db/xldatabase/rag"

# 分块粒度
headers_to_split_on = [
("#", "Header 1"),
("##", "Header 2"),
("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
headers_to_split_on)


# 读取指定路径下的所有 Markdown 文件，并保留文件夹结构信息
def read_markdown_files(markdown_files_path):
    print('Reading markdown files...')
    markdown_knowledge = []
    filepaths = []
    # 遍历指定路径下的所有文件和文件夹
    for root, dirs, files in os.walk(markdown_files_path,topdown=True):
        for file in files:
            if file.endswith('.md'):
                file_path = Path(root) / file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    '''
                    md_header_splits是一个由多个documents对象组成的list，
                    每个documents有metadata(是一个dict，用'Header 1','Header 2'等访问对应标题段)，以及page_content(正文部分)
                    '''
                    markdown_header_splits = markdown_splitter.split_text(content)
                    # markdown_knowledge += markdown_header_splits

                    # 一点改进思路
                    for document in markdown_header_splits:
                        meta = document.metadata
                        header_nums = len(meta)
                        if header_nums == 1:
                            continue
                        header_content_cat = ''
                        for i in range(header_nums):
                            header_content = meta[f'Header {i+1}']
                            # 可能对每一个header，把数字编号去掉更好? 数字编号比如1., 2.切分后就没有意义了
                            header_content_cat += header_content
                            header_content_cat += '\n\n'
                        # document.page_content = header_content_cat + document.page_content
                        markdown_knowledge.append(document)
    print('Reading markdown files done!')
    return markdown_knowledge

markdown_knowledge = read_markdown_files(markdown_files_path)


# markdown_knowledge = []
# # 读取Markdown文件的内容, 先用一个文档作为例子
# with open('./data/markdowns/zh-CN/source/2.introduction/4.schema.md', 'r', encoding='utf-8') as f:
#     content = f.read()
# md_header_splits = markdown_splitter.split_text(
# content)
# markdown_knowledge += md_header_splits


# 存入向量数据库
vectordb_chinese = Chroma.from_documents(
    documents = markdown_knowledge,
    embedding=ErnieEmbeddingFunction(),
    persist_directory=persist_directory_chinese  # 允许我们将persist_directory目录保存到磁盘上
)

