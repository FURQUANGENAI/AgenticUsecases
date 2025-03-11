import fitz  # PyMuPDF for PDF handling
import os
import pytesseract  # OCR for images
from PIL import Image as PILImage
import io
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
if not os.environ["OPENAI_API_KEY"]:
    st.error("OPENAI_API_KEY not found in .env file.")
    st.stop()

# Define LangGraph state
class DocumentState(TypedDict):
    pdf_path: str
    text_content: Annotated[Sequence[dict], "Extracted text"]
    image_content: Annotated[Sequence[dict], "Extracted images"]
    ocr_results: Annotated[Sequence[dict], "OCR text"]
    reasoning_output: Annotated[Sequence[str], "Analysis results"]

# Step 1: Extract text and images from PDF
def extract_content(state: DocumentState) -> DocumentState:
    try:
        doc = fitz.open(state["pdf_path"])
        text_content = []
        image_content = []
        for page_num, page in enumerate(doc):
            text = page.get_text("text").strip()
            text_content.append({"page": page_num + 1, "text": text})
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image = PILImage.open(io.BytesIO(base_image["image"]))
                image_content.append({"page": page_num + 1, "image": image})
        doc.close()
        return {"text_content": text_content, "image_content": image_content}
    except Exception as e:
        st.error(f"PDF extraction failed: {e}")
        return {"text_content": [], "image_content": []}

# Step 2: Perform OCR on images (if any)
def ocr_images(state: DocumentState) -> DocumentState:
    ocr_results = []
    for item in state["image_content"]:
        text = pytesseract.image_to_string(item["image"]).strip()
        ocr_results.append({"page": item["page"], "ocr_text": text})
    return {"ocr_results": ocr_results}

# Step 3: Analyze document content
def reason_content(state: DocumentState) -> DocumentState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(
        "Analyze this document:\nText: {text}\nOCR: {ocr}\nAnswer:\n1. Main topic?\n2. Charts/tables?\n3. Key info?"
    )
    text = " ".join([item["text"] for item in state["text_content"]]) or "No text"
    ocr = " ".join([item["ocr_text"] for item in state.get("ocr_results", [])]) or "No OCR"
    reasoning = llm.invoke(prompt.format(text=text, ocr=ocr)).content.split("\n")
    return {"reasoning_output": reasoning}

# Conditional routing
def route_to_ocr_or_reason(state: DocumentState) -> str:
    return "ocr" if state["image_content"] else "reason"

# Build LangGraph workflow
workflow = StateGraph(DocumentState)
workflow.add_node("extract", extract_content)
workflow.add_node("ocr", ocr_images)
workflow.add_node("reason", reason_content)
workflow.set_entry_point("extract")
workflow.add_conditional_edges("extract", route_to_ocr_or_reason, {"ocr": "ocr", "reason": "reason"})
workflow.add_edge("ocr", "reason")
workflow.add_edge("reason", END)
app = workflow.compile()

# Chat tool
@tool
def answer_question(question: str, context: str) -> str:
    """Answer a question based on the document content."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(
        "Document content: {context}\nQuestion: {question}\nAnswer concisely:"
    )
    return llm.invoke(prompt.format(context=context, question=question)).content

# Streamlit UI
def main():
    st.title("Document Extractor  Chat Agent - Developed by Furquan")
    st.write("Upload a Medical Report  and ask questions about the Report .")

    # Show workflow graph
##    st.subheader("Workflow")
   
       # File uploader
    uploaded_file = st.file_uploader("Upload Medical Report in PDF format", type="pdf")

    # Session state
    if "context" not in st.session_state:
        st.session_state.context = ""
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if uploaded_file:
        pdf_path = f"temp_{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Process Medical Report"):
            with st.spinner("Processing your Medical Report..."):
                result = app.invoke({
                    "pdf_path": pdf_path,
                    "text_content": [],
                    "image_content": [],
                    "ocr_results": [],
                    "reasoning_output": []
                })
                text = " ".join([item["text"] for item in result["text_content"]]) or "No text"
                ocr = " ".join([item["ocr_text"] for item in result.get("ocr_results", [])]) or "No OCR"
                st.session_state.context = f"Text: {text}\nOCR: {ocr}"

                st.subheader("Extracted Report")
                for item in result["text_content"]:
                    st.write(f"Page {item['page']}: {item['text'][:200]}...")
                if not result["text_content"]:
                    st.write("No text found.")

                st.subheader("OCR Results")
                for item in result.get("ocr_results", []):
                    st.write(f"Page {item['page']}: {item['ocr_text'][:200]}...")
                if not result.get("ocr_results"):
                    st.write("No images for OCR.")

                st.subheader("Analysing the Report ")
                for line in result["reasoning_output"]:
                    st.write(line)

                if result["image_content"]:
                    st.image(result["image_content"][0]["image"], 
                            caption=f"Image from Page {result['image_content'][0]['page']}")

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # Chat section
    if st.session_state.context:
        st.subheader("Chat with PDF")
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        question = st.chat_input("Ask about your Medical Report:")
        if question:
            with st.chat_message("user"):
                st.write(question)
            with st.spinner("Answering..."):
                # Correctly invoke the tool
                answer = answer_question.invoke({"question": question, "context": st.session_state.context})
            with st.chat_message("assistant"):
                st.write(answer)
            st.session_state.chat.append({"role": "user", "content": question})
            st.session_state.chat.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()