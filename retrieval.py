from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter
from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('../bert-base-chinese')
model = BertModel.from_pretrained('../bert-base-chinese',ignore_mismatched_sizes=True)

def embed(content):
    inputs = tokenizer(content, return_tensors="pt", padding=True, truncation=True)
    # 通过模型前向传递来获取编码
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 获取最后隐藏状态（用于文本编码）
    last_hidden_states = outputs.last_hidden_state
    
    # 拼接[CLS]标记和最后一个标记的向量
    cls_embedding = last_hidden_states[:, 0, :]  # 第一个token的输出
    last_token_embedding = last_hidden_states[:, -1, :]  # 最后一个token的输出
    combined_embedding = torch.cat((cls_embedding, last_token_embedding), dim=1)
    
    # 打印和返回新的维度

    return combined_embedding[0].tolist()

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

# 读取Markdown文件的内容, 先用一个文档作为例子
with open('./data/markdowns/zh-CN/source/2.introduction/4.schema.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 分块粒度
headers_to_split_on = [
("#", "Header 1"),
("##", "Header 2"),
("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
headers_to_split_on)

md_header_splits = markdown_splitter.split_text(
content)

# 存入向量数据库
vectordb_chinese = Chroma.from_documents(
    documents=md_header_splits,
    embedding=ErnieEmbeddingFunction(),
    persist_directory=persist_directory_chinese  # 允许我们将persist_directory目录保存到磁盘上
)

