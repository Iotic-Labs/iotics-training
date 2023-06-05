import base64
import json
from datetime import datetime, timedelta, timezone
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_DEFINES,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    SEARCH_TWINS,
    SEND_INPUT_MESSAGE,
    SUBSCRIBE_TO_FEED,
    UPSERT_TWIN,
)
from helpers.stomp_client import StompClient
from helpers.utilities import get_host_endpoints, make_api_call, search_twins
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    ##### IDENTITY MANAGEMENT #####
    ### 1. INSTANTIATE AN IDENTITY API OBJECT
    endpoints = get_host_endpoints(host_url=HOST_URL)
    identity_api = get_rest_high_level_identity_api(
        resolver_url=endpoints.get("resolver")
    )

    ### 2. CREATE AGENT AND USER IDENTITY, THEN DELEGATE
    (
        user_identity,
        agent_identity,
    ) = identity_api.create_user_and_agent_with_auth_delegation(
        user_seed=bytes.fromhex(USER_SEED),
        user_key_name=USER_KEY_NAME,
        agent_seed=bytes.fromhex(AGENT_SEED),
        agent_key_name=AGENT_KEY_NAME,
    )

    ### 3. GENERATE NEW TOKEN AND HEADERS
    token = identity_api.create_agent_auth_token(
        agent_registered_identity=agent_identity,
        user_did=user_identity.did,
        duration=600,
    )

    headers = {
        "accept": "application/json",
        "Iotics-ClientAppId": "synthesiser_connector",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
