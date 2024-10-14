# dbgpt-tugraph-plugins

Tu Graph插件是DB - GPT中使用的python包。

## 代码目的？

Tu Graph插件使用cpp编写，并编译成动态链接库。该库的目的是将这些插件打包成一个python包，以便于在DB - GPT中安装和使用。


## 如何在python中使用?

1. 首先使用pip安装包：

```bash
pip install dbgpt-tugraph-plugins>=0.1.0rc1 -U -i https://pypi.org/simple
```

2. 然后可以使用python中的插件：

```python
from dbgpt_tugraph_plugins import get_plugin_binary_path

leiden_bin_abs_path = get_plugin_binary_path("leiden") 

print(leiden_bin_abs_path)
```

您将获得 leiden 插件二进制文件的绝对路径。


## 如何构建？

```bash
BUILD_VERSION=0.1.0rc1 make py-package
```

该包将建立在" python / dist "目录中。
