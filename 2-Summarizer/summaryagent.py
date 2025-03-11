import fitz  # PyMuPDF for PDF handling
import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
if not os.environ["OPENAI_API_KEY"]:
    st.error("OPENAI_API_KEY not found in .env file.")
    st.stop()

# Define state for LangGraph
class SummaryState(TypedDict):
    input_path: str  # Path to PDF or text input
    text_content: Annotated[Sequence[str], "Extracted text"]
    summary: Annotated[str, "Generated summary"]

# Node 1: Extract text from input (PDF or text)
def extract(state: SummaryState) -> SummaryState:
    try:
        if state["input_path"].endswith(".pdf"):
            doc = fitz.open(state["input_path"])
            text_content = [page.get_text("text").strip() for page in doc]
            doc.close()
        else:
            text_content = [state["input_path"]]  # Treat as raw text input
        return {"text_content": text_content}
    except Exception as e:
        st.error(f"Extraction failed: {e}")
        return {"text_content": ["No text extracted"]}

# Node 2: Summarize the text
def summarize(state: SummaryState) -> SummaryState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(
        "Summarize this text concisely:\n\n{text}\n\nSummary:"
    )
    text = " ".join(state["text_content"]) or "No text to summarize"
    summary = llm.invoke(prompt.format(text=text)).content.strip()
    return {"summary": summary}

# Build LangGraph workflow
workflow = StateGraph(SummaryState)
workflow.add_node("extract", extract)
workflow.add_node("summarize", summarize)
workflow.set_entry_point("extract")
workflow.add_edge("extract", "summarize")
workflow.add_edge("summarize", END)
app = workflow.compile()

# Streamlit UI
def main():
    st.title("Summarizer Agent - Created by Furquan")
    st.write("Upload a PDF or enter TEXT to get a summary.")
# Display the workflow graph
    st.subheader("Workflow Graph")
    try:
        graph_png = app.get_graph(xray=True).draw_mermaid_png()  # Generate PNG with detailed view
        st.image(graph_png, caption="Summarizer Workflow", use_container_width=250)
    except Exception as e:
        st.error(f"Failed to render graph: {e}")
        st.write("Ensure Graphviz is installed: `pip install graphviz` and system package (e.g., `sudo apt install graphviz`)")
        st.text("Workflow: extract → summarize → end")

    # Input options
    input_type = st.radio("Choose input type:", ("PDF", "Text"))
    input_content = None
    
    if input_type == "PDF":
        uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
        if uploaded_file:
            pdf_path = f"temp_{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            input_content = pdf_path
    else:
        input_content = st.text_area("Enter text to summarize", height=200)

    if input_content and st.button("Summarize"):
        with st.spinner("Generating summary..."):
            # Run the workflow
            result = app.invoke({
                "input_path": input_content,
                "text_content": [],
                "summary": ""
            })
            
            # Display results
            st.subheader("Extracted Text")
            full_text = " ".join(result["text_content"])
            st.write(full_text[:500] + "..." if len(full_text) > 500 else full_text)
            
            st.subheader("Final Summary of the Extracted Data ")
            st.write(result["summary"])

        # Clean up PDF file if used
        if input_type == "PDF" and os.path.exists(input_content):
            os.remove(input_content)

if __name__ == "__main__":
    main()