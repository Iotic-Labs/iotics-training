from random import randint
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    SHARE_FEED_DATA,
    UNIT_DEGREE_CELSIUS,
    UPSERT_TWIN,
    USER_KEY_NAME,
    USER_SEED,
    AGENT_SEED,
)
from helpers.utilities import get_host_endpoints, make_api_call, encode_data, generate_headers
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinPublisher"


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
        user_seed=USER_SEED,
        user_key_name=USER_KEY_NAME,
        agent_seed=AGENT_SEED,
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

    headers = generate_headers(token=token)

    ##### TWIN SETUP #####
    ### 4. CREATE TWIN TEMPERATURE IDENTITY WITH CONTROL DELEGATION
    """ We now need to create a new Twin Identity which will be used for our Twin Temperature.
    Only Agents can perform actions against a Twin.
    This means, after creating the Twin Identity it has to "control-delegate" an Agent Identity
    so the latter can control the Digital Twin."""
    twin_temperature_identity = identity_api.create_twin_with_control_delegation(
        # The Twin Key Name's concept is the same as Agent and User Key Name
        twin_key_name="TwinTemperature",
        # It is a best-practice to re-use the "AGENT_SEED" as a Twin seed.
        twin_seed=AGENT_SEED,
        # The Agent Identity we want to delegate control to
        agent_registered_identity=agent_identity,
    )

    ### 5. DEFINE TWIN'S STRUCTURE
    properties = [
        {
            "key": PROPERTY_KEY_LABEL,
            "langLiteralValue": {"value": "Twin Temperature - LP", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_COMMENT,
            "langLiteralValue": {"value": "This is a Twin Temperature", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_TYPE,
            "uriValue": {"value": SAREF_TEMPERATURE_SENSOR_ONTOLOGY},
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

    feed_id = "temperature"
    feed_value_label = "sensor_reading"
    feeds = [
        {
            "id": feed_id,
            "storeLast": True,
            "properties": [
                {
                    "key": PROPERTY_KEY_LABEL,
                    "langLiteralValue": {"value": "Temperature", "lang": "en"},
                },
                {
                    "key": PROPERTY_KEY_COMMENT,
                    "langLiteralValue": {"value": "Temperature detected", "lang": "en"},
                },
            ],
            "values": [
                {
                    "comment": "Temperature in degrees Celsius",
                    "dataType": "integer",
                    "label": feed_value_label,
                    "unit": UNIT_DEGREE_CELSIUS,
                }
            ],
        },
    ]

    ### 6. CREATE DIGITAL TWIN
    """We can now use the Upsert Twin operation in order to:
    1. Create the Digital Twin;
    2. Add Twin's Metadata;
    3. Add a Feed object (Feed's Metadata + Feed's Value) to this Twin."""
    upsert_twin_payload = {
        "twinId": {"id": twin_temperature_identity.did},
        "properties": properties,
        "feeds": feeds,
    }
    make_api_call(
        method=UPSERT_TWIN.method,
        endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
        headers=headers,
        payload=upsert_twin_payload,
    )

    print(f"Twin {twin_temperature_identity.did} created")

    ##### TWIN INTERACTION #####
    ### 7. SHARE TEMPERATURE DATA
    while True:
        try:
            data_to_share = {feed_value_label: randint(1, 30)}
            encoded_data = encode_data(data=data_to_share)
            payload = {"sample": {"data": encoded_data, "mime": "application/json"}}

            make_api_call(
                method=SHARE_FEED_DATA.method,
                endpoint=SHARE_FEED_DATA.url.format(
                    host=HOST_URL, twin_id=twin_temperature_identity.did, feed_id=feed_id
                ),
                headers=headers,
                payload=payload,
            )

            print(f"Shared {data_to_share} from Twin ID {twin_temperature_identity.did}")

            sleep(2)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
