## Marketing Campaign Generator
A Python application that automates the creation of marketing blog posts using LangGraph, Groq’s Mixtral model, DuckDuckGo for research, and Streamlit for the UI. It includes a visual workflow graph via Mermaid and debugging traces with LangSmith.

## Features
Blog Post Generation: Creates a 300-word marketing blog post from a topic (e.g., "Eco-Friendly Products").
Workflow: Orchestrates idea generation and research, then synthesizes a draft and final post.

## Tools:
Groq: Fast inference with Mixtral 8x7B for text generation.
DuckDuckGo: Fetches audience trends for research.
LangGraph: Manages the workflow (Orchestrator + Synthesizer).
Streamlit: Simple UI for input and output.
LangSmith: Debugging traces for each step.

## Architecture:
Orchestrator: Coordinates ideas and research.
Synthesizer: Combines and refines content.

## How It Works
Orchestrator:
idea_node: Generates campaign ideas with Groq.
research_node: Fetches trends via DuckDuckGo.

Synthesizer:
draft_node: Writes a draft using ideas and research.
synthesize_node: Refines into a final post.

### Workflow: LangGraph sequences: idea_node → research_node → draft_node → synthesize_node.
UI: Streamlit displays inputs, outputs
Debugging: LangSmith traces each step.