import tomllib
import re

import sunbae_api
from sunbae_api import Day, Book, Word

BOOK: Book = Book.WORDMASTER_V2018
TARGET_DAYS: tuple[Day] = (Day(number=1, is_total=True),)

token: str = ""
with open("config.toml", "rb") as file:
    config_file = tomllib.load(file)
    token = config_file["token"]


user: sunbae_api.User = sunbae_api.start(token)

words: tuple[Word, ...] = sunbae_api.start_word_tests(
    user=user, book=BOOK, days=TARGET_DAYS
)

for word in words:
    answer: str = word.meaning.split(", ")[0]
    word.answer = re.sub(r"\([^)]*\)|\[[^]]*\]", "", answer)

sunbae_api.save_word_test(user=user, book=BOOK, days=TARGET_DAYS, answers=words)
