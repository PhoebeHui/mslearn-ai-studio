import os
import openai

# Add references
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')
        
    try: 
    
        # Get configuration settings 
        load_dotenv()
        project_connection = os.getenv("PROJECT_CONNECTION")
        model_deployment =  os.getenv("MODEL_DEPLOYMENT")
        
        # Initialize the project client
        projectClient = AIProjectClient.from_connection_string(
            conn_str=project_connection,
            credential=DefaultAzureCredential())

        ## Get a chat client
       # chat = projectClient.inference.get_chat_completions_client()
        openai_client = projectClient.inference.get_azure_openai_client(api_version="2024-10-21")

        ## Initialize prompt with system message
        # prompt=[
        #          SystemMessage("You are a helpful AI assistant that answers questions.")
        #     ]
        prompt=[
                {"role": "system", "content": "You are a helpful AI assistant that answers questions."}
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
            
            # Get a chat completion
            # prompt.append(UserMessage(input_text))
            # response = chat.complete(
            #     model=model_deployment,
            #     messages=prompt)
            # completion = response.choices[0].message.content
            # print(completion)
            # prompt.append(AssistantMessage(completion))

            prompt.append({"role": "user", "content": input_text})
            response = openai_client.chat.completions.create(
                 model=model_deployment,
                 messages=prompt)
            completion = response.choices[0].message.content
            print(completion)
            prompt.append({"role": "assistant", "content": completion})
    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
