import argparse

def add_parser(subparsers):
    parser = subparsers.add_parser("refactor", help="Refactor a method in a given file.")
    parser.add_argument("filename", help="File containing the method to refactor.")
    parser.add_argument("method", help="Name of the method to refactor.")
    parser.set_defaults(func=command)

def command(args):
    filename = args.filename
    method = args.method
    print(f"Refactoring method '{method}' in file '{filename}'")
