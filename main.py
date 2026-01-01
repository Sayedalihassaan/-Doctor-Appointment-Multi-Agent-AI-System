from fastapi import FastAPI
from pydantic import BaseModel
from agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage
import os

os.environ.pop("SSL_CERT_FILE", None)


app = FastAPI()

# Define Pydantic model to accept request body
class UserQuery(BaseModel):
    id_number: int
    messages: str

agent = DoctorAppointmentAgent()

@app.post("/execute")
def execute_agent(user_input: UserQuery):
    app_graph = agent.workflow()
    
    # Prepare agent state as expected by the workflow
    input = [
        HumanMessage(content=user_input.messages)
    ]
    query_data = {
        "messages": input,
        "id_number": user_input.id_number,
        "next": "",
        "query": "",
        "current_reasoning": "",
        "iteration_count": 0,
    }  

    response = app_graph.invoke(query_data,config={"recursion_limit": 20})
    
    # Extract content from message objects
    user_friendly_response = "\n".join([
        msg.content if hasattr(msg, 'content') else str(msg) 
        for msg in response["messages"]
    ])
    
    return {"response": user_friendly_response}