import argparse
import sys

from pyracms2.models import model

SUB_COMMAND_HELP = 'sub-command --help'


def iter_sub_classes(cls):
    return [x.__name__ for x in cls.__subclasses__()]


# noinspection PyProtectedMember
def insert_add_sub_parser(sub_parser: argparse._SubParsersAction):
    add_parser = sub_parser.add_parser('add')
    add_help = " (Choose a table to add a row to)"
    add_sub_parser = add_parser.add_subparsers(help=SUB_COMMAND_HELP + add_help)
    for cls in iter_sub_classes(model.Base):
        add_parser = add_sub_parser.add_parser(cls)
        db_cls = getattr(model, cls)
        attributes = db_cls.__table__.columns.keys()
        for attribute in attributes:
            add_parser.add_argument('--' + attribute, type=str)


def main():
    root_parser = argparse.ArgumentParser()
    root_sub_parser = root_parser.add_subparsers(help=SUB_COMMAND_HELP)
    insert_add_sub_parser(root_sub_parser)
    root_parser.parse_args(None if sys.argv[1:] else ['-h'])
