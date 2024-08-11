# we can connect to locadb sqlite3 // MYSQL DB

import streamlit as st
import sqlite3

from pathlib import Path
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from langchain_groq import ChatGroq

st.set_page_config(page_title="Chat & CRUD with SQL DB", 
                   page_icon="🦜")
st.title(body="Chat & CRUD with SQL DB")

LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

# Let the user decide which DB to be used // local or MYSQL
options=["Use Sqlite3-my_demo.db", "MySQL Database"]
selected_opt=st.sidebar.radio(label="Choose a DB you want to chat with",
                             options=options)

# if selection is MySQL (options index=1)
if options.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("Enter MySQL Host")
    mysql_user=st.sidebar.text_input("Enter MySQL UserName")
    mysql_password=st.sidebar.text_input("Enter MySQL Password", type="password")
    mysql_db=st.sidebar.text_input("Enter MySQL DataBase Name")
else:
    local_sqldb_name=st.sidebar.text_input("Enter SQLite3 DataBase Name")
    db_uri=LOCALDB

# get the api key & Define model
groq_API=st.sidebar.text_input("Enter Groq API", type="password")

# Now user has decided that which db to be used 
# we have to create connection with it so that we can make a generic function

@st.cache_resource(ttl="2h")  # This will let functions content be with cache memory for 2 hours
def configure_DB(db_uri, sql_host=None, sql_user=None, sql_pass=None, sql_dbName=None):
    if db_uri==LOCALDB:
        db_filepath=(Path(__file__).parent/local_sqldb_name).absolute() #absolute path of local DB --> please set the path as per your local DB address
        creator=lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error(body="Please provide all MySQL details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if groq_API:
    llm=ChatGroq(model="Llama3-8b-8192", groq_api_key=groq_API, streaming=True)
    # lets connect with the DB
    if db_uri==MYSQL and groq_API:
        db=configure_DB(db_uri=db_uri, 
                        sql_host=mysql_host, 
                        sql_user=mysql_user, 
                        sql_pass=mysql_password,
                        sql_dbName=mysql_db)
    elif db_uri==LOCALDB and not local_sqldb_name:
        st.warning(body="Please enter valid sqlite3 database name")
    else:
        db=configure_DB(db_uri=db_uri)
               

    # Now we have connected to the DB
    # lets integrate our llm with DB
    # toolkit will combine the db data with llm & then by creating agent we can use it
    toolkit=SQLDatabaseToolkit(db=db, llm=llm)

    sql_agent=create_sql_agent(llm=llm,
                            toolkit=toolkit,
                            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                            verbose=True,
                            handle_parsing_errors=True)

    # session memory
    if "messages" not in st.session_state or st.sidebar.button(label="Clear the Chat history"):
        st.session_state["messages"]=[{"role":"Assistant", "content":"How can I help you"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_query=st.chat_input(placeholder="Ask anything from SQL DataBase")

    if user_query:
        st.session_state.messages.append({"role":"user", "content":user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("Assistant"):
            st_cb=StreamlitCallbackHandler(st.container())
            response=sql_agent.run(user_query, callbacks=[st_cb])
            st.session_state.messages.append({"role":"Assistant", "content":response})
            st.write(response)
else:
    st.warning(body="Please enter Groq API key")

