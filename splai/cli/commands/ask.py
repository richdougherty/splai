from functools import partial
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAIChat
from langchain.agents.agent_toolkits import (
    create_vectorstore_router_agent,
    VectorStoreRouterToolkit,
    VectorStoreInfo,
)
from splai.utils import find_project_root

def ask_command(args):
    project_root = find_project_root()
    splai_directory = os.path.join(project_root, ".splai")
    chromadb_directory = os.path.join(splai_directory, "chromadb")

    llm = OpenAIChat(temperature=0)
    embeddings = OpenAIEmbeddings()

    collection_name = "knowledge-file"
    vectorstore = Chroma(embedding_function=embeddings,
                         persist_directory=chromadb_directory,
                         collection_name=collection_name)


    vectorstore_info = VectorStoreInfo(
        name=collection_name,
        description=f"Collection for {collection_name}",
        vectorstore=vectorstore,
    )
    router_toolkit = VectorStoreRouterToolkit(
        vectorstores=[vectorstore_info],
        llm=llm,
    )

    # Create a vectorstore router agent
    agent_executor = create_vectorstore_router_agent(
        llm=llm,
        toolkit=router_toolkit,
        verbose=True,
    )

    # Run a query
    answer = agent_executor.run(args.question)
    print(answer)

def add_parser(subparsers):
    parser = subparsers.add_parser("ask", help="Ask a question to the agent")
    parser.add_argument("question", help="Question to ask the agent")
    parser.set_defaults(command_func=ask_command)