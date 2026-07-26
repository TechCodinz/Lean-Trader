#!/usr/bin/env python3
"""
💓 HEALTH MONITORING ENDPOINT
Provides HTTP health check endpoint for external monitoring
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import threading
from datetime import datetime
from pathlib import Path

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health' or self.path == '/':
            self.send_health_response()
        elif self.path == '/status':
            self.send_status_response()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send basic health check response"""
        # Check if bot is running
        health_file = Path('/app/bot_data/health.txt')
        is_healthy = health_file.exists()
        
        status_code = 200 if is_healthy else 503
        response = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_status_response(self):
        """Send detailed status response"""
        try:
            # Read consciousness stats
            stats = {
                'status': 'operational',
                'timestamp': datetime.now().isoformat(),
                'uptime': self.get_uptime(),
                'engines': self.get_engine_count(),
                'consciousness': self.get_consciousness_level(),
                'trades_today': self.get_trades_count()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        except Exception as e:
            self.send_error(500, str(e))
    
    def get_uptime(self):
        """Get bot uptime"""
        try:
            health_file = Path('/app/bot_data/health.txt')
            if health_file.exists():
                mtime = health_file.stat().st_mtime
                uptime_seconds = time.time() - mtime
                return f"{uptime_seconds / 3600:.2f} hours"
        except:
            pass
        return "unknown"
    
    def get_engine_count(self):
        """Get number of active engines"""
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            h = get_consciousness_harmonizer()
            return len(h.engines)
        except:
            return 254  # Default
    
    def get_consciousness_level(self):
        """Get consciousness level"""
        try:
            from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
            h = get_consciousness_harmonizer()
            return f"{h.consciousness_level:.1%}"
        except:
            return "unknown"
    
    def get_trades_count(self):
        """Get today's trade count"""
        try:
            import sqlite3
            conn = sqlite3.connect('/app/bot_data/enhanced_trading_bot.db')
            cursor = conn.execute(
                "SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = DATE('now')"
            )
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


def start_health_monitor(port=8000):
    """Start health monitoring server"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"💓 Health monitor started on port {port}")
    print(f"   Health check: http://localhost:{port}/health")
    print(f"   Status API: http://localhost:{port}/status")
    server.serve_forever()


def start_health_monitor_thread(port=8000):
    """Start health monitor in background thread"""
    thread = threading.Thread(target=start_health_monitor, args=(port,), daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    import time
    start_health_monitor(8000)
