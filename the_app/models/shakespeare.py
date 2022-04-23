from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Character(Base):
    __tablename__ = 'character'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='character_pkey'),
        {'schema': 'shakespeare'}
    )

    id = Column(String(32))
    name = Column(String(64), nullable=False)
    speech_count = Column(Integer, nullable=False)
    abbrev = Column(String(32))
    description = Column(String(2056))

    work = relationship('Work', secondary='shakespeare.character_work', back_populates='character')
    paragraph = relationship('Paragraph', back_populates='character')


class Wordform(Base):
    __tablename__ = 'wordform'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='wordform_pkey'),
        {'schema': 'shakespeare'}
    )

    id = Column(Integer)
    plain_text = Column(String(64), nullable=False)
    phonetic_text = Column(String(64), nullable=False)
    stem_text = Column(String(64), nullable=False)
    occurences = Column(Integer, nullable=False)


class Work(Base):
    __tablename__ = 'work'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='work_pkey'),
        {'schema': 'shakespeare'}
    )

    id = Column(String(32))
    title = Column(String(32), nullable=False)
    long_title = Column(String(64), nullable=False)
    year = Column(Integer, nullable=False)
    genre_type = Column(String(1), nullable=False)
    source = Column(String(16), nullable=False)
    total_words = Column(Integer, nullable=False)
    total_paragraphs = Column(Integer, nullable=False)
    notes = Column(Text)

    character = relationship('Character', secondary='shakespeare.character_work', back_populates='work')
    chapter = relationship('Chapter', back_populates='work')
    paragraph = relationship('Paragraph', back_populates='work')


class Chapter(Base):
    __tablename__ = 'chapter'
    __table_args__ = (
        ForeignKeyConstraint(['work_id'], ['shakespeare.work.id'], name='chapter_work_id_fkey'),
        PrimaryKeyConstraint('id', name='chapter_pkey'),
        UniqueConstraint('work_id', 'section_number', 'chapter_number', name='chapter_work_id_section_number_chapter_number_key'),
        {'schema': 'shakespeare'}
    )

    id = Column(Integer)
    work_id = Column(ForeignKey('shakespeare.work.id'), nullable=False)
    section_number = Column(Integer, nullable=False)
    chapter_number = Column(Integer, nullable=False)
    description = Column(String(256), nullable=False)

    work = relationship('Work', back_populates='chapter')
    paragraph = relationship('Paragraph', back_populates='chapter')


t_character_work = Table(
    'character_work', metadata,
    Column('character_id', ForeignKey('shakespeare.character.id'), nullable=False),
    Column('work_id', ForeignKey('shakespeare.work.id'), nullable=False),
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

    id = Column(Integer)
    work_id = Column(ForeignKey('shakespeare.work.id'), nullable=False)
    paragraph_num = Column(Integer, nullable=False)
    character_id = Column(ForeignKey('shakespeare.character.id'), nullable=False)
    plain_text = Column(Text, nullable=False)
    phonetic_text = Column(Text, nullable=False)
    stem_text = Column(Text, nullable=False)
    paragraph_type = Column(String(1), nullable=False)
    section_number = Column(Integer, nullable=False)
    chapter_number = Column(Integer, nullable=False)
    char_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)

    character = relationship('Character', back_populates='paragraph')
    chapter = relationship('Chapter', back_populates='paragraph')
    work = relationship('Work', back_populates='paragraph')
