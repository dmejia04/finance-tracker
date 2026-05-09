# Finance Tracker

Personal finance tracker that connects to your bank via [Plaid](https://plaid.com), classifies transactions, and reports net flow and recurring spend.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Plaid credentials
```

## Usage

```bash
# fetch last 30 days and save locally
python src/main.py fetch --days 30 --save

# print report from saved file
python src/main.py report
```

## Project structure

```
src/
  bank/          # Plaid API client
  transactions/  # classification logic
  reports/       # net flow, category & weekly summaries
  main.py        # CLI entry point
data/            # local transaction cache (git-ignored)
tests/
```

## Getting a Plaid access token

1. Create a free account at https://dashboard.plaid.com
2. Grab your `client_id` and `sandbox` secret — add them to `.env`
3. Use Plaid's [Quickstart](https://github.com/plaid/quickstart) to run the Link flow and get an `access_token`
4. Add the token to `PLAID_ACCESS_TOKEN` in `.env`
