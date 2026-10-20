from strands import Agent

from models import get_model
from tools import get_all_transactions

SYSTEM_PROMPT = """
You analyze multi-account bank statements. Use the tool to fetch transactions. 
Identify:
1. Recurring charges (same merchant appearing across multiple months with similar amounts).
2. Unusual or new charges (a merchant never seen before, or an unusually high amount at a familiar merchant).
Be concise. Only use data returned by the tool. Do not invent transactions.
"""

agent = Agent(
    model=get_model(),
    tools=[get_all_transactions],
    system_prompt=SYSTEM_PROMPT
)


if __name__ == "__main__":
    response = agent("Are there any unusual or new charges I should look at?")
    print(response)