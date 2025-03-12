import os
import streamlit as st
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_groq import ChatGroq
from duckduckgo_search import DDGS

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY1")
langsmith_api_key = os.getenv("LANGCHAIN_API_KEY")

# Check for required API keys
if not groq_api_key:
    st.error("Missing GROQ_API_KEY in .env file.")
    st.stop()
if not langsmith_api_key:
    st.error("Missing LANGSMITH_API_KEY in .env file.")
    st.stop()

# Initialize LangSmith tracing and Groq LLM
os.environ["LANGCHAIN_TRACING_V2"] = "true"  # Enable tracing
os.environ["LANGCHAIN_PROJECT"] = "MarketingCampaign"
os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key  # Set LangSmith API key
llm = ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768", temperature=0)

# Define state
class CampaignState(TypedDict):
    topic: str
    ideas: str
    research: str
    draft: str
    final_post: str

# Workflow nodes
def generate_ideas(state: CampaignState) -> CampaignState:
    prompt = f"Brainstorm 3 creative marketing campaign ideas for {state['topic']}."
    response = llm.invoke(prompt)
    return {"ideas": response.content}

def research_audience(state: CampaignState) -> CampaignState:
    with DDGS() as ddgs:
        query = f"{state['topic']} target audience trends 2025"
        results = ddgs.text(query, max_results=3)
        research = "\n".join([r["body"] for r in results]) or "No research found."
    return {"research": research}

def draft_content(state: CampaignState) -> CampaignState:
    prompt = f"Write a draft marketing blog post for {state['topic']} using these ideas:\n{state['ideas']}\nand this research:\n{state['research']}"
    response = llm.invoke(prompt)
    return {"draft": response.content}

def synthesize_post(state: CampaignState) -> CampaignState:
    prompt = f"Refine this draft into a polished 300-word marketing blog post:\n{state['draft']}"
    response = llm.invoke(prompt)
    return {"final_post": response.content}

# Build workflow
workflow = StateGraph(CampaignState)
workflow.add_node("idea_node", generate_ideas)
workflow.add_node("research_node", research_audience)
workflow.add_node("draft_node", draft_content)
workflow.add_node("synthesize_node", synthesize_post)
workflow.set_entry_point("idea_node")
workflow.add_edge("idea_node", "research_node")
workflow.add_edge("research_node", "draft_node")
workflow.add_edge("draft_node", "synthesize_node")
workflow.add_edge("synthesize_node", END)
app = workflow.compile()

# Streamlit UI
st.title("Marketing Campaign Generator using architecture of orchestrator and synthesizer")
st.write("Enter a topic to create a blog post .")
topic = st.text_input("Campaign Topic", "Eco-Friendly Products")

if st.button("Generate"):
    with st.spinner("Creating content..."):
        initial_state = {"topic": topic, "ideas": "", "research": "", "draft": "", "final_post": ""}
        result = app.invoke(initial_state)
        st.subheader("Ideas")
        st.write(result["ideas"])
        st.subheader("Research")
        st.write(result["research"])
        st.subheader("Draft")
        st.write(result["draft"])
        st.subheader("Final Post")
        st.write(result["final_post"])
    


    # Display LangSmith debug link
    st.write("Debug this run in LangSmith:")
    st.markdown("[View Trace](https://smith.langchain.com/projects/p/MarketingCampaign?tab=runs)")

    
