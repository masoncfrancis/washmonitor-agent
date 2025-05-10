from dotenv import load_dotenv
from enum import Enum  # Import Enum for status validation
import proc.img as imgProc  # Import the image processing module
import proc.ml as mlProc  # Import the machine learning module
import os
import time


# Define the AgentStatus Enum
class AgentStatus(Enum):
    MONITOR = "monitor"
    IDLE = "idle"


# Define the WasherStatus Enum
class WasherStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"


# Global vars
washerStoppedCount = 0  # Counter for stopped washing machine
agentStatus = AgentStatus.IDLE.value  # Use Enum value


def setAgentStatus(status: AgentStatus):
    # TODO query API to set the status
   return status.value


def getAgentStatus():
    return AgentStatus.MONITOR.value # placeholder
    # TODO query API to get the actual value


# TODO I have decided to make this program just an agent, and the API will be served by a Go program
def getWashingMachineStatus():
    global washerStoppedCount  # Declare the global variable

    if agentStatus["status"] == AgentStatus.MONITOR.value:

        print("Checking washing machine status...")

        # Get the image of the washing machine
        washerImageFilePath = imgProc.getImage(os.environ('WASHER_CAMERA_URL'))

        # Determine if the image contains a control panel
        result = mlProc.cropToControlPanel(washerImageFilePath)
        if result["status"] == True:
            print("Control panel detected")
            imgProc.deleteImage(washerImageFilePath)  # Delete the original image because we don't need it anymore
            pass  # Placeholder for actual processing logic
        else:
            imgProc.deleteImage(washerImageFilePath)
            print("Control panel not detected. Incrementing stopped count.")
            return WasherStatus.STOPPED.value
        

if __name__ == "__main__":

    load_dotenv()

    last_washer_check = 0
    last_agent_check = 0

    while True:
        now = time.time()

        # Check agent status every 5 seconds, always
        if now - last_agent_check >= 5:
            agentStatus = getAgentStatus()
            last_agent_check = now

        # Check washer status every 60 seconds, only if agent is monitoring
        if agentStatus == AgentStatus.MONITOR.value and now - last_washer_check >= 60:
            washerStatus = getWashingMachineStatus()

            if washerStatus == WasherStatus.STOPPED.value:
                washerStoppedCount += 1
            elif washerStatus == WasherStatus.RUNNING.value:
                washerStoppedCount = 0

            if washerStoppedCount >= 5:
                agentStatus = setAgentStatus(AgentStatus.IDLE)
                print("Washing machine is stopped. Setting agent status to idle.")
                washerStoppedCount = 0

            last_washer_check = now

        time.sleep(1)  # Prevent busy-waiting
