import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from agentic_app.core.extractor import extract_text_from_pdf, heuristic_parse_submission

sample_pdf = BASE_DIR / "src" / "agentic_app" / "samples" / "sample_pitch_deck.pdf"
text = extract_text_from_pdf(sample_pdf)
assert "Company: GreenFleet AI" in text
assert "Claimed traction" in text

parsed = heuristic_parse_submission(text)
assert parsed["company"] == "GreenFleet AI"
assert parsed["sector"] == "Logistics AI"
assert parsed["stage"] == "Seed"
assert parsed["country"] == "Canada"
assert parsed["claimed_traction"].startswith("Pilot with 3 regional fleet operators")
assert parsed["revenue_model"] == "Subscription + usage fees"
print("Extraction test passed")
