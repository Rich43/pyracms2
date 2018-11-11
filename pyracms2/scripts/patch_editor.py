import argparse
import sys

from dateutil.parser import parse

from ..models import model

SUB_COMMAND_HELP = 'sub-command --help'
SUB_PARSER = 'sub_parser_'
OBJ = '_obj'
CHOOSE_A_TABLE = ' (Choose a table to add a row to)'
ADD = 'add'


class Util:
    @staticmethod
    def iter_sub_classes(cls):
        return [x.__name__ for x in cls.__subclasses__()]

    @staticmethod
    def sub_parsers(args: argparse.Namespace):
        return {k: v for k, v in args.__dict__.items()
                if k.startswith(SUB_PARSER) and not k.endswith(OBJ)
                and v is not None}.items()

    @staticmethod
    def all_values_none(args: argparse.Namespace):
        return not any([v for k, v in args.__dict__.items()
                        if not k.startswith(SUB_PARSER)])

    @staticmethod
    def sql_alchemy_type_to_python_type(db_cls, attribute: str):
        try:
            python_type = getattr(db_cls, attribute).type.python_type
        except NotImplementedError:
            python_type = str
        if python_type.__name__ == 'datetime':
            python_type = parse
        return python_type

    @staticmethod
    def show_sub_parser_help(args: argparse.Namespace):
        sub_parser_length = len(Util.sub_parsers(args))
        if bool(sub_parser_length) and Util.all_values_none(args):
            parser = getattr(args, SUB_PARSER + str(sub_parser_length) + OBJ)
            parser.print_help()


class Parser:
    # noinspection PyProtectedMember
    def __init__(self, root_sub_parser: argparse._SubParsersAction):
        self.root_sub_parser = root_sub_parser

    # noinspection PyProtectedMember
    @staticmethod
    def add_parser_set_default(sub_parser: argparse._SubParsersAction,
                               name: str, level: int):
        add_parser = sub_parser.add_parser(name)
        add_parser.set_defaults(**{SUB_PARSER + str(level): name})
        add_parser.set_defaults(**{SUB_PARSER + str(level) + OBJ: add_parser})
        return add_parser

    def setup(self):
        self.insert_add_sub_parser()

    # noinspection PyProtectedMember
    def insert_add_sub_parser(self):
        root_add_parser = Parser.add_parser_set_default(self.root_sub_parser,
                                                        ADD, 1)
        add_sub_parser = root_add_parser.add_subparsers(
            help=SUB_COMMAND_HELP + CHOOSE_A_TABLE
        )
        for cls in Util.iter_sub_classes(model.Base):
            add_parser = Parser.add_parser_set_default(add_sub_parser, cls, 2)
            db_cls = getattr(model, cls)
            attributes = db_cls.__table__.columns.keys()
            for attribute in attributes:
                python_type = Util.sql_alchemy_type_to_python_type(
                    db_cls,
                    attribute
                )
                add_parser.add_argument('--' + attribute, type=python_type)


def main():
    root_parser = argparse.ArgumentParser()
    root_sub_parser = root_parser.add_subparsers(help=SUB_COMMAND_HELP)
    Parser(root_sub_parser).setup()
    args = root_parser.parse_args(None if sys.argv[1:] else ['-h'])
    Util.show_sub_parser_help(args)
