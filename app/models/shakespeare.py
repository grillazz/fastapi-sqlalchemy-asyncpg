from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Character(Base):
    """
    The `Character` class represents a character in Shakespeare's works.

    ### Explanation
    This class defines the structure and attributes of a character,
    including their ID, name, speech count, abbreviation, and description.
    It also establishes relationships with the `Work` and `Paragraph` classes.

    ### Attributes
    - `id` (str): The ID of the character.
    - `name` (str): The name of the character.
    - `speech_count` (int): The number of speeches made by the character.
    - `abbrev` (str | None): An abbreviation for the character's name.
    - `description` (str | None): A description of the character.
    - `work` (list[Work]): The works associated with the character.
    - `paragraph` (list[Paragraph]): The paragraphs associated with the character.
    """

    __tablename__ = "character"
    __table_args__ = (PrimaryKeyConstraint("id", name="character_pkey"), {"schema": "shakespeare"})

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    speech_count: Mapped[int] = mapped_column(Integer)
    abbrev: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(String(2056))

    work: Mapped[list["Work"]] = relationship(
        "Work", secondary="shakespeare.character_work", back_populates="character"
    )
    paragraph: Mapped[list["Paragraph"]] = relationship("Paragraph", back_populates="character")


class Wordform(Base):
    """
    The `Wordform` class represents a word form in Shakespeare's works.

    ### Explanation
    This class defines the structure and attributes of a word form, including its ID, plain text representation, phonetic text representation, stem text representation, and the number of occurrences.

    ### Attributes
    - `id` (int): The ID of the word form.
    - `plain_text` (str): The plain text representation of the word form.
    - `phonetic_text` (str): The phonetic text representation of the word form.
    - `stem_text` (str): The stem text representation of the word form.
    - `occurrences` (int): The number of occurrences of the word form.

    """

    __tablename__ = "wordform"
    __table_args__ = (PrimaryKeyConstraint("id", name="wordform_pkey"), {"schema": "shakespeare"})

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plain_text: Mapped[str] = mapped_column(String(64))
    phonetic_text: Mapped[str] = mapped_column(String(64))
    stem_text: Mapped[str] = mapped_column(String(64))
    occurences: Mapped[int] = mapped_column(Integer)


class Work(Base):
    """
    The `Work` class represents a work in Shakespeare's collection.

    ### Explanation
    This class defines the structure and attributes of a work, including its ID, title, long title, year of publication, genre type, source, total number of words, total number of paragraphs, and any additional notes. It also establishes relationships with the `Character`, `Chapter`, and `Paragraph` classes.

    ### Attributes
    - `id` (str): The ID of the work.
    - `title` (str): The title of the work.
    - `long_title` (str): The long title of the work.
    - `year` (int): The year of publication of the work.
    - `genre_type` (str): The genre type of the work.
    - `source` (str): The source of the work.
    - `total_words` (int): The total number of words in the work.
    - `total_paragraphs` (int): The total number of paragraphs in the work.
    - `notes` (str | None): Additional notes about the work.
    - `character` (list[Character]): The characters associated with the work.
    - `chapter` (list[Chapter]): The chapters associated with the work.
    - `paragraph` (list[Paragraph]): The paragraphs associated with the work.

    """

    __tablename__ = "work"
    __table_args__ = (PrimaryKeyConstraint("id", name="work_pkey"), {"schema": "shakespeare"})

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(32))
    long_title: Mapped[str] = mapped_column(String(64))
    year: Mapped[int] = mapped_column(Integer)
    genre_type: Mapped[str] = mapped_column(String(1))
    source: Mapped[str] = mapped_column(String(16))
    total_words: Mapped[int] = mapped_column(Integer)
    total_paragraphs: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    character: Mapped[list["Character"]] = relationship(
        "Character", secondary="shakespeare.character_work", back_populates="work"
    )
    chapter: Mapped[list["Chapter"]] = relationship("Chapter", back_populates="work")
    paragraph: Mapped[list["Paragraph"]] = relationship("Paragraph", back_populates="work")


class Chapter(Base):
    """
    The `Chapter` class represents a chapter in a work of Shakespeare.

    ### Explanation
    This class defines the structure and attributes of a chapter, including its ID, work ID, section number, chapter number, and description. It establishes a relationship with the `Work` class and has a collection of associated paragraphs.

    ### Attributes
    - `id` (int): The ID of the chapter.
    - `work_id` (str): The ID of the associated work.
    - `section_number` (int): The section number of the chapter.
    - `chapter_number` (int): The chapter number.
    - `description` (str): A description of the chapter.
    - `work` (Work): The associated work.
    - `paragraph` (list[Paragraph]): The paragraphs associated with the chapter.

    """

    __tablename__ = "chapter"
    __table_args__ = (
        ForeignKeyConstraint(["work_id"], ["shakespeare.work.id"], name="chapter_work_id_fkey"),
        PrimaryKeyConstraint("id", name="chapter_pkey"),
        UniqueConstraint(
            "work_id", "section_number", "chapter_number", name="chapter_work_id_section_number_chapter_number_key"
        ),
        {"schema": "shakespeare"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_id: Mapped[str] = mapped_column(String(32))
    section_number: Mapped[int] = mapped_column(Integer)
    chapter_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(256))

    work: Mapped["Work"] = relationship("Work", back_populates="chapter")
    paragraph: Mapped[list["Paragraph"]] = relationship("Paragraph", back_populates="chapter")


t_character_work = Table(
    "character_work",
    Base.metadata,
    Column("character_id", String(32), primary_key=True, nullable=False),
    Column("work_id", String(32), primary_key=True, nullable=False),
    ForeignKeyConstraint(["character_id"], ["shakespeare.character.id"], name="character_work_character_id_fkey"),
    ForeignKeyConstraint(["work_id"], ["shakespeare.work.id"], name="character_work_work_id_fkey"),
    PrimaryKeyConstraint("character_id", "work_id", name="character_work_pkey"),
    schema="shakespeare",
)


class Paragraph(Base):
    """
    The `Paragraph` class represents a paragraph in a work of Shakespeare.

    ### Explanation
    This class defines the structure and attributes of a paragraph, including its ID, work ID, paragraph number, character ID, plain text representation, phonetic text representation, stem text representation, paragraph type, section number, chapter number, character count, and word count. It establishes relationships with the `Character`, `Chapter`, and `Work` classes.

    ### Attributes
    - `id` (int): The ID of the paragraph.
    - `work_id` (str): The ID of the associated work.
    - `paragraph_num` (int): The paragraph number.
    - `character_id` (str): The ID of the associated character.
    - `plain_text` (str): The plain text representation of the paragraph.
    - `phonetic_text` (str): The phonetic text representation of the paragraph.
    - `stem_text` (str): The stem text representation of the paragraph.
    - `paragraph_type` (str): The type of the paragraph.
    - `section_number` (int): The section number of the paragraph.
    - `chapter_number` (int): The chapter number of the paragraph.
    - `char_count` (int): The character count in the paragraph.
    - `word_count` (int): The word count in the paragraph.
    - `character` (Character): The associated character.
    - `chapter` (Chapter): The associated chapter.
    - `work` (Work): The associated work.

    ### Class Method
    - `find(cls, db_session: AsyncSession, character: str) -> List[Paragraph]`: A class method that finds paragraphs associated with a specific character. It takes a database session and the name of the character as arguments, and returns a list of matching paragraphs.

    """

    __tablename__ = "paragraph"
    __table_args__ = (
        ForeignKeyConstraint(["character_id"], ["shakespeare.character.id"], name="paragraph_character_id_fkey"),
        ForeignKeyConstraint(
            ["work_id", "section_number", "chapter_number"],
            ["shakespeare.chapter.work_id", "shakespeare.chapter.section_number", "shakespeare.chapter.chapter_number"],
            name="paragraph_chapter_fkey",
        ),
        ForeignKeyConstraint(["work_id"], ["shakespeare.work.id"], name="paragraph_work_id_fkey"),
        PrimaryKeyConstraint("id", name="paragraph_pkey"),
        {"schema": "shakespeare"},
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

    character: Mapped["Character"] = relationship("Character", back_populates="paragraph")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="paragraph")
    work: Mapped["Work"] = relationship("Work", back_populates="paragraph")

    @classmethod
    async def find(cls, db_session: AsyncSession, character: str):
        """
        `find` is a class method of the `Paragraph` class that finds paragraphs associated with a specific character.

        ### Explanation
        This method takes a database session (`db_session`) and the name of the character (`character`) as arguments.
        It performs a database query to find paragraphs that are associated with the specified character.
        The method returns a list of matching paragraphs.

        ### Args
        - `db_session` (AsyncSession): The database session to use for the query.
        - `character` (str): The name of the character to find paragraphs for.

        ### Returns
        - List[Paragraph]: A list of `Paragraph` objects that are associated with the specified character.

        """
        stmt = select(cls).join(Character).join(Chapter).join(Work).where(Character.name == character)
        result = await db_session.execute(stmt)
        return result.scalars().all()
