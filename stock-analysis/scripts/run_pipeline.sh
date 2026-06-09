#!/bin/bash
# Daily stock screening pipeline

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/pipeline_$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') start ===" >> "$LOG_FILE"
/usr/bin/python3 "$SCRIPT_DIR/run_pipeline.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
echo "=== $(date '+%Y-%m-%d %H:%M:%S') end (exit=$EXIT_CODE) ===" >> "$LOG_FILE"

# Keep only the last 30 days of logs
find "$LOG_DIR" -name "pipeline_*.log" -mtime +30 -delete

exit $EXIT_CODE
