import streamlit as st
import pandas as pd
import numpy as np
import os
from langchain_openai.chat_models import ChatOpenAI
from research_flow.src.research_flow.main import ResearchFlow
from typing import Dict

st.title("🔍 Research Blog Assistant")

# Sidebar configuration
st.sidebar.header("🤖 Agents")

# Agent navigation in sidebar
selected_agent = st.sidebar.radio(
    "Select Agent",
    options=["Research Blog Assistant"], # "Content Writer", "SEO Analyzer"],
    key="agent_selector"
)

# Future agents can be added like this:
# if selected_agent == "New Agent":
#     st.sidebar.info("New Agent selected")

if selected_agent == "Content Writer":
    # Content Writer agent code
    pass
elif selected_agent == "SEO Analyzer":
    # SEO Analyzer agent code
    pass

output_folder = "./output"

def list_output_files():
    if os.path.exists(output_folder):
        files = [f for f in os.listdir(output_folder) if f.endswith('.md')]
        return sorted(files, key=lambda x: os.path.getmtime(os.path.join(output_folder, x)), reverse=True)
    return []

@st.cache_data
def run_research_flow(inputs: Dict):
    research_flow = ResearchFlow()
    research_flow.input_variables = inputs
    return research_flow.kickoff()

# Create tabs for Research and Results
tab1, tab2 = st.tabs(["Generate Research", "View Results"])

with tab1:
    # Create the main form
    with st.form("research_form"):
        topic = st.text_input("Research Topic", 
            placeholder="Enter the topic you want to research")
        
        audience_level = st.selectbox(
            "Audience Level",
            options=["junior", "mid-level", "senior"],
            index=0
        )
        
        research_context = st.text_area(
            "Additional Context",
            placeholder="Enter any additional context or requirements for the research"
        )

        submitted = st.form_submit_button("Start Research")
        
        if submitted:
            with st.spinner("Generating research..."):
                try:
                    input_variables = {
                        "topic": topic,
                        "audience_level": audience_level,
                        "research": research_context,
                        "output_folder": output_folder
                    }
                    
                    result = run_research_flow(input_variables)
                    st.success("Research completed successfully!")
                    
                    if result:
                        st.subheader("Generated Research")
                        st.write(result)
                        st.info(f"Research has been saved to: {output_folder}")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

with tab2:
    st.subheader("Previous Research Results")
    files = list_output_files()
    
    if not files:
        st.info("No research files found in the output directory.")
    else:
        selected_file = st.selectbox("Select a research file to view:", files)
        
        if selected_file:
            file_path = os.path.join(output_folder, selected_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                st.markdown(content)
                
                # Add download button
                st.download_button(
                    label="Download Research",
                    data=content,
                    file_name=selected_file,
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

