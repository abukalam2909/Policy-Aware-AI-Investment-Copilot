import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from agentic_app.scripts.run_full_pipeline import run_full_pipeline

sample_pdf = BASE_DIR / "src" / "agentic_app" / "samples" / "sample_pitch_deck.pdf"
sample_policy = BASE_DIR / "src" / "agentic_app" / "samples" / "sample_policy.json"
output_dir = BASE_DIR / "tests" / "output"
output_dir.mkdir(exist_ok=True)

result = run_full_pipeline(sample_pdf, sample_policy, output_dir)

# Verify extraction
assert result["startup"]["company"] == "GreenFleet AI"
assert result["startup"]["sector"] == "Logistics AI"

# Verify policy result
assert result["policy_result"]["overall_status"] in {"pass", "review"}
assert result["policy_result"]["results"]

print("Full pipeline test passed")
print("Startup:", json.dumps(result["startup"], indent=2))
print("Policy Result:", json.dumps(result["policy_result"], indent=2))
