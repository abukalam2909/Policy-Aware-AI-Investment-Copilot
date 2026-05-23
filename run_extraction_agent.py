import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from agentic_app.scripts.run_extraction_agent import main

if __name__ == "__main__":
    main()
