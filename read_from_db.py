from langchain_chroma import Chroma
from retrieval import ErnieEmbeddingFunction
from retrieval import persist_directory_chinese


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
retriever = vectordb_chinese.similarity_search(query, k=5)
print(retriever)