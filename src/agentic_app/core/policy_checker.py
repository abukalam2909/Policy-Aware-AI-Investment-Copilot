import json
import sys
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize(value):
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _parse_revenue(raw: str) -> int:
    if not raw:
        return 0
    cleaned = raw.replace("$", "").replace(",", "").replace(" ", "")
    # strip currency codes like "cad", "usd"
    for code in ("cad", "usd", "eur", "gbp"):
        cleaned = cleaned.replace(code, "")
    cleaned = cleaned.strip()
    try:
        if cleaned.endswith("m"):
            return int(float(cleaned[:-1]) * 1_000_000)
        if cleaned.endswith("k"):
            return int(float(cleaned[:-1]) * 1_000)
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0


def matches_geography(country: str, allowed_geographies: list[str]) -> bool:
    normalized_country = normalize(country)
    region_map = {
        "north america": ["canada", "united states", "usa", "u.s.", "mexico"],
        "europe": ["germany", "france", "uk", "united kingdom", "spain", "italy"],
    }

    for allowed in allowed_geographies:
        allowed_norm = allowed.strip().lower()
        if allowed_norm == normalized_country:
            return True
        if allowed_norm in region_map and normalized_country in region_map[allowed_norm]:
            return True
    return False


def check_policy(policy: dict, startup: dict) -> dict:
    results = []
    passed = True

    geography = startup.get("country", "")
    allowed_geographies = policy.get("allowed_geographies", [])
    if not matches_geography(geography, allowed_geographies):
        results.append({"check": "geography", "status": "fail", "reason": f"Country '{geography}' is not in allowed geographies."})
        passed = False
    else:
        results.append({"check": "geography", "status": "pass", "reason": f"Country '{geography}' is allowed."})

    stage = normalize(startup.get("stage"))
    allowed_stages = [s.strip().lower() for s in policy.get("allowed_stages", [])]
    if stage not in allowed_stages:
        results.append({"check": "stage", "status": "fail", "reason": f"Stage '{startup.get('stage')}' is not in allowed stages."})
        passed = False
    else:
        results.append({"check": "stage", "status": "pass", "reason": f"Stage '{startup.get('stage')}' is allowed."})

    sector = normalize(startup.get("sector"))
    allowed_sectors = [s.strip().lower() for s in policy.get("allowed_sectors", [])]
    disallowed_sectors = [s.strip().lower() for s in policy.get("disallowed_sectors", [])]
    if any(disallowed in sector for disallowed in disallowed_sectors):
        results.append({"check": "sector", "status": "fail", "reason": f"Sector '{startup.get('sector')}' is explicitly disallowed."})
        passed = False
    elif any(allowed in sector for allowed in allowed_sectors):
        results.append({"check": "sector", "status": "pass", "reason": f"Sector '{startup.get('sector')}' aligns with allowed sectors."})
    else:
        results.append({"check": "sector", "status": "caution", "reason": f"Sector '{startup.get('sector')}' does not clearly match allowed sectors."})
        passed = False

    minimum_revenue_by_stage = policy.get("minimum_revenue_by_stage", {})
    stage_key = startup.get("stage", "")
    required_revenue = minimum_revenue_by_stage.get(stage_key, 0)
    revenue_raw = normalize(startup.get("current_revenue"))
    revenue_value = _parse_revenue(revenue_raw)

    if required_revenue and revenue_value < required_revenue:
        results.append({"check": "revenue", "status": "caution", "reason": f"Current revenue ${revenue_value} is below the required ${required_revenue} for stage {startup.get('stage')}.", "required": required_revenue, "current": revenue_value})
    else:
        results.append({"check": "revenue", "status": "pass", "reason": f"Current revenue ${revenue_value} meets stage requirement."})

    if not startup.get("financial_docs_provided", False):
        results.append({"check": "financial_documents", "status": "caution", "reason": "Financial documentation is not provided; human reviewer should verify financial claims before deeper diligence."})

    overall_status = "pass" if passed else "review"
    return {
        "startup": startup.get("company"),
        "policy": policy.get("policy_name"),
        "overall_status": overall_status,
        "results": results,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python src/policy_checker.py <policy.json> <startup.json>")
        sys.exit(1)

    policy_path = Path(sys.argv[1])
    startup_path = Path(sys.argv[2])

    policy = load_json(policy_path)
    startup = load_json(startup_path)
    report = check_policy(policy, startup)

    print(json.dumps(report, indent=2))
