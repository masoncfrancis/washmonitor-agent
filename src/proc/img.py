# Washmonitor agent image processing logic
#
# This module contains the image processing logic for the Washmonitor agent.
# It includes functions for obtaining images and cropping them

import requests
import time
import os


def getImage(url):
    """
    Fetch an image from the given URL and save it to temporary file.
    
    Args:
        url (str): The URL of the image to fetch.
    
    Returns:
        str: The path to the saved image file.
    """
    # Create a temporary file to save the image
    temp_file_path = "temp_image.jpg"
    
    # Fetch the image from the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the image to the temporary file
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)
        return temp_file_path
    else:
        raise Exception(f"Failed to fetch image from {url}. Status code: {response.status_code}")