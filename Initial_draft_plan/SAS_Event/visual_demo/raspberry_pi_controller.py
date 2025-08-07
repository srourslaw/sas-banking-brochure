#!/usr/bin/env python3
"""
Raspberry Pi Traffic Light Controller for SAS Event Demo
Controls physical LEDs and monitors GitHub Actions pipeline status
"""

import time
import json
import requests
import RPi.GPIO as GPIO
from threading import Thread
import logging
from datetime import datetime, timedelta

# GPIO Pin Configuration
RED_LED = 18      # Red traffic light
YELLOW_LED = 23   # Yellow traffic light  
GREEN_LED = 24    # Green traffic light
BUZZER = 25       # Success buzzer

# GitHub Configuration
GITHUB_REPO = "thakralone/sas-event-demo"  # Replace with your repo
GITHUB_TOKEN = "your_github_token_here"    # Replace with your token
WORKFLOW_NAME = "model-to-market-demo.yml"

# Demo Configuration
DEMO_DURATION = 300  # 5 minutes in seconds

class TrafficLightController:
    """Controls physical traffic lights based on pipeline status"""
    
    def __init__(self):
        self.setup_gpio()
        self.pipeline_status = "idle"
        self.demo_start_time = None
        self.monitoring = False
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def setup_gpio(self):
        """Initialize GPIO pins for LEDs and buzzer"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RED_LED, GPIO.OUT)
        GPIO.setup(YELLOW_LED, GPIO.OUT)
        GPIO.setup(GREEN_LED, GPIO.OUT)
        GPIO.setup(BUZZER, GPIO.OUT)
        
        # Start with red light on
        self.set_light_state("red")
        logging.info("🚦 GPIO initialized - Traffic light ready")
        
    def set_light_state(self, state):
        """Set traffic light state"""
        # Turn all lights off first
        GPIO.output(RED_LED, GPIO.LOW)
        GPIO.output(YELLOW_LED, GPIO.LOW)
        GPIO.output(GREEN_LED, GPIO.LOW)
        
        if state == "red":
            GPIO.output(RED_LED, GPIO.HIGH)
            logging.info("🔴 RED LIGHT - Demo Ready/In Progress")
        elif state == "yellow":
            GPIO.output(YELLOW_LED, GPIO.HIGH)
            logging.info("🟡 YELLOW LIGHT - Testing Phase")
        elif state == "green":
            GPIO.output(GREEN_LED, GPIO.HIGH)
            logging.info("🟢 GREEN LIGHT - Production Ready!")
        elif state == "flash_green":
            # Flash green for celebration
            for _ in range(10):
                GPIO.output(GREEN_LED, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(GREEN_LED, GPIO.LOW)
                time.sleep(0.2)
            GPIO.output(GREEN_LED, GPIO.HIGH)
            
    def success_celebration(self):
        """Celebrate successful demo completion"""
        logging.info("🎉 DEMO SUCCESS - Starting celebration sequence!")
        
        # Flash all lights
        for _ in range(5):
            GPIO.output(RED_LED, GPIO.HIGH)
            GPIO.output(YELLOW_LED, GPIO.HIGH)
            GPIO.output(GREEN_LED, GPIO.HIGH)
            time.sleep(0.3)
            
            GPIO.output(RED_LED, GPIO.LOW)
            GPIO.output(YELLOW_LED, GPIO.LOW)
            GPIO.output(GREEN_LED, GPIO.LOW)
            time.sleep(0.3)
        
        # Sound buzzer
        for _ in range(3):
            GPIO.output(BUZZER, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(BUZZER, GPIO.LOW)
            time.sleep(0.2)
            
        # End with green light
        self.set_light_state("flash_green")
        
    def get_pipeline_status(self):
        """Get current GitHub Actions pipeline status"""
        try:
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get latest workflow run
            url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                runs = response.json()['workflow_runs']
                if runs:
                    latest_run = runs[0]
                    return {
                        'status': latest_run['status'],
                        'conclusion': latest_run.get('conclusion'),
                        'created_at': latest_run['created_at'],
                        'html_url': latest_run['html_url']
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Error getting pipeline status: {e}")
            return None
    
    def monitor_pipeline(self):
        """Monitor pipeline and update lights accordingly"""
        logging.info("👀 Starting pipeline monitoring...")
        
        while self.monitoring:
            try:
                status = self.get_pipeline_status()
                
                if status:
                    pipeline_state = status['status']
                    conclusion = status.get('conclusion')
                    
                    if pipeline_state == 'queued' or pipeline_state == 'in_progress':
                        if not hasattr(self, 'progress_phase'):
                            self.progress_phase = 0
                            
                        # Update lights based on estimated progress
                        elapsed = time.time() - self.demo_start_time if self.demo_start_time else 0
                        
                        if elapsed < 120:  # First 2 minutes - building
                            self.set_light_state("red")
                        elif elapsed < 240:  # 2-4 minutes - testing
                            self.set_light_state("yellow")
                        else:  # Final minute - deploying
                            # Flash yellow to indicate almost done
                            GPIO.output(YELLOW_LED, GPIO.HIGH)
                            time.sleep(0.5)
                            GPIO.output(YELLOW_LED, GPIO.LOW)
                            time.sleep(0.5)
                            
                    elif pipeline_state == 'completed':
                        if conclusion == 'success':
                            self.success_celebration()
                            logging.info("🏆 Pipeline completed successfully!")
                            self.monitoring = False
                        else:
                            self.set_light_state("red")
                            logging.error(f"❌ Pipeline failed: {conclusion}")
                            
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logging.error(f"❌ Error in pipeline monitoring: {e}")
                time.sleep(30)
    
    def start_demo(self):
        """Start the 5-minute demo countdown"""
        logging.info("🎬 STARTING 5-MINUTE MODEL-TO-MARKET DEMO")
        logging.info("🎯 Thakral One: SAS → Git → Container → Production")
        
        self.demo_start_time = time.time()
        self.monitoring = True
        
        # Start with red light
        self.set_light_state("red")
        
        # Start monitoring in background thread
        monitor_thread = Thread(target=self.monitor_pipeline)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Manual timer as backup (in case GitHub API fails)
        self.run_manual_timer()
        
    def run_manual_timer(self):
        """Run manual timer as backup"""
        logging.info("⏰ Starting manual backup timer")
        
        # Phase 1: Build phase (0-2 minutes) - Red
        for i in range(120):
            if not self.monitoring:
                return
            time.sleep(1)
            
        # Phase 2: Test phase (2-4 minutes) - Yellow
        self.set_light_state("yellow")
        logging.info("🧪 Entering test phase")
        
        for i in range(120):
            if not self.monitoring:
                return
            time.sleep(1)
            
        # Phase 3: Deploy phase (4-5 minutes) - Flashing Yellow
        logging.info("🚀 Entering deployment phase")
        
        for i in range(60):
            if not self.monitoring:
                return
            GPIO.output(YELLOW_LED, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(YELLOW_LED, GPIO.LOW)
            time.sleep(0.5)
            
        # Success! (Manual completion)
        if self.monitoring:
            logging.info("⏰ Manual timer completed - assuming success!")
            self.success_celebration()
            self.monitoring = False
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()
        logging.info("🧹 GPIO cleaned up")

def main():
    """Main function"""
    controller = TrafficLightController()
    
    try:
        print("🚦 Thakral One Traffic Light Controller Ready")
        print("🎯 Commands:")
        print("   's' - Start demo")
        print("   'r' - Red light")
        print("   'y' - Yellow light") 
        print("   'g' - Green light")
        print("   'c' - Celebration")
        print("   'q' - Quit")
        
        while True:
            command = input("\nEnter command: ").lower().strip()
            
            if command == 's':
                controller.start_demo()
            elif command == 'r':
                controller.set_light_state("red")
            elif command == 'y':
                controller.set_light_state("yellow")
            elif command == 'g':
                controller.set_light_state("green")
            elif command == 'c':
                controller.success_celebration()
            elif command == 'q':
                break
            else:
                print("❌ Unknown command")
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        
    finally:
        controller.monitoring = False
        controller.cleanup()

if __name__ == "__main__":
    main()