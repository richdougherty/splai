import os, re, sys, yaml
import hashlib
import requests
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
from git import Repo
from splai.cli.errors import CLIError
from splai.utils import find_project_root
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

def add_parser(subparsers):
    knowledge_parser = subparsers.add_parser("knowledge", help="Index and query knowledge from the repo.", aliases=["know", "kn"])
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_subcommand")

    # Add subcommand
    add_parser = knowledge_subparsers.add_parser("add", help="Add a new knowledge source.")
    add_parser.add_argument("url", help="URL of the knowledge source.")
    add_parser.set_defaults(command_func=lambda args: add_knowledge_url(args.url))

    # Index subcommand
    index_parser = knowledge_subparsers.add_parser("index", help="Manage the knowledge index.")
    index_subparsers = index_parser.add_subparsers(dest="index_subcommand")

    # Update subcommand under index
    update_parser = index_subparsers.add_parser("update", help="Update the knowledge index.")
    update_parser.set_defaults(command_func=lambda args: index_update(args))

    # Rename 'get' to 'fetch'
    fetch_parser = knowledge_subparsers.add_parser("fetch", help="Fetch knowledge sources by name or all sources from .splai.yml.")
    fetch_group = fetch_parser.add_mutually_exclusive_group(required=True)
    fetch_group.add_argument("name", nargs='?', help="Name of the knowledge source.")
    fetch_group.add_argument("--all", action="store_true", help="Fetch all knowledge sources from .splai.yml.")
    def fetch_command(args):
        if args.name:
            fetch_by_name(args.name)
        elif args.all:
            fetch_all()
    fetch_parser.set_defaults(command_func=fetch_command)

# Helper for URLs
def github_to_git_url(url):
    # Check if the input is a Git URL
    if re.match(r'git@(.*):(.*)/(.*).git', url):
        return url
    
    # If the input is a Github URL, extract the org and repo name
    match = re.match(r'https://github.com/([^/]+)/([^/]+)', url)
    if match:
        org = match.group(1)
        repo = match.group(2)
        return f'git@github.com:{org}/{repo}.git'
    
    # If the input is not a Git or Github URL, raise an exception
    raise ValueError(f'Invalid URL: {url}')

# TODO: Move to utils.py
def load_config():
    project_root = find_project_root()
    splai_yml_path = os.path.join(project_root, ".splai.yml")
    
    with open(splai_yml_path, 'r') as yml_file:
        config = yaml.safe_load(yml_file)
    if config is None:
        config = {}
    return config

def load_knowledge_sources():
    config = load_config()
    return config.get('knowledge', {}).get('sources', [])


def add_knowledge_url(url):
    project_root = find_project_root()
    splai_config_path = os.path.join(project_root, ".splai.yml")

    # Load existing configuration
    config = load_config()
    sources = config.setdefault('knowledge', {}).setdefault('sources', [])

    if any(source.get("url") == url for source in sources):
        raise CLIError(f"Error: Knowledge source URL '{url}' is already in .splai.yml")
    
    sources.append({"url": url})

    # Save the updated configuration
    with open(splai_config_path, "w") as f:
        yaml.safe_dump(config, f)

    print(f"Knowledge source URL '{url}' added to .splai.yml")

def fetch_by_name(name):
    sources = load_knowledge_sources()
    source = next((s for s in sources if s.get("name") == name), None)
    
    if source is None:
        print(f"Error: Knowledge source '{name}' not found in .splai.yml")
        return

    if "url" in source:
        fetch_url(source["url"])
    else:
        print(f"Error: Unsupported knowledge source type for '{name}'")

def fetch_all():
    sources = load_knowledge_sources()
    
    for source in sources:
        source_name = source.get("name", "<unknown>")
        if "url" in source:
            fetch_url(source["url"])
        else:
            print(f"Error: Unsupported knowledge source type for '{source_name}'")

def fetch_url(url):
    project_root = find_project_root()
    urls_directory = os.path.join(project_root, ".splai", "knowledge", "urls")
    Path(urls_directory).mkdir(parents=True, exist_ok=True)
    
    # Generate hash of URL for the filename
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    
    # Fetch the content and determine the mimetype
    response = requests.get(url)
    response.raise_for_status()
    mimetype = response.headers.get("Content-Type", "text/plain")
    main_mimetype = mimetype.split(";")[0].strip()

    # Determine the file extension based on the mimetype
    extension = mimetypes.guess_extension(main_mimetype) or "txt"

    # Save the content to the file
    target_path = os.path.join(urls_directory, f"{url_hash}{extension}")
    with open(target_path, "wb") as target_file:
        target_file.write(response.content)

    print(f"Fetched URL '{url}' and saved to '{target_path}'")

def index_update(args):
    project_root = find_project_root()

    project_root = find_project_root()
    urls_directory = os.path.join(project_root, ".splai", "knowledge", "urls")

    # loader = DirectoryLoader(urls_directory)
    # TODO: Metadata

    # loader = UnstructuredHTMLLoader("example_data/fake-content.html")

    knowledge_file = os.path.join(project_root, "knowledge.txt")
    loader = TextLoader(knowledge_file)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=0)
    split_documents = text_splitter.split_documents(documents)

    # Create embeddings and Chroma vectorstore
    embeddings = OpenAIEmbeddings()
    collection_name = "knowledge-file"
    splai_directory = os.path.join(project_root, ".splai")
    chromadb_directory = os.path.join(splai_directory, "chromadb")
    vectorstore = Chroma.from_documents(embedding=embeddings,
                                        persist_directory=chromadb_directory,
                                        collection_name=collection_name,
                                        documents=split_documents)

    print(f"Embeddings updated and stored in {chromadb_directory}")