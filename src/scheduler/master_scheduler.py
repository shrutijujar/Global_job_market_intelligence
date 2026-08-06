# src/scheduler/master_scheduler.py

import schedule
import subprocess
import time
import sys

def update_jobs():

    print("Updating jobs...")

    subprocess.run(
    [sys.executable, "src/pipeline.py"]
)

    print("Checking alerts...")

    subprocess.run(
    [sys.executable, "src/job_alert_checker.py"]
)


# Testing every 2 minutes
schedule.every(2).minutes.do(update_jobs)

print("Master Scheduler Running...")

while True:
    schedule.run_pending()
    time.sleep(60)