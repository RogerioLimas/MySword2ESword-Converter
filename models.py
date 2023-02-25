from dataclasses import dataclass
from datetime import datetime


@dataclass
class Row:
    """Uma classe que representa a tabela Bible"""
    book: int
    chapter: int
    verse: int
    scripture: str
