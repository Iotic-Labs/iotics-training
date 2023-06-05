import base64
import json
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL,
    RADIATOR_ONTOLOGY,
    SUBSCRIBE_TO_INPUT,
    UPSERT_TWIN,
)
from helpers.stomp_client import StompClient
from helpers.utilities import get_host_endpoints, make_api_call
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
    """A User and an Agent Identity need to be created with Authentication Delegation so you can:
    1. Create Twin Identities;
    2. Generate a Token to use the IOTICS API.
    Be aware that, if Key Name and Seed don't change, multiple calls of the following function
    will not create new Identities, it will retrieve the existing ones."""
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
    """Any IOTICS operation requires a token (JWT). The latter can be created using:
    1. A User DID;
    2. An Agent Identity;
    3. A duration (in seconds)
    This token will only be valid for the duration expressed on point 3 above.
    When the token expires you won't be able to use the API so you need to generate a new token.
    Please remember that the longer the token's duration, the less secure your Twins are.
    (The token may be stolen and a malicious user can use your Twins on your behalf)."""
    token = identity_api.create_agent_auth_token(
        agent_registered_identity=agent_identity,
        user_did=user_identity.did,
        duration=600,
    )

    headers: dict = {
        "accept": "application/json",
        "Iotics-ClientAppId": "twin_radiator",  # Namespace used to group all the requests/responses
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",  # This is where the token will be used
    }

    ##### TWIN SETUP #####
    ### 4. CREATE TWIN RADIATOR IDENTITY WITH CONTROL DELEGATION
    """ We now need to create a new Twin Identity which will be used for our Twin Radiator.
    Only Agents can perform actions against a Twin.
    This means, after creating the Twin Identity it has to "control-delegate" an Agent Identity
    so the latter can control the Digital Twin."""
    twin_radiator_identity = identity_api.create_twin_with_control_delegation(
        # The Twin Key Name's concept is the same as Agent and User Key Name
        twin_key_name="TwinRadiator",
        # It is a best-practice to re-use the "AGENT_SEED" as a Twin seed.
        twin_seed=bytes.fromhex(AGENT_SEED),
        agent_registered_identity=agent_identity,
    )

    ### 5. DEFINE TWIN'S STRUCTURE
    properties = [
        {
            "key": PROPERTY_KEY_LABEL,
            "langLiteralValue": {"value": "Twin Radiator - LP", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_COMMENT,
            "langLiteralValue": {"value": "This is a Twin Radiator", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_TYPE,
            "uriValue": {"value": RADIATOR_ONTOLOGY},
        },
        ### Add the following 2 Properties later ###
        {
            "key": PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
            "uriValue": {"value": PROPERTY_VALUE_ALLOW_ALL},
        },
        {
            "key": PROPERTY_KEY_HOST_ALLOW_LIST,
            "uriValue": {"value": PROPERTY_VALUE_ALLOW_ALL},
        },
    ]

    input_id = "radiator_switch"
    input_label = "turn_on"
    inputs = [
        {
            "id": input_id,
            "properties": [
                {
                    "key": PROPERTY_KEY_LABEL,
                    "langLiteralValue": {"value": "ON/OFF switch", "lang": "en"},
                }
            ],
            "values": [
                {
                    "comment": "ON/OFF switch for the Radiator",
                    "dataType": "boolean",
                    "label": input_label,
                }
            ],
        }
    ]

    ### 6. CREATE DIGITAL TWIN RADIATOR
    """We can now use the Upsert Twin operation in order to:
    1. Create the Digital Twin;
    2. Add Twin's Metadata;
    3. Add a Input object (Input's Metadata + Input's Value) to this Twin."""
    upsert_twin_payload = {
        "twinId": {"id": twin_radiator_identity.did},
        "location": {"lat": 51.5, "lon": -0.1},
        "properties": properties,
        "inputs": inputs,
    }
    make_api_call(
        method=UPSERT_TWIN.method,
        endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
        headers=headers,
        payload=upsert_twin_payload,
    )

    print(f"Twin {twin_radiator_identity.did} upserted succesfully")

    ##### TWIN INTERACTION #####
    ### 7. WAIT FOR INPUT MESSAGES
    """Here is where STOMP comes into action.
    The 'receiver_callback' will simply print received messages on the terminal."""

    @staticmethod
    def receiver_callback(input_message):
        encoded_data = json.loads(input_message)

        try:
            data = encoded_data["message"]["data"]
        except KeyError:
            print("A KeyError occurred in the receiver_callback")
        else:
            decoded_feed_data = json.loads(base64.b64decode(data).decode("ascii"))
            print(decoded_feed_data)

    stomp_client = StompClient(
        stomp_endpoint=endpoints.get("stomp"),
        callback=receiver_callback,
        token=token,
    )

    stomp_client.subscribe(
        topic=SUBSCRIBE_TO_INPUT.url.format(
            twin_receiver_did=twin_radiator_identity.did, input_id=input_id
        ),
        subscription_id=f"{twin_radiator_identity.did}-{input_id}",
    )

    print("Waiting for Input messages...")

    while True:
        sleep(10)


if __name__ == "__main__":
    main()
