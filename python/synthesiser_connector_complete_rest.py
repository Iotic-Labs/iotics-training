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
    ### 4. CREATE TWIN SYNTHESISER IDENTITY WITH CONTROL DELEGATION
    twin_thermostat_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinThermostat",
        twin_seed=bytes.fromhex(AGENT_SEED),
        agent_registered_identity=agent_identity,
    )

    ### 5. DEFINE TWIN'S STRUCTURE
    properties = [
        {
            "key": PROPERTY_KEY_LABEL,
            "langLiteralValue": {"value": "Twin Thermostat - LP", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_COMMENT,
            "langLiteralValue": {"value": "This is a Twin Thermostat", "lang": "en"},
        },
    ]

    ### 6. CREATE DIGITAL TWIN TERMOSTAT
    upsert_twin_payload = {
        "twinId": {"id": twin_thermostat_identity.did},
        "properties": properties,
    }
    make_api_call(
        method=UPSERT_TWIN.method,
        endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
        headers=headers,
        payload=upsert_twin_payload,
    )

    print(f"Twin {twin_thermostat_identity.did} created succesfully")

    ##### TWIN INTERACTION #####
    ### 7. SEARCH FOR TWIN RADIATOR
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
                    "key": PROPERTY_KEY_TYPE,
                    "uriValue": {"value": RADIATOR_ONTOLOGY},
                }
            ],
        },
    }

    print("Searching for Twin Radiator...")

    twins_found_list = search_twins(
        method=SEARCH_TWINS.method,
        endpoint=SEARCH_TWINS.url.format(host=HOST_URL),
        headers=search_headers,
        payload=payload,
        scope="LOCAL",
    )

    print(f"Found {len(twins_found_list)} Twins")

    twin_radiator = twins_found_list[0]

    ### 8. SEARCH FOR TWIN TEMPERATURE SENSOR
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
                    "uriValue": {"value": SAREF_TEMPERATURE_SENSOR_ONTOLOGY},
                }
            ],
        },
    }

    print("Searching for Temperature Sensor Twins...")

    twins_found_list = search_twins(
        method=SEARCH_TWINS.method,
        endpoint=SEARCH_TWINS.url.format(host=HOST_URL),
        headers=search_headers,
        payload=payload,
        scope="GLOBAL",
    )

    print(f"Found {len(twins_found_list)} Twins")

    def thermostat_logic(temperature):
        message = {"turn_on": False}
        if temperature <= 15:
            message = {"turn_on": True}

        encoded_data = base64.b64encode(json.dumps(message).encode()).decode()
        payload = {"message": {"data": encoded_data, "mime": "application/json"}}

        make_api_call(
            method=SEND_INPUT_MESSAGE.method,
            endpoint=SEND_INPUT_MESSAGE.url.format(
                host=HOST_URL,
                twin_sender_id=twin_thermostat_identity.did,
                twin_receiver_host_id=twin_radiator["twinId"]["hostId"],
                twin_receiver_id=twin_radiator["twinId"]["id"],
                input_id=twin_radiator["inputs"][0]["inputId"]["id"],
            ),
            headers=headers,
            payload=payload,
        )

        print(f"Sent Input message {message}")

    @staticmethod
    def receiver_callback(headers, feed_data):
        encoded_data = json.loads(feed_data)

        try:
            data = encoded_data["feedData"]["data"]
        except KeyError:
            print("A KeyError occurred in the receiver_callback")
        else:
            decoded_feed_data = json.loads(base64.b64decode(data).decode("ascii"))
            thermostat_logic(decoded_feed_data["sensor_reading"])

    stomp_client = StompClient(
        stomp_endpoint=endpoints.get("stomp"), callback=receiver_callback, token=token
    )

    ### 9. SUBSCRIBE TO FEED DATA
    for twin_temperature in twins_found_list:
        twin_publisher_host_id = twin_temperature["twinId"]["hostId"]
        twin_publisher_id = twin_temperature["twinId"]["id"]
        feed_id = twin_temperature["feeds"][0]["feedId"]["id"]

        stomp_client.subscribe(
            topic=SUBSCRIBE_TO_FEED.url.format(
                twin_follower_id=twin_thermostat_identity.did,
                twin_publisher_host_id=twin_publisher_host_id,
                twin_publisher_id=twin_publisher_id,
                feed_id=feed_id,
            ),
            subscription_id=f"{twin_publisher_id}-{feed_id}",
        )

    while True:
        try:
            sleep(10)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
