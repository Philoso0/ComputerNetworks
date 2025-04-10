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

if os.path.exists(attachments_dir):
    for item in os.listdir(attachments_dir):
        src_path = os.path.join(attachments_dir, item)
        dst_path = os.path.join(figures_dir, item)

        if os.path.isfile(src_path):
            print(f"移动 {item} 到 figures/")
            # 如果目标文件已存在则覆盖
            if os.path.exists(dst_path):
                os.remove(dst_path)
            shutil.move(src_path, dst_path)
else:
    print("attachments 文件夹不存在，跳过移动。")

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
