# Better-import-for-notion
## 作用
对Notion导出的内容进行优化，对文件重命名，将图片和md文件放在单独文件夹，并添加YAML头部，以便导入博客
## usage
```
D:\All\BlogUsePy>python Notion2Better.py -h
usage: Notion2Fu.py [-h] --folder_path FOLDER_PATH [--prefix PREFIX] --tags TAGS --category CATEGORY

Process Markdown files for HackTheBox blog.

options:
  -h, --help            show this help message and exit
  --folder_path FOLDER_PATH
                        The folder path where markdown files are located.
  --prefix PREFIX       (Optional) Prefix to be added to the title.
  --tags TAGS           Tags for the markdown files.
  --category CATEGORY   Category for the markdown files.
```
## example
```
python Notion2Fu.py --prefix Vulnhub --tags [Vulnhub] --category 靶机 --folder_path "D:\System\Downloads\new-blog-test\vulnhub"
```

## 改善对Notion导出后的处理
默认导出不做任何处理：
![image](https://github.com/user-attachments/assets/3d2bb854-16b3-4fd1-8f60-a4f2831d3a8e)

使用`Notion2Better.py`做处理后：
![image](https://github.com/user-attachments/assets/ea73a992-b80a-4d3c-a0cf-bac960cde210)

使用Notion2Better.py处理过后添加的YAML头部：
```
---
title: Vulnhub-billu： b0x
published: 2025-03-09
tags: [Vulnhub]
category: 靶机
draft: false
---
```
## 二次开发
工具内容很简单，直接修改即可
