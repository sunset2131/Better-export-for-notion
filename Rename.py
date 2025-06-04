import os
import argparse
import re
import shutil
import time
import yaml

def rename_png_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".png") and (" " in filename or "%20" in filename):
            new_filename = filename.replace(" ", "").replace("%20", "")
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            os.rename(old_path, new_path)
            print(f"已重命名: {filename} -> {new_filename}")

def update_md_files(folder_path, img_dir=None):
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            md_name = os.path.splitext(filename)[0]  # 获取 Markdown 文件名（不含扩展名）
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            pattern = r'!\[(.*?)\]\((.*?)\)'
            matches = re.findall(pattern, content)

            updated = False
            new_content = content
            
            for alt_text, img_path in matches:
                # 首先处理路径中的空格和%20
                if ' ' in img_path or '%20' in img_path:
                    new_path = img_path.replace(' ', '').replace('%20', '')
                    new_content = new_content.replace(f"![{alt_text}]({img_path})", f"![{alt_text}]({new_path})")
                    img_path = new_path  # 更新img_path以供后续使用
                    updated = True
                
                # 如果提供了img_dir参数，修改为绝对路径
                if img_dir:
                    # 确保img_dir的格式正确，开头有/，结尾没有/
                    img_dir = img_dir.rstrip('/')
                    if not img_dir.startswith('/'):
                        img_dir = '/' + img_dir
                    
                    # 获取图片文件名
                    img_name = os.path.basename(img_path)
                    # 替换md_name中的空格为%20，确保URL正确
                    folder_name = md_name.replace(' ', '%20')
                    # 构建新的图片路径
                    new_img_path = f"{img_dir}/{folder_name}/{img_name}"
                    # 替换原始图片路径
                    new_content = new_content.replace(f"![{alt_text}]({img_path})", f"![{alt_text}]({new_img_path})")
                    updated = True

            if updated:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"已更新图片路径: {filename}")

def clean_md_filenames(folder_path, prefix):
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            name, ext = os.path.splitext(filename)
            pattern = r'[0-9a-fA-F]{32}'  # MD5 校验码的正则表达式
            match = re.search(pattern, name)
            if match:
                # 去掉MD5并在文件名前加上prefix
                new_name = prefix + name[:match.start()].rstrip() + ext
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_name)
                
                # 检查目标文件是否已存在
                if os.path.exists(new_path):
                    print(f"警告: 目标文件已存在: {new_name}")
                    # 创建唯一的文件名，添加递增数字
                    base_name = os.path.splitext(new_name)[0]
                    counter = 1
                    while os.path.exists(new_path):
                        new_name = f"{base_name}_{counter}{ext}"
                        new_path = os.path.join(folder_path, new_name)
                        counter += 1
                    print(f"使用替代名称: {new_name}")
                
                os.rename(old_path, new_path)
                print(f"已清理: {filename} -> {new_name}")

def move_md_images(folder_path, prefix, img_dir=None):
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            md_name = os.path.splitext(filename)[0]  # 获取 Markdown 文件名（不含扩展名）
            md_path = os.path.join(folder_path, filename)
            img_folder = os.path.join(folder_path, md_name)  # 直接使用 md_name 创建文件夹

            if not os.path.exists(img_folder):
                os.makedirs(img_folder)
                print(f"创建文件夹: {img_folder}")

            with open(md_path, 'r', encoding='utf-8') as file:
                content = file.read()

            pattern = r'!\[(.*?)\]\((.*?)\)'  # 匹配 Markdown 中的图片 [alt](path)
            matches = re.findall(pattern, content)

            for alt_text, img_path in matches:
                # 获取图片名称
                img_name = os.path.basename(img_path)
                old_img_path = os.path.join(folder_path, img_name)
                new_img_path = os.path.join(img_folder, img_name)

                if os.path.exists(old_img_path):
                    # 检查目标文件是否已存在
                    if os.path.exists(new_img_path):
                        print(f"警告: 目标图片已存在: {new_img_path}")
                        # 创建不覆盖的文件名
                        name, ext = os.path.splitext(img_name)
                        counter = 1
                        while os.path.exists(new_img_path):
                            new_img_name = f"{name}_{counter}{ext}"
                            new_img_path = os.path.join(img_folder, new_img_name)
                            counter += 1
                        print(f"使用替代名称: {new_img_name}")
                        
                        # 更新MD文件中的图片引用
                        if img_dir:
                            folder_name = md_name.replace(' ', '%20')
                            old_img_reference = f"{img_dir}/{folder_name}/{img_name}"
                            new_img_reference = f"{img_dir}/{folder_name}/{new_img_name}"
                            
                            with open(md_path, 'r', encoding='utf-8') as file:
                                md_content = file.read()
                            
                            md_content = md_content.replace(old_img_reference, new_img_reference)
                            
                            with open(md_path, 'w', encoding='utf-8') as file:
                                file.write(md_content)
                            print(f"已更新图片引用: {old_img_reference} -> {new_img_reference}")
                    
                    # 移动文件
                    shutil.move(old_img_path, new_img_path)
                    print(f"已移动: {img_name} -> {img_folder}")

def add_yaml_header(folder_path, tags, categories, prefix):
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            md_name = os.path.splitext(filename)[0]

            # 如果 prefix 不为空且 md_name 以 prefix 开头，移除 prefix 获取 original_name
            if prefix and md_name.startswith(prefix):
                original_name = md_name[len(prefix):]
                title = f"{prefix} - {original_name}"
            else:
                title = md_name

            stat = os.stat(file_path)
            # 将日期转换成只有年月日的字符串
            create_date = time.strftime("%Y-%m-%d", time.localtime(stat.st_ctime))
            update_date = time.strftime("%Y-%m-%d", time.localtime(stat.st_mtime))

            yaml_header = (
                f"---\n"
                f"title: {title}\n"
                f"date: '{create_date}'\n"
                f"updated: '{update_date}'\n"
                f"tags: {', '.join(tags)}\n"
                f"categories: {categories}\n"
                f"comments: true\n"
                f"---\n\n"
            )

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            if content.startswith("---\n"):
                print(f"跳过: {filename}（已存在 YAML 头部）")
                continue

            new_content = yaml_header + content

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            print(f"已添加 YAML 头部: {filename}")

def main():
    parser = argparse.ArgumentParser(description="整理 Markdown 相关文件")
    parser.add_argument("--folder_path", required=True, help="包含文件的文件夹路径")
    parser.add_argument("--tags", nargs='+', required=True, help="Markdown 文件的标签（不能为空）")
    parser.add_argument("--categories", required=True, help="Markdown 文件的分类（不能为空）")
    parser.add_argument("--prefix", required=False, default="", help="可选的文件名前缀")
    parser.add_argument("--img_dir", required=False, help="图片的绝对路径前缀，例如 '/post-images/'")
    args = parser.parse_args()

    folder_path = args.folder_path
    tags = args.tags
    categories = args.categories
    prefix = args.prefix
    img_dir = args.img_dir

    if not os.path.isdir(folder_path):
        print("错误：指定的文件夹不存在")
        return

    # 1. 首先重命名PNG文件，去除空格
    rename_png_files(folder_path)
    
    # 2. 清理MD文件名（去除MD5校验码）
    clean_md_filenames(folder_path, prefix)  
    
    # 3. 更新MD文件中的图片引用
    update_md_files(folder_path, img_dir)
    
    # 4. 移动图片到同名文件夹
    move_md_images(folder_path, prefix, img_dir)
    
    # 5. 最后添加YAML头部
    add_yaml_header(folder_path, tags, categories, prefix)

if __name__ == "__main__":
    main()
