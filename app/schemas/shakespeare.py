from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class Character(BaseModel):
    id: str
    abbrev: str
    speech_count: int
    name: str
    description: Any


class Chapter(BaseModel):
    work_id: str
    section_number: int
    description: str
    id: int
    chapter_number: int


class Work(BaseModel):
    id: str
    year: int
    source: str
    total_paragraphs: int
    title: str
    long_title: str
    genre_type: str
    total_words: int
    notes: Any


class Paragraph(BaseModel):
    id: int
    character_id: str
    phonetic_text: str
    paragraph_type: str
    section_number: int
    char_count: int
    work_id: str
    paragraph_num: int
    plain_text: str
    stem_text: str
    chapter_number: int
    word_count: int
    character: Character
    chapter: Chapter
    work: Work
