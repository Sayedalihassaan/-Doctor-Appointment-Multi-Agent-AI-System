# 🩺 Doctor Appointment Multi-Agent AI System

## Overview

This project demonstrates a fully **automated, end-to-end multi-agent AI system** for managing doctor appointments. Using **agentic AI**, multiple specialized agents collaborate to handle user requests seamlessly — from understanding the user's query, checking doctor availability, to booking, canceling, or rescheduling appointments. This showcases the **power of autonomous AI agents working together** to complete complex tasks without human intervention.

---

## Features

- **Multi-Agent Architecture**: Different agents handle specific tasks:
  - `information_node` → Provides availability info and answers FAQs.
  - `booking_node` → Manages booking, canceling, and rescheduling appointments.
  - `supervisor` → Directs the workflow and decides which agent should act next.
- **State Management**: Shared state ensures all agents collaborate effectively and keep track of user context.
- **Dynamic Workflow**: Supervisor agent decides the next step based on user query and conversation history.
- **User-Friendly Responses**: All AI responses are formatted as readable text, ready for direct display in UI.
- **Flexible Tool Integration**: Each agent uses specialized tools to interact with data.

---

## How it Works

1. **User Input**: Users provide their `ID number` and query via the UI.
2. **Supervisor Agent**: Determines which agent should handle the request (info or booking) and manages workflow.
3. **Specialized Agents**:
   - `Information Node`: Checks doctor availability or answers FAQs.
   - `Booking Node`: Books, cancels, or reschedules appointments.
4. **Tools**: Agents use functions like `check_availability_by_doctor`, `check_availability_by_specialization`, `set_appointment`, `cancel_appointment`, and `reschedule_appointment`.
5. **Response**: The AI response is returned as **clear, human-readable text** for the user.

---

## Tech Stack

- **Backend**: Python, FastAPI, Pydantic
- **AI & NLP**: LangChain, LangGraph, Llama-3.3/Groq Chat LLM
- **Data Handling**: Pandas, CSV files for doctor schedules
- **Frontend**: Streamlit for interactive user interface
- **Tools & Workflow**: Agentic AI workflow, modular toolkits for booking and info retrieval
- **Environment**: `.env` for API keys, secure key handling

---

## Demo

1. Start the FastAPI server:

```bash
uvicorn main:app --host 127.0.0.1 --port 8003
```

2. Run Streamlit UI:

```bash
streamlit run streamlit_ui.py
```
