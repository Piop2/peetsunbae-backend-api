import tomllib
import re

import sunbae_api
from sunbae_api import Day, Book, Word

BOOK: Book = Book.WORDMASTER_V2018

target_days: list[Day] = []
days_str: list[str] = input(">>> ").split()

for day_str in days_str:
    is_total: bool
    match day_str[-1:]:
        case "a":
            is_total = True
        case "w":
            is_total = False
        case _:
            raise RuntimeError

    target_days.append(Day(int(day_str[0:-1]), is_total))

token: str
with open("config.toml", "rb") as file:
    config_file = tomllib.load(file)
    token = config_file["token"]


user: sunbae_api.User = sunbae_api.start(token)

words: tuple[Word, ...] = sunbae_api.start_word_tests(
    user=user, book=BOOK, days=target_days
)

for word in words:
    answer: str = word.meaning.split(", ")[0]
    word.answer = re.sub(r"\([^)]*\)|\[[^]]*]", "", answer)

sunbae_api.save_word_test(user=user, book=BOOK, days=target_days, answers=words)
