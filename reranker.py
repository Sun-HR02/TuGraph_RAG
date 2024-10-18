from FlagEmbedding import FlagReranker
from sentence_transformers import SentenceTransformer

def rerank(query, knowledges, options): # 用CrossEncoder做rerank
    k = options['k_rerank']
    cut_off = options['cut_off']
    reranker = FlagReranker(options['reranker_model'], use_fp16=True) 
    # 对每个知识再计算相似性得分
    sort_knowledge = []
    for knowledge in knowledges:
        # 保存下每个知识和对应的相似得分
        sort_knowledge.append(dict(score = reranker.compute_score([query, knowledge.page_content[:1024]],normalize=True), knowledge=knowledge)) # 由于reranker使用1024token微调，所以只根据前1024做得分估计
    # 按得分排序, desc
    sort_knowledge = sorted(sort_knowledge, key= lambda i:i['score'], reverse=True)
    t = 0
    for i in range(k):
        knowledges[i] = sort_knowledge[i]['knowledge']
        if sort_knowledge[i]['score'][0] >= cut_off: #当前知识不会被舍弃
            t += 1
    # 只返回前K个结果
    return knowledges[:t]

# def rerank(query, knowledges, options): # 用Bi-Encoder做rerank
#     k = options['k_rerank']
#     cut_off = options['cut_off']
#     model = SentenceTransformer(options['reranker_model'])
#     # 对每个知识再计算相似性得分
#     sort_knowledge = []
#     for knowledge in knowledges:
#         # 保存下每个知识和对应的相似得分
#         sort_knowledge.append(dict(score = (model.encode(query,normalize_embeddings=True) @ model.encode(knowledge.page_content,normalize_embeddings=True).T), knowledge=knowledge)) # 由于reranker使用1024token微调，所以只根据前1024做得分估计
#     # 按得分排序, desc
#     sort_knowledge = sorted(sort_knowledge, key= lambda i:i['score'], reverse=True)
#     t = 0
#     for i in range(k):
#         knowledges[i] = sort_knowledge[i]['knowledge']
#         if sort_knowledge[i]['score'] >= cut_off: #当前知识不会被舍弃
#             t += 1
#     # 只返回前K个结果
#     return knowledges[:t]



