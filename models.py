from dataclasses import dataclass
from datetime import datetime


@dataclass
class BibleRow:
    """Uma classe que representa um registro da tabela Bible"""
    book: int
    chapter: int
    verse: int
    scripture: str


@dataclass
class CommentaryRow:
    """Uma classe que representa um registro da tabela Commentary"""
    id: int
    book: int
    chapter: int
    fromverse: int
    toverse: int
    data: str
