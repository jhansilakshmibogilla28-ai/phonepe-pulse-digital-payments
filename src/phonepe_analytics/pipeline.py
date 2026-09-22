import json
import subprocess
from pathlib import Path

import pandas as pd

from .config import OUTPUT_FILES, PHONEPE_REPO, PROCESSED, RAW_DATA, RAW_REPO
from .validation import validate_transactions


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _year(path: Path) -> int:
    return int(path.parent.name)


def _quarter(path: Path) -> int:
    return int(path.stem)


def _clone_source() -> None:
    if RAW_DATA.exists():
        return
    RAW_REPO.parent.mkdir(parents=True, exist_ok=True)
    print("Downloading official PhonePe Pulse repository...")
    subprocess.run(
        ["git", "clone", "--depth", "1", PHONEPE_REPO, str(RAW_REPO)],
        check=True,
    )


def extract_transactions() -> pd.DataFrame:
    base = RAW_DATA / "aggregated" / "transaction" / "country" / "india"
    rows = []

    for year_dir in sorted(base.glob("*")):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        for path in sorted(year_dir.glob("*.json")):
            obj = _read_json(path)
            y, q = _year(path), _quarter(path)

            for item in obj.get("data", {}).get("transactionData", []):
                for instrument in item.get("paymentInstruments", []):
                    if instrument.get("type") != "TOTAL":
                        continue
                    rows.append({
                        "year": y,
                        "quarter": q,
                        "period": f"{y}-Q{q}",
                        "category": item.get("name"),
                        "transaction_count": float(instrument.get("count", 0)),
                        "transaction_amount": float(instrument.get("amount", 0)),
                    })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["transaction_amount_crore"] = df["transaction_amount"] / 1e7
    return df


def extract_state_transactions() -> pd.DataFrame:
    base = RAW_DATA / "map" / "transaction" / "hover" / "country" / "india"
    rows = []

    for year_dir in sorted(base.glob("*")):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        for path in sorted(year_dir.glob("*.json")):
            obj = _read_json(path)
            y, q = _year(path), _quarter(path)

            for item in obj.get("data", {}).get("hoverDataList", []):
                metric = next(
                    (m for m in item.get("metric", []) if m.get("type") == "TOTAL"),
                    None,
                )
                if not metric:
                    continue

                rows.append({
                    "year": y,
                    "quarter": q,
                    "period": f"{y}-Q{q}",
                    "state": item.get("name"),
                    "transaction_count": float(metric.get("count", 0)),
                    "transaction_amount": float(metric.get("amount", 0)),
                })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["transaction_amount_crore"] = df["transaction_amount"] / 1e7
    return df


def extract_entity(entity: str) -> pd.DataFrame:
    base = RAW_DATA / "aggregated" / entity / "country" / "india"
    rows = []

    for year_dir in sorted(base.glob("*")):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        for path in sorted(year_dir.glob("*.json")):
            obj = _read_json(path)
            aggregate = obj.get("data", {}).get("aggregated", {})
            if not aggregate:
                continue

            y, q = _year(path), _quarter(path)
            row = {
                "year": y,
                "quarter": q,
                "period": f"{y}-Q{q}",
                "registered_count": float(aggregate.get("registeredCount", 0)),
            }

            if "appOpens" in aggregate:
                row["app_opens"] = float(aggregate["appOpens"])

            rows.append(row)

    return pd.DataFrame(rows)


def run() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    _clone_source()

    transactions = extract_transactions()
    state_transactions = extract_state_transactions()
    users = extract_entity("user")
    merchants = extract_entity("merchant")

    validate_transactions(transactions)

    outputs = {
        OUTPUT_FILES["transactions"]: transactions,
        OUTPUT_FILES["state_transactions"]: state_transactions,
        OUTPUT_FILES["users"]: users,
        OUTPUT_FILES["merchants"]: merchants,
    }

    for path, df in outputs.items():
        df.to_csv(path, index=False)
        print(f"Created {path.relative_to(PROCESSED.parent.parent)} ({len(df):,} rows)")

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run()
