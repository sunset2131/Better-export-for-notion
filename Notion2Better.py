import os
import re
import shutil
import urllib.parse
import argparse
from datetime import datetime

# 获取当前日期
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 正则表达式匹配图片路径
image_pattern = re.compile(r"!\[.*?\]\((?!http)(.*?)\)")


def update_yaml_header(file_path, filename, prefix, tags, category, image_flag):
    """更新 markdown 文件头部"""
    # 去除文件名中的 MD5 值
    title = re.sub(r'\s[0-9a-fA-F]{32}$', '', filename.rsplit('.', 1)[0])
    if prefix:
        title = f"{prefix}-{title}"

    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 如果 image_flag 为 true，则尝试获取文档中第一张图片的名称
    image_line = ""
    if image_flag:
        images = image_pattern.findall(content)
        if images:
            first_image = urllib.parse.unquote(images[0])
            first_image_basename = os.path.basename(first_image)
            image_line = f"image: \"./{first_image_basename}\""

    # 构造 YAML 头部，根据是否添加 image 字段来生成
    yaml_header = f"""---
title: {title}
published: {current_date}
{image_line}
tags: {tags}
category: {category}
draft: false
---"""

    # 只在没有 YAML 头部时才插入
    if not content.startswith("---\n"):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(yaml_header + "\n" + content)
        print(f"✅ Updated: {file_path}")
    else:
        print(f"⏭ Skipped (already has YAML header): {file_path}")


def move_files_and_images(file_path, folder_target, folder_path):
    """移动 .md 文件及其图片到目标文件夹"""
    os.makedirs(folder_target, exist_ok=True)
    with open(file_path, "r", encoding="utf-8") as md_file:
        content = md_file.read()
        images = image_pattern.findall(content)
    shutil.move(file_path, os.path.join(folder_target, os.path.basename(file_path)))
    print(f"📄 Moved: {file_path} -> {folder_target}/")
    for img_path in images:
        decoded_img_path = urllib.parse.unquote(img_path)
        img_full_path = os.path.join(folder_path, decoded_img_path)
        if os.path.exists(img_full_path) and os.path.isfile(img_full_path):
            img_new_path = os.path.join(folder_target, os.path.basename(decoded_img_path))
            shutil.move(img_full_path, img_new_path)
            print(f"  ✅ Moved: {decoded_img_path} -> {folder_target}/")
        else:
            print(f"  ❌ Image not found: {decoded_img_path}")


def process_markdown_files(folder_path, prefix, tags, category, image_flag):
    """处理文件夹中的所有 .md 文件"""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith(".md"):
            new_filename = re.sub(r'\s[0-9a-fA-F]{32}\.md$', '.md', filename)
            new_folder_name = f"{prefix}-{new_filename[:-3]}" if prefix else new_filename[:-3]
            new_folder_path = os.path.join(folder_path, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)

            # 更新 YAML 头部并传入 image_flag 参数
            update_yaml_header(file_path, filename, prefix, tags, category, image_flag)
            move_files_and_images(file_path, new_folder_path, folder_path)
            new_md_path = os.path.join(new_folder_path, "index.md")
            os.rename(os.path.join(new_folder_path, filename), new_md_path)
            print(f"📝 Renamed: {filename} -> index.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize exported Notion resources")
    parser.add_argument("--folder_path", required=True, help="The folder path where markdown files are located.")
    parser.add_argument("--prefix", default="", help="(Optional) Prefix to be added to the title.")
    parser.add_argument("--tags", required=True, help="Tags for the markdown files.")
    parser.add_argument("--category", required=True, help="Category for the markdown files.")
    parser.add_argument("--image", choices=["true", "false"], default="false",
                        help="Whether to add the first image in the folder to the YAML header (true/false).")
    args = parser.parse_args()
    image_flag = True if args.image.lower() == "true" else False
    process_markdown_files(args.folder_path, args.prefix, args.tags, args.category, image_flag)
