This is a project for experimenting with AI tools for use in software
development projects. It uses the LangChain library and OpenAI APIs.

# Usage

1. Install the [Poetry](https://python-poetry.org/) tool into your
   environment.

2. Enter the `splai` directory.

3. Install Splai's dependencies using Poetry.
   ```bash
   $ poetry install
   ```

5. Enter a shell with the correct Python environment using Poetry.
   ```bash
   $ poetry shell
   ```

6. Set up your OpenAI key in the environment.
   ```bash
   $ export OPENAI_API_KEY='...'
   ```

6. Index the knowledge in the repository into a local vector database.
   ```bash
   $ ./splai.sh knowledge index update
   ```

7. Run the `ask` command to query Splai about this project.
   ```bash
   $ ./splai.sh ask "What's this project called?"
   ...
   The name of the project is splai.
   ```