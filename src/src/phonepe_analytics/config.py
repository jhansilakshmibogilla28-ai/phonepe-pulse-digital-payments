from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_REPO = ROOT / "data" / "raw"
RAW_DATA = RAW_REPO / "data"
PROCESSED = ROOT / "data" / "processed"

PHONEPE_REPO = "https://github.com/PhonePe/pulse.git"

OUTPUT_FILES = {
    "transactions": PROCESSED / "aggregated_transactions.csv",
    "state_transactions": PROCESSED / "state_transactions.csv",
    "users": PROCESSED / "users.csv",
    "merchants": PROCESSED / "merchants.csv",
}
