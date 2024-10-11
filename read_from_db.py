from langchain_chroma import Chroma
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter
from transformers import BertTokenizer, BertModel
import torch
from openai import OpenAI

import os
from pathlib import Path

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

def embed(content):
    client = OpenAI(base_url="https://api.gptapi.us/v1",
        api_key="sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3")
    response = client.embeddings.create(input=content, model="text-embedding-ada-002").data[0].embedding
    return response

#向量数据库存储地方
persist_directory_chinese = "./db/xldatabase/rag"
# 读取向量数据库，读的时候已经存在本地了，就把上面的注释掉直接运行这一段就好


# 读取向量数据库，读的时候已经存在本地了，就把上面的注释掉直接运行这一段就好

vectordb_chinese = Chroma(
    persist_directory=persist_directory_chinese,
    embedding_function=ErnieEmbeddingFunction()
)

# 查看向量数据库元素
# all_data = vectordb_chinese.get()
# all_vectors = all_data['embeddings']
# all_metadatas = all_data['metadatas']
# all_document=all_data['documents']
# all_ids = all_data['ids']

# 检索
# query="给我大概介绍一下TuGraph图模型"
query="介绍下Docker部署"
retriever = vectordb_chinese.similarity_search(query, k=3)
print(retriever)