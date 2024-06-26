import requests
import os
import pandas as pd
from uuid import uuid4

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate

from langchain.llms import OpenAI, AzureOpenAI
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

# Setup variables
## Project Info
PROJECT_ID = "qa-agent-424215"
DATASET = "pnad"
TABLE = "populacao"
GLOSSARY_IDS = ['testen7cumnz', 'termos_trabalhistasq4uulp4']
## load the API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(openai_api_key=openai_api_key)
chat_llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.4)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Get glossary details
def list_glossary_terms(project_id, location_id, glossary_id):
    client = dataplex_v1.DataTaxonomyServiceClient()
    glossary_path = client.data_taxonomy_path(project = project_id, location=location_id, data_taxonomy_id=glossary_id)
    print(glossary_path)
    glossary_name = f"projects/{project_id}/locations/{location_id}/dataTaxonomies/{glossary_id}"
    request = dataplex_v1.ListDataAttributesRequest(
        parent=glossary_path
    )
    response = client.list_data_attributes(request=request)
    for term in response:
        print(f"Term: {term.display_name}")
        print(f"Description: {term.description}")
for glossary_id in glossary_ids:
    list_glossary_terms(project_id, location_id, glossary_id)

# Get dataset details
def get_basic_table_details(cursor):
    cursor.execute(f"""
      SELECT table_name, column_name, data_type, description
      FROM `{PROJECT_ID}.{DATASET}`.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS
    );""")
    tables_and_columns = cursor.fetchall()
    return tables_and_columns

def get_the_output_from_llm(query, unique_id, db_uri):
    ## Load the tables csv
    filename_t = 'csvs/tables_' + unique_id + '.csv'
    df = pd.read_csv(filename_t)

    ## For each relevant table create a string that list down all the columns and their data types
    table_info = ''
    for table in df['table_name']:
        table_info += 'Information about table' + table + ':\n'
        table_info += df[df['table_name'] == table].to_string(index=False) + '\n\n\n'

    return generate_template_for_sql(query, table_info, db_uri)
  
# Define metric
def generate_template_for_sql(query, table_info, db_uri):
    template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        f"You are an assistant that can write SQL Queries."
                        f"Given the text below, write a SQL query that answers the user's question."
                        f"DB connection string is {db_uri}"
                        f"Here is a detailed description of the table(s): "
                        f"{table_info}"
                        "Prepend and append the SQL query with three backticks '```'"
                        
                        
                    )
                ),
                HumanMessagePromptTemplate.from_template("{text}"),

            ]
        )
    
    answer = chat_llm(template.format_messages(text=query))
    return answer.content

# Generate SQL

# Check validity

# Fetch data

# Format data

# Run function and return value

def save_db_details(db_uri):
    unique_id = str(uuid4()).replace("-", "_")
    connection = psycopg2.connect(db_uri)
    cursor = connection.cursor()

    tables_and_columns = get_basic_table_details(cursor)

    ## Get all the tables and columns and enter them in a pandas dataframe
    df = pd.DataFrame(tables_and_columns, columns=['table_name', 'column_name', 'data_type'])
    filename_t = 'csvs/tables_' + unique_id + '.csv'
    df.to_csv(filename_t, index=False)

    cursor.close()
    connection.close()

    return unique_id
















def execute_the_solution(solution, db_uri):
    connection = psycopg2.connect(db_uri)
    cursor = connection.cursor()
    _,final_query,_ = solution.split("```") 
    final_query = final_query.strip('sql')
    cursor.execute(final_query)
    result = cursor.fetchall()
    return str(result)





# Function to establish connection and read metadata for the database
def connect_with_db(uri):
    st.session_state.db_uri = uri
    st.session_state.unique_id = save_db_details(uri)

    return {"message": "Connection established to Database!"}

# Function to call the API with the provided URI
def send_message(message):
    solution = get_the_output_from_llm(message, st.session_state.unique_id, st.session_state.db_uri)
    result = execute_the_solution(solution, st.session_state.db_uri)
    return {"message": solution + "\n\n" + "Result:\n" + result}



# ## Instructions
st.subheader("Instructions")
st.markdown(
    """
    1. Enter the URI of your RDS Database in the text box below.
    2. Click the **Start Chat** button to start the chat.
    3. Enter your message in the text box below and press **Enter** to send the message to the API.
    """
)

# Initialize the chat history list
chat_history = []

# Input for the database URI
uri = st.text_input("Enter the RDS Database URI")

if st.button("Start Chat"):
    if not uri:
        st.warning("Please enter a valid database URI.")
    else:
        st.info("Connecting to the API and starting the chat...")
        chat_response = connect_with_db(uri)
        if "error" in chat_response:
            st.error("Error: Failed to start the chat. Please check the URI and try again.")
        else:
            st.success("Chat started successfully!")

# Chat with the API (a mock example)
st.subheader("Chat with the API")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # response = f"Echo: {prompt}"
    response = send_message(prompt)["message"]
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Run the Streamlit app
if __name__ == "__main__":
    st.write("This is a simple Streamlit app for starting a chat with an RDS Database.")
