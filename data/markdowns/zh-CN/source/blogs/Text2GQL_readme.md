# Awesome-Text2GQL

这是 text2GQL 生成器实现的存储库。Awesome-Text2GQL 旨在生成密码/gqls 和相应的提示，作为大语言模型（LLM）微调的训练语料库。基于 TuGraph-DB，训练语料库有助于训练适合 TuGraph-DB 查询引擎功能的 Text2GQL 和 Text2Cypher 模型。


## 快速开始

### 环境

对于 Linux，推荐使用 miniconda 来管理您的 Python 环境，同时其他工具也可能有效。

```
git clone https://github.com/TuGraph-contrib/Awesome-Text2GQL
cd Awesome-Text2GQL
mkdir output
conda create --name text2gql python=3.10 
conda activate text2gql
```

安装相关的python依赖包

```
pip install .
```

### 为LLM设置

要运行基于LLMs的生成问题和概括功能，请在运行整个流程之前应用API-KEY。

1. 使用 API-KEY

我们构建了基于Aliyvn提供的Qwen推理服务的语料库泛化模块，您可以参考[Aliyvn](https://help.aliyun.com/zh/dashscope/developer-reference/acquisition-and-configuration-of-api-key?spm=a2c4g.11186623.0.0.4e202a9dXlz5vH#1e6311202fthe)来申请API-KEY。

2. 通过环境变量设置API-KEY（推荐）

```
# replace YOUR_DASHSCOPE_API_KEY with your API-KEY
echo "export DASHSCOPE_API_KEY='YOUR_DASHSCOPE_API_KEY'" >> ~/.bashrc
source ~/.bashrc
echo $DASHSCOPE_API_KEY
```

### 运行整个流程

确保您已完成上述准备工作。要体验推荐的整个流程，您可以运行如下：

```
sh ./scripts/run_the_whole_flow.sh
```

以下步骤将按顺序执行：

- 通过生成模块基于Antlr4以模板为输入生成密码。

- 通过基于LLMs的概括模块生成问题，以上一步生成的密码为输入。

- 通过基于LLMs的概括模块概括上一步生成的问题。

- 将上述生成的语料库转换为模型训练格式。

## 分别运行各部分

### Cypher生成

```
sh ./scripts/gen_query.sh
```

语料生成模块可以运行在两种模式下，即通过实例化器生成查询，或通过翻译器生成问题。

设置 `GEN_QUERY=true` 可根据模板批量生成查询。

### 问题生成

1. 根据LLMs生成问题，并以模板作为附加输入（推荐）

```
sh ./scripts/gen_question_with_template_llm.sh
```

2. 根据LLMs生成问题而不需要模板作为输入。它有助于生成最初没有对应模板的问题。

```
sh ./scripts/gen_question_directly_llm.sh
```

3. 基于Antlr4（已弃用）生成问题

将 `GEN_QUERY=false` 设置为使用生成模块的翻译器根据 Antlr4 生成问题。

```
sh ./scripts/gen_question.sh
```

### 语料库泛化

1. 使用查询和问题作为输入泛化语料库（推荐）

```
sh ./scripts/generalize_llm.sh
```

2. 泛化无查询的问题（已弃用）

```
sh ./scripts/general_questions_directly_llm.sh
```

### 转换

将上述生成的语料转换为模型训练格式。

```
sh ./scripts/generate_dataset.sh
```

