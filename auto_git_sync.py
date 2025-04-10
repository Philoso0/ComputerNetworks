import re
from git import Repo, GitCommandError
import os
import sys
import shutil

# === 文件格式化 ===

md_input_path = '计算机网络.md'
md_output_path = '计算机网络_formated.md'
figures_folder_name = 'figures'

# 读取 Markdown 文件内容
with open(md_input_path, 'r', encoding='utf-8') as f:
    text = f.read()

# === 数学公式格式化：$xxx$ -> $ xxx $ （跳过 $$...$$ 块） ===

def process_inline_math(text):
    # 保留 $$...$$ 块，先替换为占位符
    block_pattern = re.compile(r'\$\$\n.*?\n\$\$', re.DOTALL)
    blocks = []
    def block_replacer(match):
        blocks.append(match.group())
        return f"__MATH_BLOCK_{len(blocks)-1}__"
    text = block_pattern.sub(block_replacer, text)

    # 替换 $inline$ 为 $ inline $
    def inline_replacer(match):
        before = match.group(1) or ''
        content = match.group(2)
        after = match.group(3) or ''
        left_space = '' if before.endswith(' ') or before == '' else ' '
        right_space = '' if after.startswith(' ') or after == '' else ' '
        return f'{before}{left_space}${content}${right_space}{after}'

    inline_pattern = re.compile(r'([^\s$])?\$([^\n$]+?)\$([^\s$])?')
    text = inline_pattern.sub(lambda m: inline_replacer(m), text)

    # 恢复 $$...$$ 块
    def restore_block(match):
        index = int(match.group(1))
        return blocks[index]
    text = re.sub(r'__MATH_BLOCK_(\d+)__', restore_block, text)

    return text

text = process_inline_math(text)

# 替换 Markdown 图片语法：![[xxx.png]] -> ![xxx](figures/xxx.png)
text = re.sub(r'!\[\[(.+?)]]', rf'![\1]({figures_folder_name}/\1)', text)

# 保存修改后的 Markdown
with open(md_output_path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"✅ Markdown 格式和数学公式处理完成：{md_output_path}")

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

        if os.path.exists(dst_file_path):
            print(f"⚠️ 文件已存在，覆盖：{file}")
            os.remove(dst_file_path)

        print(f"📁 复制 {src_file_path} 到 {dst_file_path}")
        shutil.copy2(src_file_path, dst_file_path)

# === Git 同步 ===

remote_name = 'compnet'
branch_name = 'main'

try:
    repo = Repo(repo_path)

    if repo.is_dirty(untracked_files=True):
        print("📦 检测到未提交更改，准备提交...")
        repo.git.add(all=True)
        repo.git.commit(m='Auto pre-pull commit')

    print(f"🔄 拉取远程分支 {remote_name}/{branch_name}...")
    repo.git.pull(remote_name, branch_name, allow_unrelated_histories=True)

    print("📥 添加所有变更...")
    repo.git.add(all=True)

    print("📤 提交中...")
    repo.git.commit(m='Auto sync with formatted markdown and moved figures')

    print(f"⬆️ 推送到 {remote_name}/{branch_name}...")
    repo.git.push(remote_name, branch_name)

    print("✅ Git 同步完成。")

except GitCommandError as e:
    if "nothing to commit" in str(e):
        print("📭 无需提交，工作目录干净。")
    else:
        print(f"❌ Git 错误：{e}")
        sys.exit(1)

except Exception as ex:
    print(f"❌ 未知错误：{ex}")
    sys.exit(1)
