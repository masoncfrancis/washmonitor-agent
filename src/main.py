from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from dotenv import load_dotenv
from enum import Enum  # Import Enum for status validation
import proc.img as imgProc  # Import the image processing module
import proc.ml as mlProc  # Import the machine learning module
import os


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
agentStatus = {"status": AgentStatus.IDLE.value}  # Use Enum value

washerStoppedCount = 0  # Counter for stopped washing machine

@app.post("/setAgentStatus")
def setAgentStatus(request: AgentStatusRequest):
    agentStatus["status"] = request.status.value  # Use Enum value
    return {"message": "The status of the agent has been set", "status": agentStatus["status"]}

@app.get("/getAgentStatus")
def getAgentStatus():
    return {"status": agentStatus["status"]}

@app.get("/healthcheck")
def healthCheck():
    return {"status": "ok"}

#
# Background task to get washing machine status every 60 seconds
#

@app.event("startup")
@repeat_every(seconds=60)  # Run every 60 seconds
def getWashingMachineStatus():
    if agentStatus["status"] == AgentStatus.MONITOR.value:

        print("Checking washing machine status...")

        # Get the image of the washing machine
        washerImageFilePath = imgProc.getImage(os.environ('WASHER_CAMERA_URL'))

        # Determine if the image contains a control panel
        result = mlProc.cropToControlPanel(washerImageFilePath)
        if result["status"] == True:
            print("Control panel detected")
            pass # Placeholder for actual processing logic
        else:
            washerStoppedCount += 1
            
        # If the washing machine is stopped for 5 consecutive checks, set the status to idle
        if washerStoppedCount >= 5:
            agentStatus["status"] = AgentStatus.IDLE.value
            print("Washing machine is stopped. Setting agent status to idle.")
            washerStoppedCount = 0
        
        
        washingMachineStatus = "running" # Placeholder for actual status
        print(f"Washing machine status: {washingMachineStatus}")
