from random import randint
from time import sleep

from helpers.constants import (
    MOTION_SENSOR_ONTOLOGY,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
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

    ### 5. CREATE TWIN SENDER IDENTITY WITH CONTROL DELEGATION
    twin_motion_sensor_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinMotionSensor", twin_seed=bytes.fromhex(AGENT_SEED)
    )

    ### 6. DEFINE TWIN'S STRUCTURE
    properties = [
        create_property(
            key=PROPERTY_KEY_LABEL, value="Twin Motion Sensor - LP", language="en"
        ),
        create_property(
            key=PROPERTY_KEY_COMMENT,
            value="This is a Twin Motion Sensor",
            language="en",
        ),
        create_property(
            key=PROPERTY_KEY_TYPE, value=MOTION_SENSOR_ONTOLOGY, is_uri=True
        ),
    ]

    ### 7. CREATE DIGITAL TWIN RADIATOR
    iotics_api.upsert_twin(
        twin_did=twin_motion_sensor_identity.did, properties=properties
    )

    print(f"Twin {twin_motion_sensor_identity.did} created succesfully")

    ##### TWIN INTERACTION #####
    ### 8. SEARCH FOR TWIN RADIATOR
    """We need to Search in the entire Network of Spaces (scope=GLOBAL)
    rather than locally (scope=LOCAL) in order to find Twins in a remote Host."""
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
        client_app_id="twin_sender", payload=payload, scope="GLOBAL"
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    # print(twins_found_list)

    """The search result will return an empty list of Twins found.
    In fact the Twin we want to search is not 'findable' from other Hosts
    unless its hostMetadataAllowList is set either to All Host or
    the Host ID from which we are searching for."""

    twin_radiator = twins_found_list[0]

    ### 9. SEND INPUT MESSAGES
    """Once the Twin Receiver has been found,
    we can take all the info needed to send the Input message."""
    while True:
        try:
            message = {"turn_on": bool(randint(0, 1))}

            iotics_api.send_input_message(
                sender_twin_id=twin_motion_sensor_identity.did,
                receiver_twin_id=twin_radiator.twinId.id,
                remote_host_id=twin_radiator.twinId.hostId,
                input_id=twin_radiator.inputs[0].inputId.id,
                message=message,
            )
            print(f"Sent Input message {message}")
            sleep(2)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
