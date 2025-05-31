#!/usr/bin/python3
"""
Health check utility for AirBnB deployment
Verifies the health of the deployment
"""

import requests
import time
from config import DEPLOYMENT
from utils.logger import log_info, log_error

def check_server_health(server_url, timeout=None):
    """
    Check if a server is healthy by making a request to the health check path
    
    Args:
        server_url (str): The base URL of the server
        timeout (int): Timeout in seconds for the health check
        
    Returns:
        bool: True if server is healthy, False otherwise
    """
    if timeout is None:
        timeout = DEPLOYMENT['health_check_timeout']
        
    health_check_url = f"{server_url}{DEPLOYMENT['health_check_path']}"
    
    try:
        log_info(f"Checking health of {health_check_url}")
        response = requests.get(
            health_check_url,
            timeout=timeout,
            verify=False  # For development only, should be True in production
        )
        
        if response.status_code == 200:
            log_info(f"Health check passed for {server_url}")
            return True
        else:
            log_error(f"Health check failed for {server_url}. Status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_error(f"Health check failed for {server_url}", e)
        return False

def wait_for_healthy(server_url, max_attempts=5, delay=5):
    """
    Wait for a server to become healthy
    
    Args:
        server_url (str): The base URL of the server
        max_attempts (int): Maximum number of attempts
        delay (int): Delay between attempts in seconds
        
    Returns:
        bool: True if server becomes healthy, False otherwise
    """
    for attempt in range(max_attempts):
        if check_server_health(server_url):
            return True
            
        if attempt < max_attempts - 1:
            log_info(f"Server not healthy yet. Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
            
    log_error(f"Server {server_url} did not become healthy after {max_attempts} attempts")
    return False 