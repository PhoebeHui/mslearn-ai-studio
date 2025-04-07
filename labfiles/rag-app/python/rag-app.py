import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
import openai

def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get configuration settings
        load_dotenv()
        project_connection = os.getenv("PROJECT_CONNECTION")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")
        index_name = os.getenv("INDEX_NAME")

        # Initialize the project client
        projectClient = AIProjectClient.from_connection_string(
            conn_str=project_connection,
            credential=DefaultAzureCredential()
        )

        # Use the AI search service connection to get service details
        searchConnection = projectClient.connections.get_default(
            connection_type=ConnectionType.AZURE_AI_SEARCH,
            include_credentials=True,
        )
        search_url = searchConnection.endpoint_url
        search_key = searchConnection.key

        # Get an Azure OpenAI chat client
        aoai_client = projectClient.inference.get_azure_openai_client(api_version="2024-10-21")

        # Initialize prompt with system message
        prompt = [
            {"role": "system", "content": "You are a travel assistant that provides information on travel services available from Margie's Travel."}
        ]

        # Loop until the user types 'quit'
        while True:
            # Get input text
            input_text = input("Enter the prompt (or type 'quit' to exit): ")
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Add the user input message to the prompt
            prompt.append({"role": "user", "content": input_text})

            # Additional parameters to apply RAG pattern using the AI Search index
            rag_params = {
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": search_url,
                            "index_name": index_name,
                            "authentication": {
                                "type": "api_key",
                                "key": search_key,
                            }
                        }
                    }
                ],
            }

            # Submit the prompt with the data source options and display the response
            response = aoai_client.chat.completions.create(
                model=model_deployment,
                messages=prompt,
                extra_body=rag_params
            )
            completion = response.choices[0].message.content
            print(completion)

            # Add the response to the chat history
            prompt.append({"role": "assistant", "content": completion})

    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    main()