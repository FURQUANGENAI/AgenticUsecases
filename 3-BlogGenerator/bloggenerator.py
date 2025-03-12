import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langgraph.graph import StateGraph, END
from typing import TypedDict
from PIL import Image

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY1")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# Check API keys
if not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
    st.error("Missing API keys in .env file.")
    st.stop()

# Initialize LLM and search tool
llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0.7)
web_search = TavilySearchResults(max_results=3)

# Define state
class BlogState(TypedDict):
    topic: str
    research: str
    blog: str
    feedback: str

# Workflow nodes
def research_topic(state: BlogState) -> BlogState:
    topic = state["topic"]
    results = web_search.run(topic) or []
    research = "\n".join([r.get("content", "") for r in results if r.get("content")])
    if not research:
        research = "No info found."
    return {"research": research}

def write_blog(state: BlogState) -> BlogState:
    prompt = f"Write a short, engaging blog post on '{state['topic']}' using this info:\n{state['research']}"
    blog = llm.invoke(prompt).content
    return {"blog": blog}

def handle_feedback(state: BlogState) -> BlogState:
    feedback = state.get("feedback", "")
    if not feedback or "improve" not in feedback.lower():
        return state
    prompt = f"Refine this blog based on feedback '{feedback}':\n{state['blog']}"
    blog = llm.invoke(prompt).content
    return {"blog": blog}

# Build workflow (around line 54-56 in your file)
workflow = StateGraph(BlogState)
workflow.add_node("research_node", research_topic)  # Line ~54
workflow.add_node("write_node", write_blog)        # Line ~55 (renamed for consistency)
workflow.add_node("feedback_node", handle_feedback) # Line 56 (fixed from "feedback")
workflow.set_entry_point("research_node")
workflow.add_edge("research_node", "write_node")
workflow.add_edge("write_node", "feedback_node")
workflow.add_edge("feedback_node", END)
app = workflow.compile()

# Streamlit UI
st.title("Blog Generator using Langgraph - Agentic AI")
# Generate Workflow Graph

graph_png=app.get_graph(xray=True).draw_mermaid_png() 
with st.expander("View Workflow Graph - Furquan"):
    st.image(graph_png, caption="Blog Generator Workflow Graph", use_container_width=100)

st.write("Enter a topic to generate a blog post, I will search for you.")
topic = st.text_input("Blog Topic - eg : Benefits of Search & AI")
if st.button("Generate Blog") and topic:
    with st.spinner("Generating blog..."):
        initial_state = {"topic": topic, "research": "", "blog": "", "feedback": ""}
        result = app.invoke(initial_state)
        st.session_state.result = result
        st.subheader("Generated Blog after Searching the Web")
        st.write(result["blog"])

if "result" in st.session_state:
    with st.form(key="feedback_form"):
        feedback = st.text_area("Feedback (use 'improve' to refine, e.g., 'improve clarity'):", "")
        submit = st.form_submit_button("Submit your Feedback")
    if submit and feedback:
        with st.spinner("Updating blog after getting your Feedback..."):
            feedback_state = {**st.session_state.result, "feedback": feedback}
            updated_result = app.invoke(feedback_state)
            st.session_state.result = updated_result
            st.success("Your Feedback applied!")
            st.subheader("Updated Blog")
            st.write(updated_result["blog"])

if not topic:
    st.warning("Please enter a topic.")