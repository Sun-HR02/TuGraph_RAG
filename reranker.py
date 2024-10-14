from FlagEmbedding import FlagReranker

def rerank(query, knowledges, options):
    k = options['k_rerank']
    reranker = FlagReranker(options['reranker_model'], use_fp16=True) 
    # 对每个知识再计算相似性得分
    sort_knowledge = []
    for knowledge in knowledges:
        # 保存下每个知识和对应的相似得分
        sort_knowledge.append(dict(score = reranker.compute_score([query, knowledge.page_content[:1024]]), knowledge=knowledge)) # 由于reranker使用1024token微调，所以只根据前1024做得分估计
    # 按得分排序, desc
    sort_knowledge = sorted(sort_knowledge, key= lambda i:i['score'], reverse=True)
    for i in range(k):
        knowledges[i] = sort_knowledge[i]['knowledge']
    # 只返回前K个结果
    return knowledges[:k]





