import json
import threading

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
    SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_property
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    ##### IDENTITY MANAGEMENT #####
    ### 1. INSTANTIATE AN IDENTITY API OBJECT
    endpoints = get_host_endpoints(host_url=HOST_URL)
    identity_api = Identity(
        resolver_url=endpoints.get("resolver"), grpc_endpoint=endpoints.get("grpc")
    )

    ### 2. CREATE AGENT AND USER IDENTITY, THEN DELEGATE
    identity_api.create_user_and_agent_with_auth_delegation(
        user_seed=bytes.fromhex(USER_SEED),
        user_key_name=USER_KEY_NAME,
        agent_seed=bytes.fromhex(AGENT_SEED),
        agent_key_name=AGENT_KEY_NAME,
    )

    ### 3. GENERATE NEW TOKEN
    identity_api.refresh_token(duration=600)

    ##### TWIN SETUP #####
    ### 4. INSTANTIATE IOTICSviagRPC
    iotics_api = IOTICSviagRPC(auth=identity_api)

    ### 4. CREATE TWIN SYNTHESISER IDENTITY WITH CONTROL DELEGATION
    twin_thermostat_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinThermostat", twin_seed=bytes.fromhex(AGENT_SEED)
    )

    ### 5. DEFINE TWIN'S STRUCTURE
    properties = [
        create_property(
            key=PROPERTY_KEY_LABEL, value="Twin Thermostat - LP", language="en"
        ),
        create_property(
            key=PROPERTY_KEY_COMMENT, value="This is a Twin Thermostat", language="en"
        ),
    ]

    ### 6. CREATE DIGITAL TWIN TERMOSTAT
    iotics_api.upsert_twin(twin_did=twin_thermostat_identity.did, properties=properties)
    print(f"Twin {twin_thermostat_identity.did} created succesfully")

    ##### TWIN INTERACTION #####
    ### 7. SEARCH FOR TWIN RADIATOR
    twins_found_list = []
    payload = iotics_api.get_search_payload(
        text="LP",
        properties=[
            create_property(key=PROPERTY_KEY_TYPE, value=RADIATOR_ONTOLOGY, is_uri=True)
        ],
        response_type="FULL",
    )

    print("Searching for Twin Radiator...")

    for response in iotics_api.search_iter(
        client_app_id="twin_radiator", payload=payload
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    print(f"Found {len(twins_found_list)} Twins")

    twin_radiator = twins_found_list[0]

    ### 8. SEARCH FOR TWIN TEMPERATURE SENSOR
    twins_found_list = []
    payload = iotics_api.get_search_payload(
        text="LP",
        properties=[
            create_property(
                key=SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY, value="T1234"
            )
        ],
        response_type="FULL",
    )

    print("Searching for Temperature Sensor Twins...")

    for response in iotics_api.search_iter(
        client_app_id="twin_temperature_sensor", payload=payload, scope="GLOBAL"
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    print(f"Found {len(twins_found_list)} Twins")

    twin_temperature = twins_found_list[0]

    def get_feed_data(feed_listener, event: threading.Event):
        for latest_feed_data in feed_listener:
            data = json.loads(latest_feed_data.payload.feedData.data)
            temperature = data["sensor_reading"]

            if temperature <= 15:
                event.set()
            else:
                event.clear()

    ### 9. SUBSCRIBE TO FEED DATA
    events_list = []
    for twin_temperature in twins_found_list:
        feed_listener = iotics_api.fetch_interests(
            follower_twin_did=twin_thermostat_identity.did,
            followed_twin_did=twin_temperature.twinId.id,
            remote_host_id=twin_temperature.twinId.hostId,
            followed_feed_id=twin_temperature.feeds[0].feedId.id,
        )

        event = threading.Event()

        threading.Thread(
            target=get_feed_data,
            args=(
                feed_listener,
                event,
            ),
            daemon=True,
        ).start()

        events_list.append(event)

    ### 9. SEND INPUT MESSAGES
    previous_message_sent = {"turn_on": True}
    while True:
        try:
            if all(eve.is_set() for eve in events_list):
                message = {"turn_on": True}
            else:
                message = {"turn_on": False}

            if message != previous_message_sent:
                iotics_api.send_input_message(
                    sender_twin_id=twin_thermostat_identity.did,
                    receiver_twin_id=twin_radiator.twinId.id,
                    input_id=twin_radiator.inputs[0].inputId.id,
                    message=message,
                )
                print(f"Sent Input message {message}")
                previous_message_sent = message
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
