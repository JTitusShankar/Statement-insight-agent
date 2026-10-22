import logging

from strands import Agent

from models import get_model
from tools import get_all_transactions

# To hide a Strands warning from the model that arises from using groq's free tier models.
logging.getLogger("strands.models.openai").setLevel(logging.ERROR)

SYSTEM_PROMPT = """
You analyze multi-account bank statements. Use the tool to fetch transactions.

Recurring/subscription: same merchant and same amount in more than one month. Include every one of those transactions.
New: the merchant name appears only once across all accounts in the whole statement.
Unusual: one charge is more than double of each of that merchant's other individual charges across all accounts in the whole statement. Include only that large charge, not the normal ones. A new merchant regardless of the amount is considered unusual because it appears only once in the statement.
Return only the transactions in the categories the question asks for. 

Only use data returned by the tool. Do not invent transactions.
"""

def get_agent():
    return Agent(
        model=get_model(),
        tools=[get_all_transactions],
        system_prompt=SYSTEM_PROMPT,
    )


def main():
    agent = get_agent()
    print("Ask about your statements. Type 'quit' to exit.")
    print()

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        response = agent(user_input)
        print(response.message['content'][1]['text']) # type: ignore
        print()


if __name__ == "__main__":
    main()