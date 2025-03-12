## Animal Image Recognition with GPT-4of
A Python application that uses Streamlit, LangGraph, and OpenAI’s GPT-4o to upload a small JPG image of an animal, display it, and generate a description of the animal. The app also visualizes the workflow as a graph, providing insight into the image recognition process.

## Features
Image Upload: Upload small JPG images (resized to 200x200 pixels).
Display: Shows the uploaded image in the Streamlit UI.
Recognition: Uses GPT-4o to describe the animal in the image.
Workflow Visualization: Displays a collapsible graph of the LangGraph workflow.
Agentic Workflow: Two nodes (upload and describe) orchestrated by LangGraph.

## Prerequisites
Python: 3.8 or higher.
API Key: OpenAI API key for GPT-4o access.
System Dependencies: Graphviz for rendering the workflow graph.