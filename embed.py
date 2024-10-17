from openai import OpenAI
from FlagEmbedding import BGEM3FlagModel
from sentence_transformers import SentenceTransformer


# def embed(content, options):
#     base_url = options['gpt-baseurl']
#     api_key = options['gpt-apikey']
#     model = options['embedding-model']
#     client = OpenAI(base_url=base_url,
#         api_key=api_key)
#     response = client.embeddings.create(input=content, model=model).data[0].embedding
#     return response

def embed(content, options): #using bge
    # model = BGEM3FlagModel(options['embedding-model'], use_fp16=True) # BAAI/bge-m3
    model = SentenceTransformer(options['embedding-model'])
    response = model.encode(content)
    # response = model.encode(content, max_length = 8192)['dense_vecs']

    return response