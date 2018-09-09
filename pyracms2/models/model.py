from datetime import datetime

from sqlalchemy import (Column, Integer, UnicodeText, Unicode, ForeignKey,
                        DateTime)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, MapperExtension
from sqlalchemy_utils import PasswordType, LocaleType, EmailType, CountryType

from .meta import Base


class BaseExtension(MapperExtension):
    """Base entension class for all entity """

    def before_update(self, mapper, connection, instance):
        """ set the updated_at  """
        instance.updated = datetime.utcnow()


class BaseMixin(object):

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'extension': BaseExtension()}

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow)


class Domain(Base, BaseMixin):
    name = Column(Unicode)


class Translation(Base, BaseMixin):
    """
    A translation for a particular language.
    """
    translation_id = Column(Integer, ForeignKey('translations.id'))
    name = Column(Unicode)
    display_name = Column(UnicodeText)
    description = Column(UnicodeText)
    locale = Column(LocaleType)


class Translations(Base, BaseMixin):
    """
    A collection of languages that you want to translate the translation to.
    """
    translations = relationship(Translation)


class UserGroup(Base, BaseMixin):
    user_id = Column(Integer, ForeignKey('user.id'))
    group_id = Column(Integer, ForeignKey('group.id'))


class Group(Base, BaseMixin):
    name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, back_populates='translations')
    user = relationship("User", secondary=UserGroup, back_populates='group')


class User(Base, BaseMixin):
    name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, back_populates='translations')
    password = Column(PasswordType(schemes=['pbkdf2_sha512']))
    locale = Column(LocaleType)
    email = Column(EmailType)
    country = Column(CountryType)
    entity_id = Column(Integer, ForeignKey('entity.id'))
    entity = relationship(Translations, back_populates='entity')
    group = relationship("Group", secondary=UserGroup, back_populates='user')


class EntityEntity(Base, BaseMixin):
    entity_one_id = Column(Integer, ForeignKey('entity.id'))
    entity_two_id = Column(Integer, ForeignKey('entity.id'))


class EntityTranslations(Base, BaseMixin):
    entity_id = Column(Integer, ForeignKey('entity.id'))
    translations_id = Column(Integer, ForeignKey('translations.id'))


class Entity(Base, BaseMixin):
    name = Column(Unicode)
    route_name = Column(Unicode)
    display_name_id = Column(Integer, ForeignKey('translations.id'))
    display_name = relationship(Translations, back_populates='translations')
    domain_id = Column(Integer, ForeignKey('domain.id'))
    domain = relationship(Domain, back_populates='domain')
    entity = relationship(EntityEntity, back_populates='entity')
    translations = relationship(EntityTranslations, back_populates='entity')
