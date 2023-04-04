import argparse, os, re
from git import Repo
from splai.utils import find_project_root
from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader

def add_parser(subparsers):
    parser = subparsers.add_parser("knowledge", help="Index and query knowledge from the repo.")
    knowledge_subparsers = parser.add_subparsers(dest="knowledge_subcommand")

    # Index subcommand
    index_parser = knowledge_subparsers.add_parser("index", help="Manage the knowledge index.")
    index_subparsers = index_parser.add_subparsers(dest="index_subcommand")

    # Update subcommand under index
    update_parser = index_subparsers.add_parser("update", help="Update the knowledge index.")
    update_parser.set_defaults(func=command)

    # Rename 'get' to 'fetch'
    fetch_parser = knowledge_subparsers.add_parser("fetch", help="Download a git repo into the knowledge cache.")
    fetch_parser.add_argument("name", help="Name of the knowledge item.")
    fetch_parser.add_argument("source", help="Source git repository URL.")
    fetch_parser.add_argument("--tag", default=None, help="Optional git tag to clone (defaults to main/master).")
    fetch_parser.set_defaults(func=command)

def command(args):
    if args.knowledge_subcommand == "index" and args.index_subcommand == "update":
        index_update(args)
    elif args.knowledge_subcommand == "fetch":
        fetch(args.name, args.source, args.tag)
    else:
        print("Invalid option. Use 'index update' to update the knowledge index, or 'fetch' to download a git repo.")

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

def fetch(name, source, tag):
    project_root = find_project_root()
    target_dir = os.path.join(project_root, ".splai", "knowledge", "cache", name)
    os.makedirs(target_dir, exist_ok=True)

    source = github_to_git_url(source)

    if not tag:
        tag = "master"

    print(f"Cloning '{source}' to '{target_dir}'")
    repo = Repo.clone_from(source, target_dir, depth=1, branch=tag)
    print(f"Knowledge '{name}' downloaded from {source} to {target_dir}")

def index_update(args):
    project_root = find_project_root()

    knowledge_file = os.path.join(project_root, "knowledge.txt")
    loader = TextLoader(knowledge_file)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
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