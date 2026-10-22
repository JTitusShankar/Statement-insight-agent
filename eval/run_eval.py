import json
import sys
from pathlib import Path
from time import sleep

project_folder = Path(__file__).parent.parent
sys.path.append(str(project_folder))

from agent import get_agent

# Added this to ensure robustness. During testing, I noticed that the LLM's non-deterministic nature leads to different results even with the same input.
ITERATIONS = 3

FORMAT_INSTRUCTIONS = (
    " Respond strictly in this format only, one entry per line: "
    "account | date | merchant_name | amount "
    "For recurring charges, list every monthly occurrence. Do not summarize. "
    "Use the exact date format from the statements. List only the relevant items."
)

def get_reply_text(response):
    texts = []
    for block in response.message["content"]:
        if "text" in block:
            texts.append(block["text"])
    return "\n".join(texts)


def parse_entries(text):
    entries = []
    for line in str(text).splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 4:
            continue
        account, date, merchant, amount = parts
        try:
            amount_value = float(amount)
        except ValueError:
            continue
        entries.append((account.lower(), date, merchant.lower(), amount_value))
    return entries


cases_file = Path(__file__).parent / "cases.json"
with cases_file.open() as f:
    cases = json.load(f)


# To test accuracy with multi-turn history
KEEP_HISTORY = False

agent = get_agent()
correct = 0

for iteration in range(ITERATIONS):
    print("Iteration", iteration + 1)
    print()

    for case in cases:
        if not KEEP_HISTORY:
            agent.messages = []
        prompt = case["question"] + FORMAT_INSTRUCTIONS
        reply = get_reply_text(agent(prompt))
        found = parse_entries(reply)
        expected = parse_entries("\n".join(case["expected_recurring"] + case["expected_unusual"]))

        passed = True

        if len(expected) != len(found): #Since its a bank statement analysis agent, strict checking is necessary
            passed = False
        else:
            for item in expected:
                if item not in found:
                    passed = False
                    break

        if passed:
            correct += 1
            print(case["id"] + ": PASS")
        else:
            print(case["id"] + ": FAIL")

        print()
        print(f"Expected: {expected}")
        print(f"Found: {found}")
        print()

        sleep(60) #I noticed that automated testing hits Groq's rate limit, hence adding a delay

total = len(cases) * ITERATIONS
accuracy = 100 * correct / total
print()
print("Iterations:", ITERATIONS)
print("Cases run:", total)
print("Fully correct:", correct)
print("Accuracy:", round(accuracy, 1), "%")
