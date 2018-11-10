import argparse
from pyracms2.models import model


class ThrowAwayArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        pass

    def exit(self, status=0, message=None):
        pass


def iter_sub_classes(cls):
    return [x.__name__ for x in cls.__subclasses__()]


DESCRIPTION = 'Patch File Editor'
ARGUMENTS = [
    {'name': '--add', 'type': str,
     'choices': iter_sub_classes(model.Base), 'help': 'Add a row'}
]


def setup_argument_parser(arg_parser: argparse.ArgumentParser):
    for argument in ARGUMENTS:
        argument_copy = dict(argument)
        name = argument_copy['name']
        del argument_copy['name']
        arg_parser.add_argument(name, **argument_copy)


def main():
    dummy_parser = ThrowAwayArgumentParser()
    setup_argument_parser(dummy_parser)
    args = dummy_parser.parse_args()

    if args.add:
        parser = argparse.ArgumentParser(DESCRIPTION)
        cls = getattr(model, args.add)
        attributes = cls.__table__.columns.keys()
        attributes_sub_parser = root_parser.add_subparsers()
        attributes_parser = attributes_sub_parser.add_parser('attributes')
        for attribute in attributes:
            attributes_parser.add_argument('--' + attribute, type=str,
                                           help=attribute)

    root_parser.parse_args()