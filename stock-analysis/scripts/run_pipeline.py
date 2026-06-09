import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(script_name):
    script_path = ROOT / "scripts" / script_name
    subprocess.run([sys.executable, str(script_path)], check=True)


def main():
    print("Running full pipeline...")
    run("fetch_stock_data.py")
    run("generate_report.py")
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
