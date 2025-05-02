from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel

app = FastAPI()

#
# Endpoint stuff
#


# Define the request model for /setAgentStatus
class AgentStatusRequest(BaseModel):
    status: str

# In-memory storage for agent status
agent_status = {"status": "idle"}

@app.post("/setAgentStatus")
def set_agent_status(request: AgentStatusRequest):
    if request.status not in ["monitor", "idle"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    agent_status["status"] = request.status
    return {"message": "The status of the agent has been set", "status": agent_status["status"]}

@app.get("/getAgentStatus")
def get_agent_status():
    return {"status": agent_status["status"]}

#
# Background task to get washing machine status every 60 seconds
#

@app.event("startup")
@repeat_every(seconds=60)  # Run every 60 seconds
def get_washing_machine_status():

    if agent_status["status"] == "monitor":
        # Here you would implement the logic to check the washing machine status
        # For example, you could call an external API or check a database
        # For demonstration purposes, we'll just simulate it with a print statement
        print("Checking washing machine status...")
        
        # Simulate getting the washing machine status
        washing_machine_status = simulate_get_washing_machine_status()
        print(f"Washing machine status: {washing_machine_status}")

    # Simulate getting the washing machine status
    # In a real-world scenario, this would involve calling an external API or checking a database
    washing_machine_status = "running"
