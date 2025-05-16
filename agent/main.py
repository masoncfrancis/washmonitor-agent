import requests
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

def setAgentStatus(status: AgentStatus, user: str = ""):
    payload = {"status": status.value}
    if status == AgentStatus.MONITOR:
        if not user:
            raise ValueError("User is required when status is 'monitor'")
        payload["user"] = user
    requests.post(apiURL + "/setAgentStatus", json=payload)
    return status.value


def getAgentStatus():
    return requests.get(apiURL + "/getAgentStatus").json()["status"]


def getWashingMachineStatus():
    if agentStatus == AgentStatus.MONITOR.value:
        print("Checking washing machine status...")

        try:
            washerImageFilePath = imgProc.getImage(os.environ.get('WASHER_CAMERA_URL'))
        except Exception as e:
            print(f"Error getting the washer image: {e}")
            return WasherStatus.STOPPED.value  # O cualquier valor seguro

        result = mlProc.cropToControlPanel(washerImageFilePath)
        if result["status"] == True:
            print("Control panel detected")
            imgProc.deleteImage(washerImageFilePath)
            classification = mlProc.classifyControlPanel(result["imagePath"])
            print("Classification result:", classification)
            imgProc.deleteImage(result["imagePath"])
            if classification == WasherStatus.STOPPED.value:
                return WasherStatus.STOPPED.value
            elif classification == WasherStatus.RUNNING.value:
                return WasherStatus.RUNNING.value
        else:
            imgProc.deleteImage(washerImageFilePath)
            print("Control panel not detected")
            return WasherStatus.STOPPED.value

    return WasherStatus.STOPPED.value  # Default to stopped
        

if __name__ == "__main__":

    load_dotenv()

    apiURL = os.environ.get('API_URL')

    last_washer_check = time.monotonic()
    last_agent_check = time.monotonic()

    while True:
        now = time.monotonic()

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
                print("Washing machine is stopped for 5 checks. Setting agent status to idle.")
                setAgentStatus(AgentStatus.IDLE)
                washerStoppedCount = 0

                # Notify the user
                requests.post(
                    os.environ.get('DISCORD_URL'),
                    json={"content": "✅ Washing machine has finished running"}
                )
            else:
                print(f"Washing machine is {washerStatus}. Agent status remains as monitor.")

            last_washer_check = now

        # Dormir hasta el siguiente evento programado
        next_agent = last_agent_check + 5
        next_washer = last_washer_check + 60 if agentStatus == AgentStatus.MONITOR.value else float('inf')
        sleep_time = max(0, min(next_agent, next_washer) - time.monotonic())
        time.sleep(sleep_time)
