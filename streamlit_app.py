"""
Streamlit Cloud Entry Point for Personal Career AI Engine.

Run locally with:
    streamlit run streamlit_app.py

Or on Streamlit Community Cloud:
    Automatically discovered as the root main app file.
"""

import sys
import runpy
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Target entry point in career_ai.app
APP_PATH = PROJECT_ROOT / "career_ai" / "app" / "streamlit_app.py"

if __name__ == "__main__" or "streamlit" in sys.modules:
    runpy.run_path(str(APP_PATH), run_name="__main__")
