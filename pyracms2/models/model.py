from sqlalchemy import (
    Column, Integer, UnicodeText, Unicode, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import (
    PasswordType, LocaleType, EmailType, CountryType)

from .meta import Base


class Domain(Base):
    __tablename__ = 'domain'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)


class UserGroup(Base):
    __tablename__ = 'user_group'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    group_id = Column(Integer, ForeignKey('group.id'))


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, back_populates='translations')
    user = relationship(UserGroup, back_populates='user')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, back_populates='translations')
    password = Column(PasswordType(schemes=['pbkdf2_sha512']))
    locale = Column(LocaleType)
    email = Column(EmailType)
    country = Column(CountryType)
    entity_id = Column(Integer, ForeignKey('entity.id'))
    entity = relationship(Translations, back_populates='entity')
    group = relationship(UserGroup, back_populates='group')


class Translation(Base):
    """
    A translation for a particular language.
    """
    __tablename__ = 'translation'
    id = Column(Integer, primary_key=True)
    translation_id = Column(Integer, ForeignKey('translations.id'))
    name = Column(Unicode)
    display_name = Column(UnicodeText)
    description = Column(UnicodeText)
    locale = Column(LocaleType)


class Translations(Base):
    """
    A collection of languages that you want to translate the translation to.
    """
    __tablename__ = 'translations'
    id = Column(Integer, primary_key=True)
    translations = relationship(Translation)


class EntityEntity(Base):
    __tablename__ = 'entity_entity'
    id = Column(Integer, primary_key=True)
    entity_one_id = Column(Integer, ForeignKey('entity.id'))
    entity_two_id = Column(Integer, ForeignKey('entity.id'))


class EntityTranslations(Base):
    __tablename__ = 'entity_translations'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entity.id'))
    translations_id = Column(Integer, ForeignKey('translations.id'))


class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    route_name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, back_populates='translations')
    domain_id = Column(Integer, ForeignKey('domain.id'))
    domain = relationship(Domain, back_populates='domain')
    entity = relationship(EntityEntity, back_populates='entity')
    translations = relationship(EntityTranslations, back_populates='entity')


# Index('my_index', MyModel.name, unique=True, mysql_length=255)
