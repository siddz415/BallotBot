import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

# Load environment variables
load_dotenv()

# Set up Anthropic LLM
Settings.llm = Anthropic(model="claude-3-5-sonnet-20240620")

# Read the content of SFCA_propositions.txt
with open('data/SFCA_propositions.txt', 'r') as file:
    propositions_data = file.read()

# Create system prompt
system_prompt = f"""You are a helpful voter's assistant for San Francisco, California. Your role is to provide information about different propositions that voters can vote for in their area. Use the following information about current propositions:

{propositions_data}

When responding to queries about propositions, you should:

1. Explain what the proposition is about
2. Describe the current situation (before the proposition)
3. Describe what would change if the proposition passes (after)
4. List the pros and cons of the proposition

Always strive to provide balanced, factual information to help voters make informed decisions. If you're unsure about any details or if a proposition is not listed in the provided information, say so clearly."""

# Streamlit app
st.title("Voter's Proposition Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter a proposition or topic you'd like to learn about:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "human", "content": prompt})
    
    # Display user message
    with st.chat_message("human"):
        st.markdown(prompt)

    # Prepare the full conversation history for the LLM
    conversation = system_prompt + "\n\n"
    for message in st.session_state.messages:
        conversation += f"{message['role'].capitalize()}: {message['content']}\n\n"
    conversation += "Assistant:"

    # Get response from LLM
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in Settings.llm.stream_complete(conversation):
            full_response += response.delta
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add some instructions for the user
st.sidebar.header("How to use")
st.sidebar.write("""
1. Enter the name or topic of a proposition you're interested in.
2. The assistant will provide information about the proposition, including:
   - What it's about
   - The current situation
   - What would change if it passes
   - Pros and cons
3. You can ask follow-up questions or inquire about different propositions.
4. Use this information to help make an informed decision!
""")