import base64
import json
from random import randint
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COLOUR,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_DEFINES,
    PROPERTY_KEY_FROM_MODEL,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_SPACE_NAME,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_MODEL,
    SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    SHARE_FEED_DATA,
    UNIT_DEGREE_CELSIUS,
    UPSERT_TWIN,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.utilities import get_host_endpoints, make_api_call
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""

AGENT_KEY_NAME = ""
AGENT_SEED = ""


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
        "Iotics-ClientAppId": "publisher_connector",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    ##### TWIN SETUP #####
    ### 4. CREATE TWIN TEMPERATURE MODEL IDENTITY WITH CONTROL DELEGATION
    twin_temperature_model_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinTemperatureModel",
        twin_seed=bytes.fromhex(AGENT_SEED),
        agent_registered_identity=agent_identity,
    )

    ### 5. DEFINE TWIN MODEL'S STRUCTURE
    properties_twin_model = [
        {"key": PROPERTY_KEY_TYPE, "uriValue": {"value": PROPERTY_VALUE_MODEL}},
        {
            "key": PROPERTY_KEY_LABEL,
            "langLiteralValue": {"value": "Twin Temperature Model - LP", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_COMMENT,
            "langLiteralValue": {
                "value": "This is a Twin Temperature Model",
                "lang": "en",
            },
        },
        {
            "key": PROPERTY_KEY_DEFINES,
            "uriValue": {"value": SAREF_TEMPERATURE_SENSOR_ONTOLOGY},
        },
        {
            "key": PROPERTY_KEY_SPACE_NAME,
            "stringLiteralValue": {"value": "Replace with Space Name"},
        },
        {
            "key": PROPERTY_KEY_COLOUR,
            "stringLiteralValue": {"value": "#9aceff"},
        },
        {
            "key": PROPERTY_KEY_CREATED_BY,
            "stringLiteralValue": {"value": "Lorenzo"},
        },
    ]

    feed_id = "temperature"
    feed_label = "sensor_reading"
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
                    "label": feed_label,
                    "unit": UNIT_DEGREE_CELSIUS,
                }
            ],
        },
    ]

    ### 6. CREATE DIGITAL TWIN MODEL
    upsert_twin_payload = {
        "twinId": {"id": twin_temperature_model_identity.did},
        "properties": properties_twin_model,
        "feeds": feeds,
    }
    make_api_call(
        method=UPSERT_TWIN.method,
        endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
        headers=headers,
        payload=upsert_twin_payload,
    )

    print(f"Twin Model {twin_temperature_model_identity.did} created succesfully")

    ### 7. CREATE DIGITAL TWINS FROM MODEL
    twin_from_model_id_list = []
    for temp_sensor in range(2):
        twin_temperature_identity = identity_api.create_twin_with_control_delegation(
            twin_key_name=f"TwinTemperature{temp_sensor}",
            twin_seed=bytes.fromhex(AGENT_SEED),
            agent_registered_identity=agent_identity,
        )

        properties_twin_from_model = [
            {
                "key": PROPERTY_KEY_FROM_MODEL,
                "uriValue": {"value": twin_temperature_model_identity.did},
            },
            {
                "key": PROPERTY_KEY_LABEL,
                "langLiteralValue": {
                    "value": f"Twin Temperature {temp_sensor+1} - LP",
                    "lang": "en",
                },
            },
            {
                "key": PROPERTY_KEY_COMMENT,
                "langLiteralValue": {
                    "value": "This is a Twin Temperature",
                    "lang": "en",
                },
            },
            {
                "key": PROPERTY_KEY_DEFINES,
                "uriValue": {"value": SAREF_TEMPERATURE_SENSOR_ONTOLOGY},
            },
            {
                "key": SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY,
                "stringLiteralValue": {"value": "T1234"},
            },
            {
                "key": PROPERTY_KEY_SPACE_NAME,
                "stringLiteralValue": {"value": "Replace with Space Name"},
            },
            {
                "key": PROPERTY_KEY_COLOUR,
                "stringLiteralValue": {"value": "#9aceff"},
            },
            {
                "key": PROPERTY_KEY_CREATED_BY,
                "stringLiteralValue": {"value": "Lorenzo"},
            },
            # Add later
            {
                "key": PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
                "uriValue": {"value": "Replace with Host ID"},
            },
            {
                "key": PROPERTY_KEY_HOST_ALLOW_LIST,
                "uriValue": {"value": "Replace with Host ID"},
            },
        ]

        upsert_twin_payload = {
            "twinId": {"id": twin_temperature_identity.did},
            "properties": properties_twin_from_model,
            "feeds": feeds,
        }

        make_api_call(
            method=UPSERT_TWIN.method,
            endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
            headers=headers,
            payload=upsert_twin_payload,
        )
        print(f"Twin {twin_temperature_model_identity.did} created succesfully")

        twin_from_model_id_list.append(twin_temperature_identity.did)

    ##### TWIN INTERACTION #####
    ### 8. SHARE TEMPERATURE DATA
    while True:
        try:
            for twin_id in twin_from_model_id_list:
                data_to_share = {feed_label: randint(1, 30)}
                encoded_data = base64.b64encode(
                    json.dumps(data_to_share).encode()
                ).decode()
                payload = {"sample": {"data": encoded_data, "mime": "application/json"}}

                make_api_call(
                    method=SHARE_FEED_DATA.method,
                    endpoint=SHARE_FEED_DATA.url.format(
                        host=HOST_URL, twin_id=twin_id, feed_id=feed_id
                    ),
                    headers=headers,
                    payload=payload,
                )

                print(f"Shared {data_to_share} from Twin ID {twin_id}")

            sleep(2)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
