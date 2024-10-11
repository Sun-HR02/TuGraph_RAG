from read_from_db import  read_from_db
from augment_generate import generate_answer


options = dict()
options['k'] = 3
options['gpt-baseurl'] = 'https://api.gptapi.us/v1'
options['gpt-apikey'] = "sk-xfovpV3O7IwdmDDJBb05Ff03E5014c14Ab5e935715Fe90D3"
options['embedding-model'] = "text-embedding-ada-002"
options['chat-model'] = "gpt-4o-mini"
options['persist_directory'] = './db/xldatabase/rag'


print('print your question here: ')

query = input()
# 检索
knowledge = read_from_db(query, options['k'], options)
# 增强生成
response = generate_answer(query, knowledge, options)

print(response)