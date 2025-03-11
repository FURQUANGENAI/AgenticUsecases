# Document Extractor Chat Agent

A  Streamlit app to process medical report PDFs and chat with their content using AI.Inspired by Andrew NG

## Features
- Upload a PDF (e.g., medical report).
- Extracts text and images, performs OCR on images.
- Analyzes content for main topic, charts/tables, and key info.
- Allows chatting with the PDF content via an AI agent.

## Requirements
- Python 3.8+
- Install dependencies:
  ```bash
  pip install langgraph langchain langchain-openai streamlit PyMuPDF pytesseract pillow python-dotenv

## Workflow:
- Extract text/images → OCR (if images) → Analyze → Chat.
## Tech:
LangGraph manages the processing pipeline.
OpenAI GPT-4o-mini powers analysis and chat.
Streamlit provides the UI.

==================================

## Code Explanation
This is a Streamlit-based application that processes PDF files (specifically medical reports) and allows users to chat with the content using an AI-powered agent. Here’s a breakdown:

## Imports
Libraries:
fitz (PyMuPDF): Extracts text and images from PDFs.
pytesseract: Performs OCR on images.
PIL (Pillow): Handles image processing.
langgraph: Manages the workflow as a state graph.
streamlit: Creates the web UI.
langchain_openai: Provides the OpenAI LLM (GPT-4o-mini).
langchain_core: Supplies prompts and tools for AI interactions.
dotenv: Loads environment variables (e.g., API keys).

## Setup
Environment Variables: Loads the OpenAI API key from a .env file. If missing, it stops with an error.

## LangGraph Workflow
State Definition: DocumentState is a typed dictionary tracking:
pdf_path: Path to the PDF.
text_content: Extracted text per page.
image_content: Extracted images per page.
ocr_results: OCR text from images.
reasoning_output: Analysis results.

## Step 1: extract_content:
Opens the PDF with fitz.
Extracts text and images page-by-page.
Returns them in the state.

## Step 2: ocr_images:
Runs OCR on extracted images using pytesseract.
Adds OCR text to the state.

## Step 3: reason_content:
Uses ChatOpenAI (GPT-4o-mini) to analyze the combined text and OCR.
Answers three questions: main topic, charts/tables, key info.
Returns the answers as a list.

## Routing:
route_to_ocr_or_reason: Checks if images exist. If yes, goes to ocr; if no, skips to reason.

## Graph:
Defines a workflow: extract → (ocr if images) → reason → end.
Compiled into app for execution.

## Chat Tool
answer_question:
A @tool-decorated function using GPT-4o-mini.
Takes a question and document context, returns a concise answer.
Invoked with .invoke() passing a dictionary of arguments.

## Streamlit UI
Title & Intro: Displays a custom title and instructions.
File Uploader: Accepts a PDF (labeled as a medical report).
Session State:
context: Stores the combined text and OCR for chatting.
chat: Stores chat history.
Processing:
Saves the uploaded PDF temporarily.
On "Process Medical Report" button click:
Runs the LangGraph workflow.
Combines text and OCR into context.
Displays extracted text, OCR results, analysis, and first image (if any).
Cleans up the temp file.

## Chat Interface:
Shows only if context exists (i.e., after processing).
Displays chat history.
Takes user input via st.chat_input.
Invokes answer_question with the question and context.
Updates and displays the chat history.
