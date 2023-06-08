import json

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL,
    RADIATOR_ONTOLOGY,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import (
    create_input_with_meta,
    create_location,
    create_property,
    create_value,
)
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated

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
    """A User and an Agent Identity need to be created with Authentication Delegation so you can:
    1. Create Twin Identities;
    2. Generate a Token to use the IOTICS API.
    Be aware that, if Key Name and Seed don't change, multiple calls of the following function
    will not create new Identities, it will retrieve the existing ones."""
    identity_api.create_user_and_agent_with_auth_delegation(
        user_seed=bytes.fromhex(USER_SEED),
        user_key_name=USER_KEY_NAME,
        agent_seed=bytes.fromhex(AGENT_SEED),
        agent_key_name=AGENT_KEY_NAME,
    )

    ### 3. GENERATE NEW TOKEN
    """For the sake of this exercise we want to create a token
    that lasts for quite a good amount of time. If someone steals this token
    they will be able to perform any operation against any Twin
    created with your Agent (Control Delegation)."""
    identity_api.refresh_token(duration=600)

    ##### TWIN SETUP #####
    ### 4. INSTANTIATE IOTICSviagRPC
    iotics_api = IOTICSviagRPC(auth=identity_api)

    ### 5. CREATE TWIN RADIATOR IDENTITY WITH CONTROL DELEGATION
    """ We now need to create a new Twin Identity which will be used for our Twin Radiator.
    Only Agents can perform actions against a Twin.
    This means, after creating the Twin Identity it has to "control-delegate" an Agent Identity
    so the latter can control the Digital Twin."""
    twin_radiator_identity = identity_api.create_twin_with_control_delegation(
        # The Twin Key Name's concept is the same as Agent and User Key Name
        twin_key_name="TwinRadiator",
        # It is a best-practice to re-use the "AGENT_SEED" as a Twin seed.
        twin_seed=bytes.fromhex(AGENT_SEED),
    )

    ### 6. DEFINE TWIN'S STRUCTURE
    properties = [
        create_property(
            key=PROPERTY_KEY_LABEL, value="Twin Radiator - LP", language="en"
        ),
        create_property(
            key=PROPERTY_KEY_COMMENT, value="This is a Twin Radiator", language="en"
        ),
        create_property(key=PROPERTY_KEY_TYPE, value=RADIATOR_ONTOLOGY, is_uri=True),
        ### Add the following 2 Properties later ###
        create_property(
            key=PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
            value=PROPERTY_VALUE_ALLOW_ALL,
            is_uri=True,
        ),
        create_property(
            key=PROPERTY_KEY_HOST_ALLOW_LIST,
            value=PROPERTY_VALUE_ALLOW_ALL,
            is_uri=True,
        ),
    ]

    input_id = "radiator_switch"
    input_label = "turn_on"
    inputs = [
        create_input_with_meta(
            input_id=input_id,
            properties=[
                create_property(
                    key=PROPERTY_KEY_LABEL, value="ON/OFF switch", language="en"
                ),
            ],
            values=[
                create_value(
                    label=input_label,
                    comment="ON/OFF switch for the Radiator",
                    data_type="boolean",
                )
            ],
        )
    ]

    ### 7. CREATE DIGITAL TWIN RADIATOR
    """We can now use the Upsert Twin operation in order to:
    1. Create the Digital Twin;
    2. Add Twin's Metadata;
    3. Add a Input object (Input's Metadata + Input's Value) to this Twin."""
    iotics_api.upsert_twin(
        twin_did=twin_radiator_identity.did,
        location=create_location(lat=51.5, lon=-0.1),
        properties=properties,
        inputs=inputs,
    )

    print(f"Twin {twin_radiator_identity.did} created succesfully")

    ##### TWIN INTERACTION #####
    ### 8. WAIT FOR INPUT MESSAGES
    input_listener = iotics_api.receive_input_messages(
        twin_id=twin_radiator_identity.did, input_id=input_id
    )

    print("Waiting for Input messages...")

    try:
        for message in input_listener:
            input_msg_received = json.loads(message.payload.message.data)
            print(input_msg_received)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
