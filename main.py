import typer,tomllib
from pathlib import Path

#todo 先这这里写toml,后续独立为一个文件
toml_config = """
title = "My Word Book"
[settings]
main_book_path = "word_book.md"
"""
toml_data = tomllib.loads(toml_config)
main_book_path : Path = Path(toml_data["settings"]["main_book_path"])

app : typer.Typer = typer.Typer()

class word_book_manager:
    """管理词书的类，提供添加单词,合并,清洗词书等功能"""
    def __init__(self, main_book_path : Path):
        self.main_book_path = main_book_path

    def add(self,word : str,):

        with open(self.main_book_path, "r",encoding="utf-8",) as f:
            existing : set[str] = {line.strip() for line in f if line.strip()}
            #读取文件内容，去除空行，并将单词存储在一个集合中
        if word in existing:
            print(f"{word} 已经在词书里了.")
        else:
            with open(self.main_book_path, "a",encoding="utf-8",) as f:
                f.write(word + "\n")
            print(f"{word} 已经添加到词书里了.")

    def merge(self,other_book_path : Path,):

        with open(self.main_book_path, "r",encoding="utf-8",) as f:
            existing : set[str] = {line.strip() for line in f if line.strip()}
        with open(other_book_path, "r",encoding="utf-8",) as f:
            other_words : set[str] = {line.strip() for line in f if line.strip()}
        new_words = other_words - existing
        if new_words:
            with open(self.main_book_path, "a",encoding="utf-8",) as f:
                for word in new_words:
                    f.write('\n'.join([word,]))
            print(f"已合并 {len(new_words)} 个新单词.")
        else:
            print("没有新单词需要合并.")

            



            
    