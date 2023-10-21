from typing import List, Optional

from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Table, Text, \
    UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Character(Base):
    __tablename__ = 'character'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='character_pkey'),
        {'schema': 'shakespeare'}
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    speech_count: Mapped[int] = mapped_column(Integer)
    abbrev: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(String(2056))

    work: Mapped[list['Work']] = relationship('Work', secondary='shakespeare.character_work', back_populates='character')
    paragraph: Mapped[list['Paragraph']] = relationship('Paragraph', back_populates='character')


class Wordform(Base):
    __tablename__ = 'wordform'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='wordform_pkey'),
        {'schema': 'shakespeare'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plain_text: Mapped[str] = mapped_column(String(64))
    phonetic_text: Mapped[str] = mapped_column(String(64))
    stem_text: Mapped[str] = mapped_column(String(64))
    occurences: Mapped[int] = mapped_column(Integer)


class Work(Base):
    __tablename__ = 'work'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='work_pkey'),
        {'schema': 'shakespeare'}
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(32))
    long_title: Mapped[str] = mapped_column(String(64))
    year: Mapped[int] = mapped_column(Integer)
    genre_type: Mapped[str] = mapped_column(String(1))
    source: Mapped[str] = mapped_column(String(16))
    total_words: Mapped[int] = mapped_column(Integer)
    total_paragraphs: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    character: Mapped[list['Character']] = relationship('Character', secondary='shakespeare.character_work', back_populates='work')
    chapter: Mapped[list['Chapter']] = relationship('Chapter', back_populates='work')
    paragraph: Mapped[list['Paragraph']] = relationship('Paragraph', back_populates='work')


class Chapter(Base):
    __tablename__ = 'chapter'
    __table_args__ = (
        ForeignKeyConstraint(['work_id'], ['shakespeare.work.id'], name='chapter_work_id_fkey'),
        PrimaryKeyConstraint('id', name='chapter_pkey'),
        UniqueConstraint('work_id', 'section_number', 'chapter_number', name='chapter_work_id_section_number_chapter_number_key'),
        {'schema': 'shakespeare'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_id: Mapped[str] = mapped_column(String(32))
    section_number: Mapped[int] = mapped_column(Integer)
    chapter_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(256))

    work: Mapped['Work'] = relationship('Work', back_populates='chapter')
    paragraph: Mapped[list['Paragraph']] = relationship('Paragraph', back_populates='chapter')


t_character_work = Table(
    'character_work', Base.metadata,
    Column('character_id', String(32), primary_key=True, nullable=False),
    Column('work_id', String(32), primary_key=True, nullable=False),
    ForeignKeyConstraint(['character_id'], ['shakespeare.character.id'], name='character_work_character_id_fkey'),
    ForeignKeyConstraint(['work_id'], ['shakespeare.work.id'], name='character_work_work_id_fkey'),
    PrimaryKeyConstraint('character_id', 'work_id', name='character_work_pkey'),
    schema='shakespeare'
)


class Paragraph(Base):
    __tablename__ = 'paragraph'
    __table_args__ = (
        ForeignKeyConstraint(['character_id'], ['shakespeare.character.id'], name='paragraph_character_id_fkey'),
        ForeignKeyConstraint(['work_id', 'section_number', 'chapter_number'], ['shakespeare.chapter.work_id', 'shakespeare.chapter.section_number', 'shakespeare.chapter.chapter_number'], name='paragraph_chapter_fkey'),
        ForeignKeyConstraint(['work_id'], ['shakespeare.work.id'], name='paragraph_work_id_fkey'),
        PrimaryKeyConstraint('id', name='paragraph_pkey'),
        {'schema': 'shakespeare'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_id: Mapped[str] = mapped_column(String(32))
    paragraph_num: Mapped[int] = mapped_column(Integer)
    character_id: Mapped[str] = mapped_column(String(32))
    plain_text: Mapped[str] = mapped_column(Text)
    phonetic_text: Mapped[str] = mapped_column(Text)
    stem_text: Mapped[str] = mapped_column(Text)
    paragraph_type: Mapped[str] = mapped_column(String(1))
    section_number: Mapped[int] = mapped_column(Integer)
    chapter_number: Mapped[int] = mapped_column(Integer)
    char_count: Mapped[int] = mapped_column(Integer)
    word_count: Mapped[int] = mapped_column(Integer)

    character: Mapped['Character'] = relationship('Character', back_populates='paragraph')
    chapter: Mapped['Chapter'] = relationship('Chapter', back_populates='paragraph')
    work: Mapped['Work'] = relationship('Work', back_populates='paragraph')

    @classmethod
    async def find(cls, db_session: AsyncSession, character: str):
        stmt = select(cls).join(Character).join(Chapter).join(Work).where(Character.name == character)
        result = await db_session.execute(stmt)
        instance = result.scalars().all()
        return instance
