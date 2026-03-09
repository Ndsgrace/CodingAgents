# Java AI Architect Agent 🤖☕

An autonomous multi-agent system built with **LangGraph** and **Gemini 1.5**, designed to architect and implement Java projects with zero manual supervision.

## Overview
This project utilizes a **Boss-Worker (Architect-Programmer)** architecture to automate the software development lifecycle for Java applications. It leverages two distinct models to balance high-level reasoning with execution speed.



## The Dual-Agent Logic
* **Lead Architect (Gemini 1.5 Pro):** Handles high-level design patterns, class structures, and project requirements.
* **Developer (Gemini 1.5 Flash):** Executes file system operations and writes the actual `.java` code using specialized tools.

## Key Features
* **Autonomous Loop:** The agents collaborate until the Architect issues a `TERMINATE` command.
* **Decision Logging:** Every architectural choice is recorded in a `report.txt` file for traceability.
* **Safety Throttle:** A built-in iteration counter prevents infinite loops and protects API quota.
* **Environment Isolation:** Designed to run in a local virtual environment (`venv`) to ensure stability.

## Prerequisites
* **Python 3.13+**
* **Java JDK** (for compiling generated code)
* **Google AI Studio API Key** (Gemini Pro/Flash)

## Setup
1. Clone the repository: `git clone https://github.com/Ndsgrace/CodingAgents.git`
2. Create a `.env` file with your key: `GOOGLE_API_KEY=your_key_here`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the agent: `python main.py`

## Project Structure
* `main.py`: The core LangGraph logic.
* `java_generated_code/`: Output directory for the autonomous agent.
* `report.txt`: Automated architectural decision record.