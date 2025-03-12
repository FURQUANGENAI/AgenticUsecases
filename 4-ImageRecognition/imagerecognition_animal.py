import os
import streamlit as st
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from PIL import Image
import io
import base64
from openai import OpenAI

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing OPENAI_API_KEY in .env file.")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ImageState(TypedDict):
    image: Any
    description: str

def upload_image(state: ImageState) -> ImageState:
    return state

def describe_image(state: ImageState) -> ImageState:
    image_data = base64.b64encode(state["image"]).decode("utf-8")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Describe this small JPG image of an animal."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]}
        ]
    )
    return {"description": response.choices[0].message.content}

workflow = StateGraph(ImageState)
workflow.add_node("upload_node", upload_image)
workflow.add_node("describe_node", describe_image)
workflow.set_entry_point("upload_node")
workflow.add_edge("upload_node", "describe_node")
workflow.add_edge("describe_node", END)
app = workflow.compile()

st.title("Animal Image Recognition ")
st.write("Upload a small JPG image of an animal (e.g., 200x200 pixels).")
graph_png=app.get_graph(xray=True).draw_mermaid_png() 
with st.expander("View Image  Graph Workflow - Furquan"):
    st.image(graph_png, caption="Image Recognization Workflow Graph", use_container_width=100)


uploaded_file = st.file_uploader("Choose an image...", type=["jpg"])
if uploaded_file:
    image = Image.open(uploaded_file).resize((200, 200), Image.Resampling.LANCZOS)
    st.image(image, caption="Uploaded Animal Image", use_container_width=250)
    with st.spinner("Recognizing animal..."):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        initial_state = {"image": image_bytes.getvalue(), "description": ""}
        result = app.invoke(initial_state)
        st.subheader("Animal Description")
        st.write(result["description"])