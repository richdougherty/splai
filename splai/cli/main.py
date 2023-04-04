#!/usr/bin/env python3

import argparse
from splai.cli.commands import __all__ as commands

def main():
    parser = argparse.ArgumentParser(description="AI helper.")
    subparsers = parser.add_subparsers(dest="subcommand")

    for command in commands:
        command.add_parser(subparsers)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)

if __name__ == "__main__":
    main()
