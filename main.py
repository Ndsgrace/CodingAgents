import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import FileManagementToolkit
from langgraph.graph import StateGraph, END

# 1. Security & Environment Setup
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not found in .env file.")
    exit()

# Configuration
MAX_ITERATIONS = 10  # Safety throttle to protect your API quota
working_dir = "./java_generated_code"
if not os.path.exists(working_dir):
    os.makedirs(working_dir)

# 2. Tool Selection
toolkit = FileManagementToolkit(root_dir=str(working_dir))
file_tools = toolkit.get_tools()

# 3. Enhanced Agent State
class AgentState(TypedDict):
    task: str
    next_instruction: str
    history: List[str]
    decisions_log: List[str]  # For the report.txt feature
    iterations: int           # Safety counter

# 4. Model Initialization
architect = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
programmer = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0).bind_tools(file_tools)

def architect_node(state: AgentState):
    """Lead Architect providing code and reasoning."""
    # Ensure iteration count exists
    it_count = state.get("iterations", 0)
    
    # 1. Safety Check: Stop if we hit the limit discussed earlier
    if it_count >= MAX_ITERATIONS:
        return {
            "next_instruction": "TERMINATE", 
            "history": state['history'] + ["Safety: Max iterations reached."]
        }

    # 2. Prompting with established English-first structure
    prompt = f"""You are a Senior Java Architect.
    Objective: {state['task']}
    Current History: {state['history']}
    
    Your response MUST follow this exact format:
    REASONING: [Explain your architectural decision here]
    CODE: [The specific instruction or code for the Programmer]
    
    If the project is complete, reply ONLY with 'TERMINATE'."""
    
    # 3. Model Invocation
    response = architect.invoke(prompt)
    content = response.content
    
    # 4. Robust Parsing Logic for report.txt
    reasoning = "N/A"
    if "REASONING:" in content and "CODE:" in content:
        # Split safely based on your format
        parts = content.split("CODE:")
        reasoning = parts[0].replace("REASONING:", "").strip()
    elif "TERMINATE" in content.upper():
        reasoning = "Project completed successfully."
    else:
        # Fallback if the model misses the 'CODE:' tag
        reasoning = "Automated reasoning extraction failed; check history."

    # 5. Return updated state to LangGraph
    return {
        "next_instruction": content,
        "history": state['history'] + [f"Iteration {it_count}: {content}"],
        "decisions_log": state['decisions_log'] + [f"Iteration {it_count} Reasoning: {reasoning}"],
        "iterations": it_count + 1
    }

def programmer_node(state: AgentState):
    """Developer executing the file operations."""
    instruction = state['next_instruction']
    
    # If the architect didn't say terminate, we let the programmer try tools
    if "TERMINATE" not in instruction:
        programmer.invoke(instruction)
        
    return {"history": state['history'] + ["Programmer: Operation executed."]}

# --- GRAPH LOGIC ---

workflow = StateGraph(AgentState)
workflow.add_node("architect", architect_node)
workflow.add_node("programmer", programmer_node)

workflow.set_entry_point("architect")

def router(state: AgentState):
    """Decides whether to keep coding or finalize the report."""
    if "TERMINATE" in state['next_instruction'] or state['iterations'] >= MAX_ITERATIONS:
        # Generate the final report.txt discussed
        report_path = os.path.join(working_dir, "report.txt")
        with open(report_path, "w") as f:
            f.write("=== ARCHITECTURAL DECISION REPORT ===\n\n")
            f.write("\n\n".join(state['decisions_log']))
        return "end"
    return "continue"

workflow.add_edge("architect", "programmer")
workflow.add_conditional_edges("programmer", router, {
    "continue": "architect", 
    "end": END
})

executor = workflow.compile()

# --- EXECUTION ---
if __name__ == "__main__":
    task_description = "Create a professional Java project for a Library System: include a Book class, a LibraryManager with search logic, and a Main test class."
    inputs = {
        "task": task_description, 
        "next_instruction": "", 
        "history": [], 
        "decisions_log": [], 
        "iterations": 0
    }
    
    print("--- Starting Autonomous Java Agent (Local SSD Mode) ---")
    for event in executor.stream(inputs):
        # Print key events to terminal for monitoring
        print(event)