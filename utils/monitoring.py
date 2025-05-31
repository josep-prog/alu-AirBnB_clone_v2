#!/usr/bin/python3
"""
Monitoring utility for AirBnB deployment
Handles server monitoring and alerting
"""

import psutil
import requests
import time
from datetime import datetime
from fabric.api import run, sudo
from utils.logger import log_info, log_error, log_warning
from config import WEB_SERVERS, DEPLOYMENT

class ServerMonitor:
    def __init__(self, server_name, server_config):
        self.server_name = server_name
        self.server_config = server_config
        self.metrics = {}
        
    def collect_metrics(self):
        """Collect server metrics"""
        try:
            # CPU Usage
            cpu_percent = run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
            self.metrics['cpu_usage'] = float(cpu_percent)
            
            # Memory Usage
            memory_info = run("free -m | grep Mem")
            total_mem = int(memory_info.split()[1])
            used_mem = int(memory_info.split()[2])
            self.metrics['memory_usage'] = (used_mem / total_mem) * 100
            
            # Disk Usage
            disk_info = run("df -h / | tail -1")
            disk_usage = int(disk_info.split()[4].strip('%'))
            self.metrics['disk_usage'] = disk_usage
            
            # Nginx Status
            nginx_status = run("systemctl is-active nginx")
            self.metrics['nginx_status'] = nginx_status == 'active'
            
            # Load Average
            load_avg = run("cat /proc/loadavg").split()[0]
            self.metrics['load_average'] = float(load_avg)
            
            # Network Connections
            connections = run("netstat -an | grep :80 | wc -l")
            self.metrics['active_connections'] = int(connections)
            
            # Response Time
            start_time = time.time()
            response = requests.get(f"http://{self.server_config['host']}{DEPLOYMENT['health_check_path']}")
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.metrics['response_time'] = response_time
            self.metrics['http_status'] = response.status_code
            
            return True
            
        except Exception as e:
            log_error(f"Failed to collect metrics for {self.server_name}", e)
            return False
            
    def check_alerts(self):
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # CPU Usage Alert
        if self.metrics.get('cpu_usage', 0) > 80:
            alerts.append(f"High CPU usage: {self.metrics['cpu_usage']}%")
            
        # Memory Usage Alert
        if self.metrics.get('memory_usage', 0) > 85:
            alerts.append(f"High memory usage: {self.metrics['memory_usage']}%")
            
        # Disk Usage Alert
        if self.metrics.get('disk_usage', 0) > 85:
            alerts.append(f"High disk usage: {self.metrics['disk_usage']}%")
            
        # Nginx Status Alert
        if not self.metrics.get('nginx_status', False):
            alerts.append("Nginx service is not running")
            
        # Load Average Alert
        if self.metrics.get('load_average', 0) > 5:
            alerts.append(f"High load average: {self.metrics['load_average']}")
            
        # Response Time Alert
        if self.metrics.get('response_time', 0) > 1000:  # More than 1 second
            alerts.append(f"High response time: {self.metrics['response_time']}ms")
            
        # HTTP Status Alert
        if self.metrics.get('http_status', 0) != 200:
            alerts.append(f"HTTP status error: {self.metrics['http_status']}")
            
        return alerts

def setup_monitoring():
    """Setup monitoring on all servers"""
    try:
        # Install required packages
        for server_name, server_config in WEB_SERVERS.items():
            if server_name == 'lb-01':  # Skip load balancer
                continue
                
            run("sudo apt-get update")
            run("sudo apt-get install -y python3-pip net-tools")
            run("sudo pip3 install psutil requests")
            
        log_info("Monitoring setup completed successfully")
        return True
        
    except Exception as e:
        log_error("Failed to setup monitoring", e)
        return False

def monitor_servers():
    """Monitor all servers and generate alerts"""
    alerts = []
    
    for server_name, server_config in WEB_SERVERS.items():
        if server_name == 'lb-01':  # Skip load balancer
            continue
            
        monitor = ServerMonitor(server_name, server_config)
        if monitor.collect_metrics():
            server_alerts = monitor.check_alerts()
            if server_alerts:
                alerts.extend([f"{server_name}: {alert}" for alert in server_alerts])
                
    return alerts

def send_alert(alerts):
    """Send alerts (placeholder for actual alert mechanism)"""
    if not alerts:
        return
        
    alert_message = "\n".join(alerts)
    log_warning(f"Alerts generated:\n{alert_message}")
    
    # TODO: Implement actual alert mechanism (email, Slack, etc.)
    # For now, just log the alerts 