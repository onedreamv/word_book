import typer,tomllib
from pathlib import Path

#todo 先这这里写toml,后续独立为一个文件
toml_config = """
title = "My Word Book"
[settings]
main_book_path = "word_book.md"
"""
toml_data = tomllib.loads(toml_config)
main_book_path = Path(toml_data["settings"]["main_book_path"])

print(main_book_path)
app = typer.Typer()

class word_book_manager:
    
    def add(self,word : str,):
        with open(main_book_path, "r",encoding="utf-8",) as f:
            existing = {line.strip() for line in f if line.strip()}
            #读取文件内容，去除空行，并将单词存储在一个集合中
        if word in existing:
            print(f"{word} 已经在词书里了.")
        else:
            with open(main_book_path, "a",encoding="utf-8",) as f:
                f.write(word + "\n")
            print(f"{word} 已经添加到词书里了.")



            
    