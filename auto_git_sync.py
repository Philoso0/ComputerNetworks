import re
from git import Repo, GitCommandError
import os
import sys
import shutil

# === 文件格式化 ===

md_input_path = '计算机网络.md'
md_output_path = '计算机网络_formated.md'
figures_folder_name = 'figures'

# 使用正则替换 ![[xxx.png]] -> ![xxx](figures/xxx.png)
with open(md_input_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 替换 Markdown 图片语法
new_text = re.sub(r'!\[\[(.+?)]]', rf'![\1]({figures_folder_name}/\1)', text)

with open(md_output_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print(f"Markdown 图片路径替换完成：{md_output_path}")

# === 移动 attachments 下的文件到 figures ===

repo_path = os.path.abspath('.')  # 当前目录
attachments_dir = os.path.join(repo_path, 'attachments')
figures_dir = os.path.join(repo_path, figures_folder_name)

os.makedirs(figures_dir, exist_ok=True)

# 遍历 attachments 下所有子目录及文件
for root, dirs, files in os.walk(attachments_dir):
    for file in files:
        src_file_path = os.path.join(root, file)
        dst_file_path = os.path.join(figures_dir, file)

        # 如果目标已存在，可选择覆盖或跳过
        if os.path.exists(dst_file_path):
            print(f"⚠️ 文件已存在，覆盖：{file}")
            os.remove(dst_file_path)

        print(f"📁 复制 {src_file_path} 到 {dst_file_path}")
        shutil.copy2(src_file_path, dst_file_path)

# === Git 同步 ===

remote_name = 'compnet'      # 或 'compnet'
branch_name = 'main'

try:
    repo = Repo(repo_path)

    print(f"正在拉取 {remote_name}/{branch_name}...")
    repo.git.pull(remote_name, branch_name, allow_unrelated_histories=True)

    print("添加所有变更...")
    repo.git.add(all=True)

    print("提交中...")
    repo.git.commit(m='Auto sync with formatted markdown and moved figures')

    print(f"推送到 {remote_name}/{branch_name}...")
    repo.git.push(remote_name, branch_name)

    print("Git 同步完成。")

except GitCommandError as e:
    if "nothing to commit" in str(e):
        print("📭 无需提交，工作目录干净。")
    else:
        print(f"❌ Git 错误：{e}")
        sys.exit(1)

except Exception as ex:
    print(f"❌ 未知错误：{ex}")
    sys.exit(1)