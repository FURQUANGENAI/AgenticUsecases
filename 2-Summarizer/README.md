# Summarizer Agent

A Streamlit-based agent using LangGraph to summarize PDFs or text input, with a visual workflow graph.

## Features
- Upload a PDF or enter text to summarize.
- Extracts text from PDFs using PyMuPDF.
- Generates concise summaries with OpenAI's GPT-4o-mini.
- Displays the LangGraph workflow as a visual graph.

## Requirements
- Python 3.8+
- Install dependencies:
  ```bash
  pip install langgraph langchain-openai streamlit PyMuPDF python-dotenv graphviz

  =============================================================================

## Code Explanation
This script builds a Summarizer Agent using LangGraph and displays its workflow graph in a Streamlit UI. It processes either a PDF or raw text input, extracts the text, summarizes it using GPT-4o-mini, and shows the results alongside a visual representation of the process.

##  Here’s how it works, step-by-step:

## Imports
fitz (PyMuPDF): Extracts text from PDFs.
os: Handles file operations (e.g., saving/deleting temp PDFs).
typing: Defines the SummaryState type for LangGraph.
langgraph.graph: Provides StateGraph and END for building the workflow.
streamlit: Creates the web interface.
dotenv: Loads environment variables (e.g., API key).
langchain_openai: Supplies ChatOpenAI for LLM calls.
langchain_core.prompts: Offers ChatPromptTemplate for prompt formatting.