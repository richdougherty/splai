#!/usr/bin/env python3

import argparse
import sys
from splai.cli.commands import __all__ as commands
from splai.cli.errors import CLIError

def main():
    parser = argparse.ArgumentParser(description="AI helper.")
    subparsers = parser.add_subparsers(dest="subcommand")

    for command in commands:
        command.add_parser(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'command_func'):
        try:
            args.command_func(args)
        except CLIError as e:
            print(e)
            sys.exit(e.exit_code)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
