import argparse
import sys
from ..models import model

SUB_COMMAND_HELP = 'sub-command --help'


def iter_sub_classes(cls):
    return [x.__name__ for x in cls.__subclasses__()]


# noinspection PyProtectedMember
def insert_add_sub_parser(sub_parser: argparse._SubParsersAction):
    root_add_parser = sub_parser.add_parser('add')
    root_add_parser.set_defaults(sub_parser_1='add')
    add_sub_parser = root_add_parser.add_subparsers(
        help=SUB_COMMAND_HELP + " (Choose a table to add a row to)"
    )
    for cls in iter_sub_classes(model.Base):
        add_parser = add_sub_parser.add_parser(cls)
        add_parser.set_defaults(sub_parser_2=cls)
        db_cls = getattr(model, cls)
        attributes = db_cls.__table__.columns.keys()
        for attribute in attributes:
            add_parser.add_argument('--' + attribute, type=str)


def main():
    root_parser = argparse.ArgumentParser()
    root_sub_parser = root_parser.add_subparsers(help=SUB_COMMAND_HELP)
    insert_add_sub_parser(root_sub_parser)
    args = root_parser.parse_args(None if sys.argv[1:] else ['-h'])
    print(args)
