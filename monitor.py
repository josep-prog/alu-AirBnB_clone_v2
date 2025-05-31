#!/usr/bin/python3
"""
Monitoring script for AirBnB deployment
Can be run as a cron job to monitor servers
"""

import os
import sys
import json
from datetime import datetime
from utils.monitoring import monitor_servers, send_alert
from utils.logger import log_info, log_error

def save_metrics(metrics):
    """Save metrics to a JSON file"""
    try:
        metrics_dir = 'metrics'
        if not os.path.exists(metrics_dir):
            os.makedirs(metrics_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metrics_file = f"{metrics_dir}/metrics_{timestamp}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=4)
            
        log_info(f"Metrics saved to {metrics_file}")
        
    except Exception as e:
        log_error("Failed to save metrics", e)

def main():
    """Main monitoring function"""
    try:
        log_info("Starting server monitoring")
        
        # Monitor servers and get alerts
        alerts = monitor_servers()
        
        # Send alerts if any
        if alerts:
            send_alert(alerts)
            
        log_info("Server monitoring completed")
        
    except Exception as e:
        log_error("Monitoring failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main() 