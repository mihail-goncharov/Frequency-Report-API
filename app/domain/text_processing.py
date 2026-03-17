import re
from functools import lru_cache
from typing import Iterable

import pymorphy3

_word_re = re.compile(r"[A-Za-zA-Яа-яЁё]+")


class Lemmatizer:
    def __init__(self) -> None:
        self._morph = pymorphy3.MorphAnalyzer()

    @lru_cache(maxsize=100_000)
    def lemma(self, word: str) -> str:
        parsed = self._morph.parse(word)
        if not parsed:
            return word
        return parsed[0].normal_form


def tokenize(line: str) -> Iterable[str]:
    for match in _word_re.finditer(line):
        yield match.group(0).lower()
