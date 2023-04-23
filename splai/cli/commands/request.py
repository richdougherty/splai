import os
from splai.utils import find_project_root
from langchain.agents import initialize_agent, load_tools
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAIChat
from langchain.tools.vectorstore.tool import VectorStoreQATool
from langchain.vectorstores import Chroma

def add_parser(subparsers):
    parser = subparsers.add_parser("request", aliases=["req"], help="Request the agent to perform an action.")
    parser.add_argument("question_or_task", help="The question or task for the agent to perform.")
    parser.set_defaults(command_func=request_command)

def request_command(args):
    perform_request(args.question_or_task)

def perform_request(question_or_task):
    # Replace this with the actual logic for performing the request
    print(f"Request: {question_or_task}")

    # First, let's load the language model we're going to use to control the agent.
    llm = OpenAIChat(temperature=0)
 
    embeddings = OpenAIEmbeddings()

    collection_name = "knowledge-file"

    project_root = find_project_root()
    splai_directory = os.path.join(project_root, ".splai")
    chromadb_directory = os.path.join(splai_directory, "chromadb")
    vectorstore = Chroma(embedding_function=embeddings,
                         persist_directory=chromadb_directory,
                         collection_name=collection_name)


    vectorstore_tool = VectorStoreQATool(
        name=collection_name,
        description=VectorStoreQATool.get_description(
            name=collection_name,
            description="Useful knowledge"
        ),
        vectorstore=vectorstore,
        llm=llm,
    )

    tools = load_tools(["llm-math"], llm=llm) + [vectorstore_tool]


    # Finally, let's initialize an agent with the tools, the language model, and the type of agent we want to use.
    agent = initialize_agent(tools, llm, agent="chat-zero-shot-react-description", verbose=True)

    # Now let's test it out!
    agent.run(question_or_task)
