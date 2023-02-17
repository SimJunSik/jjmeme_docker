from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    BigInteger,
    ForeignKey,
)
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ACCOUNT(Base):
    __tablename__ = "ACCOUNT"
    account_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
    password = Column(String(), nullable=False)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)


class MEME(Base):
    __tablename__ = "MEME"
    meme_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(), nullable=False)
    description = Column(String(), default="")
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)


class IMAGE(Base):
    __tablename__ = "IMAGE"
    image_id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(), nullable=False)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    meme_id = Column(Integer, ForeignKey("MEME.meme_id"))


class TAG(Base):
    __tablename__ = "TAG"
    tag_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("CATEGORY.category_id"), nullable=True)
    name = Column(String(), nullable=False)
    view_count = Column(Integer, default=0)


class MEME_TAG(Base):
    __tablename__ = "MEME_TAG"
    meme_tag_id = Column(Integer, primary_key=True, index=True)
    meme_id = Column(Integer, ForeignKey("MEME.meme_id"))
    tag_id = Column(Integer, ForeignKey("TAG.tag_id"))


class CATEGORY(Base):
    __tablename__ = "CATEGORY"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(), nullable=False)
    priority = Column(Integer, default=0)


class TAG_FAV(Base):
    __tablename__ = "TAG_FAV"
    tag_like_id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("TAG.tag_id"))
    account_id = Column(Integer, ForeignKey("ACCOUNT.account_id"))


class COLLECTION(Base):
    __tablename__ = "COLLECTION"
    collection_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("ACCOUNT.account_id"))
    is_shared = Column(Boolean())


class MEME_COLLECTION(Base):
    __tablename__ = "MEME_COLLECTION"
    meme_board_id = Column(Integer, primary_key=True, index=True)
    meme_id = Column(Integer, ForeignKey("MEME.meme_id"))
    collection_id = Column(Integer, ForeignKey("COLLECTION.board_id"))
    