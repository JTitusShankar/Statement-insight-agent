import json
from pathlib import Path

from strands import tool

DATA_FILE = Path(__file__).parent / "data" / "fake_statements.json"


@tool
def get_all_transactions() -> str:
    """Return every bank transaction as a readable string.

    Use this whenever the user asks about spending, purchases, deposits,
    statements, or transaction history.

    Returns:
        One line per transaction formatted as account | date | description | amount.
    """
    with DATA_FILE.open() as f:
        by_month = json.load(f)

    lines = []
    lines.append("Account | Date | Description | Amount")

    for transactions in by_month.values():
        for t in transactions:
            lines.append(f"{t['account']} | {t['date']} | {t['description']} | {t['amount']}")

    return "\n".join(lines)
