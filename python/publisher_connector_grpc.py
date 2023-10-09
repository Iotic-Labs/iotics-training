from random import randint
from time import sleep

from helpers.constants import (
    AGENT_SEED,
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
    UNIT_DEGREE_CELSIUS,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_feed_with_meta, create_property, create_value
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "PublisherConnector"


def main():
    ##### IDENTITY MANAGEMENT #####
    ### 1. INSTANTIATE AN IDENTITY API OBJECT
    endpoints = get_host_endpoints(host_url=HOST_URL)
    identity_api = Identity(
        resolver_url=endpoints.get("resolver"), grpc_endpoint=endpoints.get("grpc")
    )

    ### 2. CREATE AGENT AND USER IDENTITY, THEN DELEGATE
    (
        user_identity,
        agent_identity,
    ) = identity_api.create_user_and_agent_with_auth_delegation(
        user_seed=USER_SEED,
        user_key_name=USER_KEY_NAME,
        agent_seed=AGENT_SEED,
        agent_key_name=AGENT_KEY_NAME,
    )

    ### 3. GENERATE NEW TOKEN
    identity_api.refresh_token(
        agent_identity=agent_identity, user_did=user_identity.did, duration=600
    )

    ##### TWIN SETUP #####
    ### 4. INSTANTIATE IOTICSviagRPC
    iotics_api = IOTICSviagRPC(auth=identity_api)

    ### 5. CREATE TWIN TEMPERATURE MODEL IDENTITY WITH CONTROL DELEGATION
    twin_temperature_model_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinTemperatureModel",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )

    ### 6. DEFINE TWIN MODEL'S STRUCTURE
    properties_twin_model = [
        create_property(key=PROPERTY_KEY_TYPE, value=PROPERTY_VALUE_MODEL, is_uri=True),
        create_property(
            key=PROPERTY_KEY_LABEL, value="Twin Temperature Model - LP", language="en"
        ),
        create_property(
            key=PROPERTY_KEY_COMMENT,
            value="This is a Twin Temperature Model",
            language="en",
        ),
        create_property(
            key=PROPERTY_KEY_DEFINES,
            value=SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
            is_uri=True,
        ),
        create_property(key=PROPERTY_KEY_SPACE_NAME, value="Space A"),
        create_property(key=PROPERTY_KEY_COLOUR, value="#9aceff"),
        create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo"),
    ]

    feed_id = "temperature"
    feed_label = "sensor_reading"
    feeds = [
        create_feed_with_meta(
            feed_id=feed_id,
            properties=[
                create_property(
                    key=PROPERTY_KEY_LABEL, value="Temperature", language="en"
                ),
                create_property(
                    key=PROPERTY_KEY_COMMENT,
                    value="Temperature detected",
                    language="en",
                ),
            ],
            values=[
                create_value(
                    label=feed_label,
                    comment="Temperature in degrees Celsius",
                    unit=UNIT_DEGREE_CELSIUS,
                    data_type="integer",
                )
            ],
        )
    ]

    iotics_api.upsert_twin(
        twin_did=twin_temperature_model_identity.did,
        properties=properties_twin_model,
        feeds=feeds,
    )

    print(f"Twin Model {twin_temperature_model_identity.did} created")

    ### 7.  CREATE DIGITAL TWINS FROM MODEL
    twin_from_model_id_list = []
    for temp_sensor in range(2):
        twin_temperature_identity = identity_api.create_twin_with_control_delegation(
            twin_key_name=f"TwinTemperature{temp_sensor}",
            twin_seed=AGENT_SEED,
            agent_identity=agent_identity,
        )

        properties_twin_from_model = [
            create_property(
                key=PROPERTY_KEY_FROM_MODEL,
                value=twin_temperature_model_identity.did,
                is_uri=True,
            ),
            create_property(
                key=PROPERTY_KEY_LABEL,
                value=f"Twin Temperature {temp_sensor+1} - LP",
                language="en",
            ),
            create_property(
                key=PROPERTY_KEY_COMMENT,
                value="This is a Twin Temperature",
                language="en",
            ),
            create_property(
                key=PROPERTY_KEY_TYPE,
                value=SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
                is_uri=True,
            ),
            create_property(
                key=SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY, value="T1234"
            ),
            create_property(key=PROPERTY_KEY_SPACE_NAME, value="Space A"),
            create_property(key=PROPERTY_KEY_COLOUR, value="#9aceff"),
            create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo"),
            # Add later
            # create_property(
            #     key=PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
            #     value="Replace with Host ID",
            # ),
            # create_property(
            #     key=PROPERTY_KEY_HOST_ALLOW_LIST,
            #     value="Replace with Host ID",
            # ),
        ]

        iotics_api.upsert_twin(
            twin_did=twin_temperature_identity.did,
            properties=properties_twin_from_model,
            feeds=feeds,
        )

        print(f"Twin {twin_temperature_identity.did} created")

        twin_from_model_id_list.append(twin_temperature_identity.did)

    ##### TWIN INTERACTION #####
    ### 8. SHARE TEMPERATURE DATA
    while True:
        try:
            for twin_id in twin_from_model_id_list:
                data_to_share = {feed_label: randint(1, 30)}
                iotics_api.share_feed_data(
                    twin_did=twin_id, feed_id=feed_id, data=data_to_share
                )
                print(f"Shared {data_to_share} from Twin ID {twin_id}")

            sleep(2)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
