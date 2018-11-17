from datetime import datetime
from string import ascii_letters, digits

from babel import Locale
from nanoid import generate
from sqlalchemy import (Column, Integer, UnicodeText, Unicode, ForeignKey,
                        DateTime, Table, Numeric, Boolean)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, MapperExtension
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils import PasswordType, LocaleType, EmailType, CountryType

from .meta import Base


def create_fingerprint():
    return generate(ascii_letters + digits, 8)


class BaseExtension(MapperExtension):

    """Base entension class for all entity """
    def before_update(self, mapper, connection, instance):
        instance.updated = datetime.utcnow()


class BaseMixin(object):

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'extension': BaseExtension()}

    id = Column(Integer, primary_key=True)
    fingerprint = Column(Unicode, unique=True, default=create_fingerprint)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow)


class Domain(Base, BaseMixin):
    name = Column(Unicode)
    display_name = Column(Unicode)
    url = Column(Unicode)


class Translation(Base, BaseMixin):
    """
    A translation for a particular language.
    """
    translation_id = Column(Integer, ForeignKey('translations.id'))
    name = Column(Unicode)
    display_name = Column(UnicodeText)
    description = Column(UnicodeText)
    locale = Column(LocaleType)

    def __init__(self, name: str, display_name: str, description: str,
                 locale: Locale):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.locale = locale


class Translations(Base, BaseMixin):
    """
    A collection of languages that you want to translate the translation to.
    """
    translations = relationship(Translation, cascade='all, delete-orphan')


entity_entity = Table('entityentity', Base.metadata,
                      Column("entity_one_id", Integer,
                            ForeignKey('entity.id')),
                      Column("entity_two_id", Integer,
                            ForeignKey('entity.id'))
                      )

entity_translations = Table('entitytranslations', Base.metadata,
                            Column("entity_id", Integer,
                                  ForeignKey('entity.id')),
                            Column("translations_id", Integer,
                                  ForeignKey('translations.id'))
                            )


class DataType(BaseMixin):
    name = Column(Unicode)

    @declared_attr
    def entity_id(self):
        return Column(Integer, ForeignKey('entity.id'))


class Strings(Base, DataType):
    string = Column(UnicodeText)


class Integers(Base, DataType):
    integer = Column(Integer)


class Floats(Base, DataType):
    float = Column(Numeric)


class Booleans(Base, DataType):
    boolean = Column(Boolean(name="boolean"))


class Entity(Base, BaseMixin):
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    route_name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, cascade='all, delete-orphan')
    domain_id = Column(Integer, ForeignKey('domain.id'))
    domain = relationship(Domain)
    translations = relationship(Translations, secondary=entity_translations)
    entities = relationship("Entity", secondary=entity_entity,
                            back_populates='entities',
                            primaryjoin=id == entity_entity.c.entity_one_id,
                            secondaryjoin=id == entity_entity.c.entity_two_id,
                            collection_class=
                            attribute_mapped_collection('name'),
                            cascade='all, delete-orphan')
    strings = relationship(Strings, cascade='all, delete-orphan')
    booleans = relationship(Booleans, cascade='all, delete-orphan')
    integers = relationship(Integers, cascade='all, delete-orphan')
    floats = relationship(Floats, cascade='all, delete-orphan')


class RootEntities(Base, BaseMixin):
    entity_id = Column(Integer, ForeignKey('entity.id'))
    entity = relationship(Entity)


user_group = Table('usergroup', Base.metadata,
                   Column('user_id', Integer, ForeignKey('user.id')),
                   Column('group_id', Integer, ForeignKey('group.id'))
                   )


class Group(Base, BaseMixin):
    name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, cascade='all, delete-orphan')
    user = relationship("User", secondary=user_group, back_populates='group')


class User(Base, BaseMixin):
    name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, cascade='all, delete-orphan')
    password = Column(PasswordType(schemes=['pbkdf2_sha512']))
    locale = Column(LocaleType)
    email = Column(EmailType)
    country = Column(CountryType)
    entity_id = Column(Integer, ForeignKey('entity.id'))
    entity = relationship(Entity)
    group = relationship(Group, secondary=user_group, back_populates='user')
