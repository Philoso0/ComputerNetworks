import re

with open('计算机网络.md', 'r', encoding='utf-8') as f:
    text = f.read()
new_text = re.sub(r'!\[\[(.+?)]]', r'![\1](\1)', text)
with open('计算机网络_formated.md', 'w', encoding='utf-8') as f:
    f.write(new_text)