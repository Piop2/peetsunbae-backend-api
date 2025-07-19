import json
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Optional, Literal, Sequence

import requests


@dataclass(frozen=True)
class Day:
    number: int
    is_total: bool

    def get_exam_id(self) -> int:
        if self.is_total:
            return self.number * 2 - 2
        return self.number * 2 - 1


@dataclass(frozen=True)
class User:
    access_token: str
    id: int
    name: str
    value: str
    academy: str
    location: str
    job: Optional[str]
    email: str
    todoist_api_key: Optional[str]
    todoist_email: Optional[str]
    avatar: int
    filtered_location: Optional[str]


@dataclass
class Word:
    id: int
    day: int
    word: str
    meaning: str
    answer: str = field(default="")
    how_long: int = field(default=0)
    result: Literal["correct", "incorrect"] = field(default="correct")

    def to_dict(self) -> dict[str, int | str]:
        return {
            "id": self.id,
            "day": self.day,
            "word": self.word,
            "meaning": self.meaning,
            "answer": self.answer,
            "howlong": self.how_long,
            "result": self.result,
        }


class Book(Enum):
    WORDMASTER_V2018 = auto()
    # WORDMASTER_V2022 = auto()
    # WORDMASTER_HYPER_V2021 = auto()
    # WORDMASTER_FINAL_V2020 = auto()


def start(access_token: str) -> User:
    """토큰을 통해 수능선배에서 유저 정보를 가져옵니다.

    해당 패키지의 다른 함수들을 사용하기 위해서 반드시 선행되어야하는 함수입니다.

    Args:
        access_token (str): 수능선배 유저 토큰

    Returns:
        User: 유저 데이터
    """
    response_json: dict[str, Any] = requests.get(
        url="https://peetsunbae.com/dashboard/home/start",
        cookies={"access_token": access_token},
    ).json()
    return User(
        access_token=access_token,
        id=response_json["id"],
        name=response_json["name"],
        value=response_json["value"],
        academy=response_json["academy"],
        location=response_json["location"],
        job=response_json["job"],
        email=response_json["email"],
        todoist_api_key=response_json["todoistApiKey"],
        todoist_email=response_json["todoistEmail"],
        avatar=response_json["avatar"],
        filtered_location=response_json["filteredLocation"],
    )


def start_word_tests(user: User, book: Book, days: Sequence[Day]) -> tuple[Word, ...]:
    """테스트할 단어를 가져옵니다

    Args:
        user (User): 유저 데이터
        book (Book): 테스트할 영어 단어장
        days (Sequence[Day]): 테스트할 단어 Day

    Raises:
        ValueError: 올바르지 않은 단어장 번호

    Returns:
        tuple[Word, ...]: 단어
    """
    list_length: int
    book_kind: str
    match book:
        case Book.WORDMASTER_V2018:
            list_length = 116
            book_kind = "book1"
        case _:
            raise ValueError

    exam_ids: list[int] = [day.get_exam_id() for day in days]

    check_list: list[bool] = []
    for i in range(list_length):
        if i in exam_ids:
            check_list.append(True)
            continue
        check_list.append(False)

    response: requests.Response = requests.post(
        url="https://peetsunbae.com/dashboard/words/starttest",
        cookies={"access_token": user.access_token},
        json={
            "check": check_list,
            "bookKind": book_kind,
            "userName": user.name,
        },
    )
    response.raise_for_status()

    return tuple(
        [
            Word(
                id=word_data["id"],
                day=word_data["day"],
                word=word_data["word"],
                meaning=word_data["meaning"],
            )
            for word_data in response.json()["data"]
        ]
    )


def save_word_test(
    user: User, book: Book, days: Sequence[Day], answers: tuple[Word, ...]
) -> None:
    """테스트 결과를 저장합니다

    Args:
        user (User): 유저 데이터
        book (Book): 영어 단어장
        days (Sequence[Day]): 테스트한 단어 Day
        answers (tuple[Word, ...]): 테스트 결과

    Raises:
        ValueError: 올바르지 않은 단어장 번호
    """
    data: list[dict[str, int | str]] = [answer.to_dict() for answer in answers]

    day_informations: list[dict[str, int | bool]] = []
    for day in days:
        day_informations.append({"dayNumber": day.number, "isTotal": day.is_total})

    book_kind: int
    match book:
        case Book.WORDMASTER_V2018:
            book_kind = 1
        case _:
            raise ValueError

    response: requests.Response = requests.post(
        url="https://peetsunbae.com/dashboard/words/save",
        cookies={"access_token": user.access_token},
        json={
            "data": json.dumps(data),
            "dayInfo": day_informations,
            "kind": book_kind,
        },
    )

    response.raise_for_status()
    return
