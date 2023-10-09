import base64
import json
import logging
import sys
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import uuid

import requests
from helpers.constants import INDEX_JSON_PATH


def get_host_endpoints(host_url: str) -> dict:
    if not host_url:
        logging.error("Parameter HOST_URL not set")
        sys.exit(1)

    index_json: str = host_url + INDEX_JSON_PATH
    req_resp: dict = {}

    try:
        req_resp = requests.get(index_json).json()
    except requests.exceptions.ConnectionError:
        logging.error(
            "Can't connect to %s. Check HOST_URL is spelt correctly", index_json
        )
        sys.exit(1)

    return req_resp


def make_api_call(
    method: str,
    endpoint: str,
    headers: Optional[dict] = None,
    payload: Optional[dict] = None,
) -> dict:
    """This method will simply execute a REST call according to a specific
    method, endpoint and optional headers and payload."""

    try:
        req_resp: requests.Response = requests.request(
            method=method, url=endpoint, headers=headers, json=payload
        )
        req_resp.raise_for_status()
        response: dict = req_resp.json()
    except Exception as ex:
        print("Getting error", ex)
        sys.exit(1)

    return response


def search_twins(
    method: str, endpoint: str, headers: dict, payload: dict, scope: str
) -> List[dict]:
    # The following variable will be used to append any Twins found by the Search operation
    twins_found_list = []

    search_headers = headers.copy()
    search_headers.update(
        {
            "Iotics-RequestTimeout": (
                datetime.now(tz=timezone.utc) + timedelta(seconds=3)
            ).isoformat()
        }
    )

    # We can now use the Search operation over REST by specifying the 'scope' parameter.
    # The latter defines where to search for Twins, either locally ('LOCAL') in the Space defined by the 'HOST_URL'
    # or globally ('GLOBAL') in the Network.
    with requests.request(
        method=method,
        url=endpoint,
        headers=search_headers,
        stream=True,
        verify=True,
        params={"scope": scope},
        json=payload,
    ) as resp:
        resp.raise_for_status()
        # Iterates over the response data, one Host at a time
        for chunk in resp.iter_lines():
            response = json.loads(chunk)
            twins_found = []
            try:
                twins_found = response["result"]["payload"]["twins"]
            except KeyError:
                continue
            finally:
                if twins_found:
                    # Append the twins found to the list of twins
                    twins_found_list.extend(twins_found)

    return twins_found_list


def decode_data(data: str):
    decoded_data = json.loads(base64.b64decode(data).decode("ascii"))

    return decoded_data


def encode_data(data: dict):
    encoded_data = base64.b64encode(json.dumps(data).encode()).decode()

    return encoded_data


def generate_headers(token: str) -> dict:
    headers = {
        "accept": "application/json",
        "Iotics-ClientAppId": uuid.uuid4().hex,  # Namespace used to group all the requests/responses
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",  # This is where the token will be used
    }

    return headers
