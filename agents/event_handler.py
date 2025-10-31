# agents/event_handler.py
import os
import time
import json

def run_event_handler(bus, log_path="logs/system.log"):
    """
    Watches the given log file in real-time.
    Whenever a new line containing 'ERROR' is added, it publishes an 'issue.detected' event.
    """

    print("[EventHandler] Watching logs...")

    # make sure log file exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        open(log_path, "w").close()

    # open file and go to end
    with open(log_path, "r") as log_file:
        log_file.seek(0, os.SEEK_END)

        while True:
            line = log_file.readline()

            # if no new line, wait and continue
            if not line:
                time.sleep(1)
                continue

            # optional debug
            # print("[Debug] Line read:", line.strip())

            # detect error lines
            if "ERROR" in line:
                parts = line.strip().split(":")
                if len(parts) >= 2:
                    error_type = parts[1].strip()
                else:
                    error_type = "unknown"

                data = {
                    "error_type": error_type,
                    "raw": line.strip(),
                    "timestamp": time.time()
                }

                # print for debugging  
                print(f"[EventHandler] Detected issue: {{'error_type': '{error_type}', ...}}")
                print(f"[EventHandler] Detected issue: {data}")

                # publish event to bus
                bus.publish("issue.detected", data)

            # (optional) also log into telemetry file
            try:
                if line.strip():  # Only log non-empty lines
                    os.makedirs("insightflow", exist_ok=True)
                    with open("insightflow/telemetry.json", "a", encoding='utf-8') as f:
                        clean_data = line.strip().replace('\x00', '')  # Remove null characters
                        f.write(json.dumps({"event": "log_line", "data": clean_data}) + "\n")
            except Exception:
                pass
