import base64
from datetime import datetime, timezone, timedelta
import json
from helpers.constants import (
    PROPERTY_KEY_DEFINES,
    RADIATOR_ONTOLOGY,
    SEARCH_TWINS,
    SEND_INPUT_MESSAGE,
    UPSERT_TWIN,
)
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

    headers: dict = {
        "accept": "application/json",
        "Iotics-ClientAppId": "twin_sender",  # Namespace used to group all the requests/responses
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",  # This is where the token will be used
    }

    ##### TWIN SETUP #####
    ### 4. CREATE TWIN IDENTITY WITH CONTROL DELEGATION
    twin_motion_sensor_identity = identity_api.create_twin_with_control_delegation(
        # The Twin Key Name's concept is the same as Agent and User Key Name
        twin_key_name="TwinMotionSensor",
        # It is a best-practice to re-use the "AGENT_SEED" as a Twin seed.
        twin_seed=bytes.fromhex(AGENT_SEED),
        agent_registered_identity=agent_identity,
    )

    ### 5. DEFINE TWIN'S STRUCTURE
    ### 6. CREATE DIGITAL TWIN RADIATOR
    """We can now use the Upsert Twin operation in order to:
    1. Create the Digital Twin;
    2. Add Twin's Metadata;
    3. Add a Input object (Input's Metadata + Input's Value) to this Twin."""
    upsert_twin_payload = {"twinId": {"id": twin_motion_sensor_identity.did}}
    make_api_call(
        method=UPSERT_TWIN.method,
        endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
        headers=headers,
        payload=upsert_twin_payload,
    )

    print(f"Twin {twin_motion_sensor_identity.did} upserted succesfully")

    ### 7. SEARCH FOR TWIN RECEIVER BY LABEL
    """We need to Search in the entire Network of Spaces (scope=GLOBAL)
    rather than locally (scope=LOCAL) in order to find Twins in a remote Host.
    The only search parameter we want to use for the sake of this exercise is the Twin's Label
    which must match exactly the Label of the Twin we want to find (and then take all the info we need)."""
    search_headers = headers.copy()
    search_headers.update(
        {
            "Iotics-RequestTimeout": (
                datetime.now(tz=timezone.utc) + timedelta(seconds=3)
            ).isoformat()
        }
    )

    payload = {
        "responseType": "FULL",
        "filter": {
            "text": "LP",
            "properties": [
                {
                    "key": PROPERTY_KEY_DEFINES,
                    "uriValue": {"value": RADIATOR_ONTOLOGY},
                }
            ],
        },
    }

    twins_found_list = search_twins(
        method=SEARCH_TWINS.method,
        endpoint=SEARCH_TWINS.url.format(host=HOST_URL),
        headers=search_headers,
        payload=payload,
        scope="LOCAL",
    )

    twin_radiator = twins_found_list[0]

    """The search result will return an empty list of Twins found.
    In fact the Twin we want to search is not 'findable' from other Hosts
    unless its hostMetadataAllowList is set either to All Host or
    the Host ID from which we are searching for."""

    ### 8. SEND INPUT MESSAGES
    """Once the Twin Receiver has been found,
    we can take all the info needed to send the Input message."""
    message = {"turn_on": True}
    encoded_data = base64.b64encode(json.dumps(message).encode()).decode()
    payload = {"message": {"data": encoded_data, "mime": "application/json"}}

    make_api_call(
        method=SEND_INPUT_MESSAGE.method,
        endpoint=SEND_INPUT_MESSAGE.url.format(
            host=HOST_URL,
            twin_sender_did=twin_motion_sensor_identity.did,
            twin_receiver_host_id=twin_radiator["twinId"]["hostId"],
            twin_receiver_did=twin_radiator["twinId"]["id"],
            input_id=twin_radiator["inputs"][0]["inputId"]["id"],
        ),
        headers=headers,
        payload=payload,
    )


if __name__ == "__main__":
    main()