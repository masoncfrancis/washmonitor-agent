from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from dotenv import load_dotenv
from enum import Enum  # Import Enum for status validation

load_dotenv()  # Load environment variables from a .env file

app = FastAPI()

#
# Endpoint stuff
#

# Define the AgentStatus Enum
class AgentStatus(Enum):
    MONITOR = "monitor"
    IDLE = "idle"

# Define the request model for /setAgentStatus
class AgentStatusRequest(BaseModel):
    status: AgentStatus  # Use the Enum for validation

# In-memory storage for agent status
agent_status = {"status": AgentStatus.IDLE.value}  # Use Enum value

@app.post("/setAgentStatus")
def set_agent_status(request: AgentStatusRequest):
    agent_status["status"] = request.status.value  # Use Enum value
    return {"message": "The status of the agent has been set", "status": agent_status["status"]}

@app.get("/getAgentStatus")
def get_agent_status():
    return {"status": agent_status["status"]}

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

#
# Background task to get washing machine status every 60 seconds
#

@app.event("startup")
@repeat_every(seconds=60)  # Run every 60 seconds
def get_washing_machine_status():
    if agent_status["status"] == AgentStatus.MONITOR.value:
        # Here you would implement the logic to check the washing machine status
        # For example, you could call an external API or check a database
        # For demonstration purposes, we'll just simulate it with a print statement
        print("Checking washing machine status...")
        
        # Simulate getting the washing machine status
        washing_machine_status = "running" # Placeholder for actual status
        print(f"Washing machine status: {washing_machine_status}")

    # Simulate getting the washing machine status
    # In a real-world scenario, this would involve calling an external API or checking a database
    washing_machine_status = "running"