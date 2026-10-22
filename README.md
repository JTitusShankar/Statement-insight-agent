# Statement insight agent prototype

An agentic AI bank statement analyzer that helps account holders effortlessly track their finances. The core functionality implemented and tested so far identifies hidden subscriptions and unusual charges across multi-account statements, powered by the Strands Agents SDK and gpt-oss-20B hosted on Groq.

The synthetic transaction data is in `data/fake_statements.json`. It has data for two accounts, `chequing_001` and `credit_002`, for July, August, and September 2026.

## Why I built this

Like a lot of people with more than one bank account, I rarely had time to read every line of my monthly statements. That changed when I noticed Uber had been charging me $9.99 plus tax every month for an Uber One subscription I never signed up for.

Uber support informed me that the card was attached to an account that I didn't even recognize. Soon after, my dad's credit card was hit by a malicious card-validation bot. It left a trail of small charges from merchants we did not recognize.

Realizing how easy it is for subscriptions and fraudulent transactions to slip through the cracks, I decided to build an agentic AI assistant. I wanted something I could ask, in normal language, critical questions I had about charges in my bank statement.

I’ve since built and tested the initial prototype, which is now up and running. However, this is not the end. I will continue to work on this project and have big plans for it as outlined in the ***Next Steps*** section at the end.

## Setup

Use Python 3.12 or 3.13. I started on 3.15 but `pip install` failed because some packages had no Windows wheels for it yet.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Add your key to `.env`:

```
GROQ_API_KEY=your_key_here
```

Ask a question:

```powershell
python agent.py
```

Run the tests:

```powershell
python eval/run_eval.py
```

`ITERATIONS` at the top of `eval/run_eval.py` is how many times the full test suite runs. The script waits 60 seconds between cases so it does not hit the Groq free-tier rate limit.

## Files

- `agent.py` creates the agent and holds the system prompt.
- `models.py` loads the Groq model. Temperature is `0.0`.
- `tools.py` has `get_all_transactions()`, which prints one transaction per line.
- `eval/cases.json` is the labeled questions.
- `eval/run_eval.py` sends each question and scores the reply.

## How I tested it

I added `eval/run_eval.py` to perform automated testing of the model's reply against labeled test-cases (`eval/cases.json`).

To keep the comparison simple and strict, both the expected answers and the agent’s required output format match the format returned by the get_all_transactions tool (`account | date | merchant | amount`).

The test compares whole transaction rows. Order does not matter. I also added a line of code after it started returning (during preliminary testing) the right charges and then extra ones the question did not ask. Now a case fails not only if an expected transaction is missing, but also if the model adds a transaction that was not expected.

## Issues found

- A case about unusual charges was not including new merchants.
- Two cases that asked mixed intent questions i.e. asking for both recurring and unusual charges kept failing.
- Also, during repeated iterations, the LLM's non-deterministic nature started to surface i.e. a case would pass on one run, then fail on the next run with the same question.

## How I debugged

To debug, I set breakpoints in failing test cases to compare the model's inputs with the expected outputs. For cases that continued to fail, I reviewed the agent's reasoning logs and took the following actions:

1. I found that Groq's default temperature for `gpt-oss-20b` was 0.6. My AI-agent has to flag specific transactions precisely, so I set it to 0.0.
2. Tightened the prompt so recurring, new, and unusually high each mean one thing and ensured they are defined in a non-ambiguous manner.

One full test then scored 100%. To confirm mitigation of the inconsistencies encountered earlier due to the LLM's non-deterministic nature, I integrated a configurable `ITERATIONS` parameter into the evaluation script to validate the model's response consistency across a set number of test executions.

The agent scored 100% yet again when running the full test suite across 3 consecutive runs.

## Design notes

I kept the gpt-oss-20B model instead of jumping to the 120B version, which perhaps would have been an easy fix for most of the issues above.

However, in real life (for example, in production), we don’t always want to solve every issue by spending more on a bigger model. Hence, after double-checking the fit of the gpt-oss-20B model for my use case, I decided to work on tightening the prompt and conducting more testing to ensure robustness.

This proved worthwhile as the agent began working as expected after I implemented the fixes, **saving 40%–50% in average token costs**.

## Next Steps

As a certified AWS Solutions Architect Associate, I like to approach from a solutions architecure systems design perspective:

- **PDF to JSON tool implementation**: Implement or integrate a tool to parse real bank statement PDFs into structured JSONs that can be fed directly to the agent.  

- **Cloud Deployment & Scaling**: I plan to containerize the agent with Docker and deploy it on AWS ECS (so that I can use the power of the cloud to scale effortlessly) behind an Elastic Load Balancer (ELB) (to handle traffic smoothly). I’ll use S3 for low-cost, secure bank statement storage (although at its current form we are just using fake statement data).  

- **Switching to AWS Bedrock**: I’m planning to move from Groq to AWS Bedrock to keep infrastructure native to AWS. Since models.py abstracts the model and model provider, swapping out the LLM provider will be straightforward without breaking the core logic.  

- **Further Cost Optimization**: The repeated work here is classification, not writing. To save on costs further, in the future, I might move the classification step to Jev. It handles classification at a much cheaper rate ( I only have to pay for input tokens while output tokens are free) and then just use the LLM to format the final answer in a more human-friendly way.
