import os
import argparse
from splai.utils import find_project_root

def add_parser(subparsers):
    parser = subparsers.add_parser("init", help="Initialize a new Splai project with settings.")
    parser.add_argument("directory", nargs="?", default=".", help="Target directory for the .splai settings file (defaults to current directory).")
    parser.set_defaults(func=command)

def command(args):
    target_directory = args.directory
    # FIXME: Require --force if already exists in parent dir

    splai_file = os.path.join(target_directory, ".splai.yml")
    if os.path.exists(splai_file):
        print(f".splai.yml file already exists in {target_directory}")
    else:
        with open(splai_file, "w") as f:
            f.write("# Splai project settings\n")
        print(f"Created .splai.yml file in {target_directory}")