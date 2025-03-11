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
