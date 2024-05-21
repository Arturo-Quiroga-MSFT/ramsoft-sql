# Import necessary libraries and modules
import os
from dotenv import load_dotenv
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from langchain_community.chat_models import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.agents import AgentType, create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables using os.getenv
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL")
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DB = os.getenv("SQL_DB")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PWD = os.getenv("SQL_PWD")


# Define the ODBC connection string for the SQL Server database
driver = '{ODBC Driver 18 for SQL Server}'
odbc_str = 'mssql+pyodbc:///?odbc_connect=' \
                'Driver='+driver+ \
                ';Server=tcp:' + os.getenv("SQL_SERVER") + \
                ';DATABASE=' + os.getenv("SQL_DB") + \
                ';Uid=' + os.getenv("SQL_USERNAME")+ \
                ';Pwd=' + os.getenv("SQL_PWD") + \
                ';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=60;'


# Create a SQLAlchemy engine object for the SQL Server database
db_engine = create_engine(odbc_str)

# Create an Azure OpenAI chatbot object for natural language processing
llm = AzureChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL"),
                      deployment_name=os.getenv("OPENAI_CHAT_MODEL"),
                      temperature=0)


# Create a SQL database agent using the Azure OpenAI chatbot and the SQLDatabaseToolkit
db = SQLDatabase(db_engine, schema="hospitaldb")
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sqldb_agent = create_sql_agent(
    llm=llm,
    toolkit=sql_toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Define Streamlit app
def app():
    # Set the title and logo of the Streamlit app
    st.title("Testing of SQL Query Tool")
    st.image("https://biendata.xyz/media/7c92a358-84ff-4d88-b44b-33861780b703_logo.png", use_column_width=True)
    
    # Prompt the user to enter a question and provide a text input field
    st.write("Enter your question below and click 'Submit' to get an answer.")
    question = st.text_input("Question:")
    
    # When the user clicks the "Submit" button, generate a response using the SQL database agent
    if st.button("Submit"):
        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", 
                 """
                 You are a helpful AI assistant expert in querying a sql hospitaldb Database to find answers to user's questions. Your primary focus is on the findings 
                 contained in the Reports column of the Patients table. You can provide information about the patients and reports in the hospitaldb Database.
                 """
                ),
                ("user", f"{question}\n ai: "),
            ]
        )
        response = sqldb_agent.run(final_prompt)
        
        # Display the response in the Streamlit app's output area
        st.write("Output:")
        st.write(response)

# Run the Streamlit app
if __name__ == "__main__":
    app()
