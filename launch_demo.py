#!/usr/bin/env python3
"""
Launch Demo - Simple Discovery Interface

Launches a working demo of the Canvas-to-Discovery flow
without complex import dependencies.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the simple discovery demo"""

    print("🚀 Launching Data Discovery Demo...")
    print("   This will open in your browser at http://localhost:8503")
    print("   Press Ctrl+C to stop")
    print()

    # Path to the simple discovery app
    demo_app_path = Path(__file__).parent / "src" / "agentic_data_scraper" / "ui" / "simple_discovery.py"

    if not demo_app_path.exists():
        print(f"❌ Demo app not found at: {demo_app_path}")
        return 1

    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(demo_app_path),
        "--server.port", "8503",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ]

    try:
        # Run streamlit
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n👋 Demo stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start demo: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())