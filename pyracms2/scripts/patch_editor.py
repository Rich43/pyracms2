import argparse
import sys

from dateutil.parser import parse

from ..models import model

SUB_COMMAND_HELP = 'sub-command --help'
SUB_PARSER = 'sub_parser_'
OBJ = '_obj'


def iter_sub_classes(cls):
    return [x.__name__ for x in cls.__subclasses__()]


# noinspection PyProtectedMember
def add_parser_set_default(sub_parser: argparse._SubParsersAction, name: str,
                           level: int):
    add_parser = sub_parser.add_parser(name)
    add_parser.set_defaults(**{SUB_PARSER + str(level): name})
    add_parser.set_defaults(**{SUB_PARSER + str(level) + OBJ: add_parser})
    return add_parser


def sql_alchemy_type_to_python_type(db_cls, attribute: str):
    try:
        python_type = getattr(db_cls, attribute).type.python_type
    except NotImplementedError:
        python_type = str
    if python_type.__name__ == 'datetime':
        python_type = parse
    return python_type


# noinspection PyProtectedMember
def insert_add_sub_parser(sub_parser: argparse._SubParsersAction):
    root_add_parser = add_parser_set_default(sub_parser, 'add', 1)
    add_sub_parser = root_add_parser.add_subparsers(
        help=SUB_COMMAND_HELP + ' (Choose a table to add a row to)'
    )
    for cls in iter_sub_classes(model.Base):
        add_parser = add_parser_set_default(add_sub_parser, cls, 2)
        db_cls = getattr(model, cls)
        attributes = db_cls.__table__.columns.keys()
        for attribute in attributes:
            python_type = sql_alchemy_type_to_python_type(db_cls, attribute)
            add_parser.add_argument('--' + attribute, type=python_type)


def sub_parsers(args: argparse.Namespace):
    return {k: v for k, v in args.__dict__.items()
            if k.startswith(SUB_PARSER) and not k.endswith(OBJ)
            and v is not None}.items()


def all_values_none(args: argparse.Namespace):
    return not any([v for k, v in args.__dict__.items()
                    if not k.startswith(SUB_PARSER)])


def main():
    root_parser = argparse.ArgumentParser()
    root_sub_parser = root_parser.add_subparsers(help=SUB_COMMAND_HELP)
    insert_add_sub_parser(root_sub_parser)
    args = root_parser.parse_args(None if sys.argv[1:] else ['-h'])
    sub_parser_length = len(sub_parsers(args))
    if bool(sub_parser_length) and all_values_none(args):
        parser = getattr(args, SUB_PARSER + str(sub_parser_length) + OBJ)
        parser.print_help()
