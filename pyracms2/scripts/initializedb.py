import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars
from sqlalchemy_utils import Country

from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models.model import *


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        translations = Translations()
        translation = Translation("test", "Test", "Just Testing",
                                  Locale("en_GB"))
        translations.translations.append(translation)
        user = User()
        user.name = "test"
        user.display_name = translations
        user.locale = Locale("en_GB")
        user.email = "test@example.com"
        user.country = Country("GB")
        user.password = "password1"
        dbsession.add(user)

        entity = Entity()
        entity.name = "test"
        entity.display_name = translations

        domain = Domain()
        domain.name = "test"
        domain.display_name = "test"
        domain.url = "test.com"

        entity.domain = domain

        entity_two = Entity()
        entity_two.name = "test"
        entity_two.display_name = translations
        entity.entities.append(entity_two)
        dbsession.add(entity)