# Analyst Persona Generator Streamlit App

Welcome to the **Analyst Persona Generator Streamlit App**, an interactive tool that leverages LangGraph, LangChain, and the Groq API to generate diverse analyst personas for research topics.  this Streamlit application allows users to input topics, adjust the number of analysts, and refine personas with human feedback in real-time.

## Overview

### Purpose
This app generates AI-driven analyst personas (including names, roles, affiliations, and descriptions) based on a user-defined research topic. It supports iterative refinement through human-in-the-loop feedback and maintains state across sessions using LangGraph's checkpointing.

### Key Technologies
- **Framework**: LangGraph (for stateful workflows), LangChain (for LLM integration)
- **Language Model**: Groq (e.g., `llama3-70b-8192` or similar supported models)
- **UI**: Streamlit
- **Data Structures**: Pydantic for structured output
- **Environment**: Python 3.9+

## Features
- Generate 1 to 5 analyst personas based on a research topic.
- Provide iterative feedback to refine personas.
- Real-time display of results with an interactive interface.
- State persistence across feedback cycles using memory checkpoints.

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- An IDE (e.g., PyCharm, VSCode)
- Groq API key

