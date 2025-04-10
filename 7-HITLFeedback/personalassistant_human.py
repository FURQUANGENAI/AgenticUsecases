import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from typing import List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage
import re

# Load environment variables
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY1")

# Use a supported Groq model
llm = ChatGroq(model="llama3-70b-8192")
result = llm.invoke("Hello, Furquan! How are you doing today?")
print(result)

# Define Models
class Analyst(BaseModel):
    affiliation: str = Field(description="Primary affiliation of the analyst.")
    name: str = Field(description="Name of the analyst.")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(description="Description of the analyst focus, concerns, and motives.")
    
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(description="Comprehensive list of analysts with their roles and affiliations.")

class GenerateAnalystsState(TypedDict):
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    human_analyst_feedback: str  # Human feedback
    analysts: List[Analyst]  # Analyst asking questions



# Analyst Instructions
analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts: 
{human_analyst_feedback}

3. Determine the most interesting themes based upon documents and / or feedback above.

4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme."""

# Node Functions
def create_analysts(state: GenerateAnalystsState):
    topic = state['topic']
    max_analysts = state['max_analysts']
    human_analyst_feedback = state.get('human_analyst_feedback', '')
    
    structured_llm = llm.with_structured_output(Perspectives)
    system_message = analyst_instructions.format(topic=topic, human_analyst_feedback=human_analyst_feedback, max_analysts=max_analysts)
    
    try:
        analysts = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate the set of analysts.")])
        return {"analysts": analysts.analysts}
    except Exception as e:
        st.error(f"Error generating analysts: {str(e)}")
        return {"analysts": []}

def human_feedback(state: GenerateAnalystsState):
    st.session_state.feedback = st.text_area("Provide feedback for the analysts (leave blank to finish):", key="feedback_input")
    return state

def should_continue(state: GenerateAnalystsState):
    human_analyst_feedback = state.get('human_analyst_feedback', None)
    if st.session_state.get('feedback', '').strip():
        return "create_analysts"
    return END

# Build Graph
builder = StateGraph(GenerateAnalystsState)
builder.add_node("create_analysts", create_analysts)
builder.add_node("human_feedback", human_feedback)
builder.add_edge(START, "create_analysts")
builder.add_edge("create_analysts", "human_feedback")
builder.add_conditional_edges("human_feedback", should_continue, ["create_analysts", END])

memory = MemorySaver()
graph = builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)

# Streamlit Interface
st.title("AI Analyst Persona Generator")
st.write("Generate analyst personas for a research topic with optional human feedback.")

with st.form("input_form"):
    topic = st.text_input("Enter the research topic:", value="The benefits of adopting Robotics in Physical AI framework")
    max_analysts = st.number_input("Number of analysts (max 5):", min_value=1, max_value=5, value=3)
    submitted = st.form_submit_button("Generate Analysts")

if submitted:
    thread = {"configurable": {"thread_id": str(hash(st.session_state.get("session_id", 0)))}}
    st.session_state.session_id = st.session_state.get("session_id", 0) + 1

    with st.spinner("Generating analysts..."):
        for event in graph.stream({"topic": topic, "max_analysts": max_analysts}, thread, stream_mode="values"):
            analysts = event.get("analysts", [])
            if analysts:
                st.subheader("Generated Analysts")
                for analyst in analysts:
                    st.markdown(f"### {analyst.name}")
                    st.text(analyst.persona)
                st.session_state.analysts = analysts

    if st.session_state.get("analysts"):
        with st.expander("Provide Feedback or Continue"):
            if st.button("Continue with Feedback"):
                feedback = st.session_state.feedback
                graph.update_state(thread, {"human_analyst_feedback": feedback}, as_node="human_feedback")
                st.experimental_rerun()

        if st.button("Finalize"):
            final_state = graph.get_state(thread)
            st.session_state.analysts = final_state.values.get('analysts', [])
            st.success("Analyst generation finalized!")
            st.experimental_rerun()

if st.session_state.get("analysts"):
    st.subheader("Final Analyst Personas")
    for analyst in st.session_state.analysts:
        st.markdown(f"### {analyst.name}")
        st.text(analyst.persona)