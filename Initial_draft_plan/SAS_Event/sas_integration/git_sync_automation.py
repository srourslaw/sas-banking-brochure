#!/usr/bin/env python3
"""
SAS-to-Git Sync Automation Script
Monitors SAS output directory and automatically commits changes to trigger CI/CD pipeline
"""

import os
import json
import time
import shutil
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Configuration
SAS_OUTPUT_DIR = "C:\\SAS_Event_Demo\\model_artifacts"
GIT_REPO_DIR = "/Users/husseinsrour/Downloads/SAS_Event/credit_risk_pipeline"
MODEL_ARTIFACT_DIR = os.path.join(GIT_REPO_DIR, "model_artifact")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sas_git_sync.log'),
        logging.StreamHandler()
    ]
)

class SASModelHandler(FileSystemEventHandler):
    """Handle SAS model file changes and sync to Git"""
    
    def __init__(self):
        self.last_processed = {}
        self.processing = False
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Check if this is a trigger file
        if event.src_path.endswith('.flag') and not self.processing:
            self.processing = True
            logging.info("🎯 SAS model update detected - starting sync process")
            self.sync_model_artifacts()
            self.processing = False
    
    def sync_model_artifacts(self):
        """Sync SAS model artifacts to Git repository"""
        try:
            # Create model artifact directory if it doesn't exist
            os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
            
            # Copy model files from SAS output
            sas_files = {
                'model_coefficients.json': 'model_coefficients.txt',
                'deployment_config.json': 'model_metadata.json',
                'test_cases.json': 'test_cases.json'
            }
            
            for sas_file, git_file in sas_files.items():
                sas_path = os.path.join(SAS_OUTPUT_DIR, sas_file)
                git_path = os.path.join(MODEL_ARTIFACT_DIR, git_file)
                
                if os.path.exists(sas_path):
                    if sas_file == 'model_coefficients.json':
                        # Convert JSON coefficients to simple text format for existing pipeline
                        self.convert_coefficients_to_text(sas_path, git_path)
                    elif sas_file == 'deployment_config.json':
                        # Convert deployment config to metadata format
                        self.convert_deployment_to_metadata(sas_path, git_path)
                    else:
                        shutil.copy2(sas_path, git_path)
                    
                    logging.info(f"✅ Synced {sas_file} → {git_file}")
            
            # Update version and timestamp
            self.update_model_metadata()
            
            # Commit to Git and trigger pipeline
            self.commit_and_push()
            
        except Exception as e:
            logging.error(f"❌ Error syncing model artifacts: {e}")
    
    def convert_coefficients_to_text(self, json_path, text_path):
        """Convert JSON coefficients to text format expected by existing pipeline"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            with open(text_path, 'w') as f:
                f.write("# Thakral One Credit Risk Model Coefficients\n")
                f.write(f"# Generated: {data.get('created_timestamp', 'Unknown')}\n")
                f.write(f"# Model Type: {data.get('model_type', 'logistic_regression')}\n\n")
                
                f.write(f"INTERCEPT: {data.get('intercept', 0)}\n\n")
                
                coefficients = data.get('coefficients', {})
                for feature, coeff in coefficients.items():
                    f.write(f"{feature}: {coeff}\n")
                
                # Add performance metrics
                perf = data.get('performance', {})
                f.write(f"\n# Performance Metrics\n")
                f.write(f"AUC: {perf.get('auc', 'N/A')}\n")
                f.write(f"Accuracy: {perf.get('accuracy', 'N/A')}\n")
                f.write(f"Precision: {perf.get('precision', 'N/A')}\n")
                f.write(f"Recall: {perf.get('recall', 'N/A')}\n")
                
        except Exception as e:
            logging.error(f"Error converting coefficients: {e}")
    
    def convert_deployment_to_metadata(self, json_path, metadata_path):
        """Convert deployment config to metadata format"""
        try:
            with open(json_path, 'r') as f:
                config = json.load(f)
            
            metadata = {
                "name": config.get("model_name", "thakral_credit_risk"),
                "version": config.get("version", "1.0.0"),
                "type": "classification",
                "features": list(config.get("input_schema", {}).keys()),
                "target": "risk_prediction",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sla_requirements": config.get("sla_requirements", {}),
                "source": "SAS Model Studio",
                "deployment_ready": True
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error converting deployment config: {e}")
    
    def update_model_metadata(self):
        """Update model metadata with latest deployment info"""
        metadata_path = os.path.join(MODEL_ARTIFACT_DIR, "model_metadata.json")
        
        try:
            # Load existing metadata or create new
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Update with current deployment info
            metadata.update({
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "deployment_trigger": "SAS_MODEL_STUDIO",
                "pipeline_version": "2.0.0",
                "demo_mode": True,
                "thakral_one_signature": "Accelerating SAS models to production"
            })
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logging.error(f"Error updating metadata: {e}")
    
    def commit_and_push(self):
        """Commit changes to Git and trigger CI/CD pipeline"""
        try:
            os.chdir(GIT_REPO_DIR)
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Create commit message
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"""🚀 SAS Model Update - {timestamp}

🎯 Thakral One: 5-Minute Model-to-Market Demo
📊 Credit Risk Model v2.0 from SAS Model Studio
⚡ Automated deployment pipeline triggered

Features: Income, Age, LoanAmount, CreditScore, DebtToIncome, EmploymentYears, LoanTerm
Target: Credit Risk Classification
Source: SAS Model Studio → Git → Container → Production

🤖 Generated with Thakral One Automation
Co-Authored-By: SAS Model Studio <sas@thakralone.com>"""

            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push to trigger CI/CD
            subprocess.run(['git', 'push'], check=True)
            
            logging.info("🚀 Successfully committed and pushed model updates")
            logging.info("⏱️  CI/CD pipeline should now begin the 5-minute countdown!")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Git operations failed: {e}")
        except Exception as e:
            logging.error(f"❌ Error in commit and push: {e}")

def main():
    """Main function to start the SAS file watcher"""
    logging.info("🎬 Starting Thakral One SAS-to-Git Sync Service")
    logging.info(f"👀 Watching SAS directory: {SAS_OUTPUT_DIR}")
    logging.info(f"📁 Git repository: {GIT_REPO_DIR}")
    
    # Create directories if they don't exist
    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    
    # Set up file watcher
    event_handler = SASModelHandler()
    observer = Observer()
    
    # Watch both the SAS output directory and Git sync trigger
    try:
        observer.schedule(event_handler, SAS_OUTPUT_DIR, recursive=False)
        observer.schedule(event_handler, "C:\\SAS_Event_Demo\\git_sync", recursive=False)
        observer.start()
        
        logging.info("✅ File watcher started successfully")
        logging.info("🎯 Ready for SAS Model Studio updates!")
        logging.info("💡 Run your SAS automation script to trigger the demo")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logging.info("🛑 Stopping file watcher...")
        
        observer.join()
        
    except Exception as e:
        logging.error(f"❌ Error starting file watcher: {e}")

if __name__ == "__main__":
    main()