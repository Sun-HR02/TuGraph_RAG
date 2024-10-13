# 忧郁的龙卷风

>
>忧郁的龙卷风卷啊卷，
>职场漩涡深不见底。
>
>人人争做加班狂徒，
>名利场中竞相逐利。
>
>创新之名行旧套路，
>才华尽耗于内卷戏。
>
>何时能见晴空万里，
>莫让心灵再蒙尘翳。




## Project Structure

`data/`: 存储了原始知识文档

`result/`: 包含模型输出的问题答案，以及针对`val.jsonl`给出评分结果

`test/` ：存储了测试用文件，其中`val.jsonl`包含了正确答案，`test1.jsonl`不包含答案

`augment_generate.py` : 结合向量数据库内容，向大模型提问,使用gpt-4o-mini

`embed.py` : 嵌入功能文件的代码

`main.py` : 使用服务的主代码

`read_from_db.py` :从向量数据库中读取数据和检索

`retrieval.py` :实现markdown文档的分段和嵌入，并且存储到向量数据库当中
- 针对markdown分段，使用langchain根据文档标题段落分段
- 使用BGE-M3进行嵌入得到向量

`score.py` : 评分函数代码

`utils.py` : 工具函数代码

## Quick Start

1. `pip install -r requirements.txt` to install all dependencies.
2. `python retrieval.py` to retrieve the text from the markdown file and store it in the vector database.
3. 修改 `main.py`中的参数，数据库位置要和retrieval中的路径一致。修改测试问题文件以及最终结果输出路径。设置参数选择是否在val、test上运行，以及是否需要打分评估
4. `python main.py`  to start Q&A.

> 在运行`retrieval.py`后，会生成db文件夹用于存储向量数据库，为节约项目大小，已设置不上传github
