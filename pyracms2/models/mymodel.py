from sqlalchemy import (
    Column,
    # Index,
    Integer,
    UnicodeText,
    Unicode,
    ForeignKey
)
from sqlalchemy.orm import relationship

from .meta import Base


class Domain(Base):
    __tablename__ = 'domain'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)

class Locale(Base):
    __tablename__ = 'locale'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    display_name = Column(UnicodeText)

class Translation(Base):
    __tablename__ = 'translation'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    display_name = Column(UnicodeText)

class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    route_name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translation.id'))
    display_name = relationship(Translation, back_populates='translation')

# Index('my_index', MyModel.name, unique=True, mysql_length=255)
