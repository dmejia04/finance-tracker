import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import date, timedelta

load_dotenv()

_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Development,
    "production": plaid.Environment.Production,
}


def get_client() -> plaid_api.PlaidApi:
    cfg = plaid.Configuration(
        host=_ENV_MAP[os.getenv("PLAID_ENV", "sandbox")],
        api_key={
            "clientId": os.environ["PLAID_CLIENT_ID"],
            "secret": os.environ["PLAID_SECRET"],
        },
    )
    return plaid_api.PlaidApi(plaid.ApiClient(cfg))


def fetch_transactions(
    access_token: str,
    days: int = 30,
    max_count: int = 500,
) -> list[dict]:
    client = get_client()
    end = date.today()
    start = end - timedelta(days=days)

    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=max_count, offset=0),
    )
    response = client.transactions_get(request)
    return [t.to_dict() for t in response.transactions]
