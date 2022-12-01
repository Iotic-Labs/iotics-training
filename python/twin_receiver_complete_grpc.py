import json

from helpers.constants import (
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_VALUE_ALLOW_ALL_HOSTS,
)
from helpers.identity_helper import IdentityHelper
from iotics.lib.grpc.helpers import (
    create_input_with_meta,
    create_property,
    create_value,
)
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

RESOLVER_URL = ""  # IOTICSpace_URL/index.json
HOST = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated
USER_DID = ""  # Copy-paste DID string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    ### 1. INSTANTIATE AN IDENTITY HELPER
    identity_helper = IdentityHelper(
        resolver_url=RESOLVER_URL, host_url=HOST, grpc=True
    )

    ### 2. GENERATE USER AND AGENT SEED
    identity_helper.create_seed()  # Create a seed for the User
    identity_helper.create_seed()  # Create a seed for the Agent

    ### 3. CREATE USER AND AGENT IDENTITY, THEN DELEGATE
    """Here we are using the Regular Identity library where we
    create the User Identity, Agent Identity and Authentication Delegation
    in 3 different operations.
    These info will have to be stored safely !!
    Otherwise all the Twins created with these 2 Identities
    cannot be updated/deleted with different Identities"""
    user_identity = identity_helper.create_user_identity(
        user_key_name=USER_KEY_NAME, user_seed=USER_SEED, print_output=True
    )
    agent_identity = identity_helper.create_agent_identity(
        agent_key_name=AGENT_KEY_NAME, agent_seed=AGENT_SEED, print_output=True
    )
    identity_helper.authentication_delegation(
        user_identity=user_identity, agent_identity=agent_identity
    )

    ### 4. GENERATE NEW TOKEN
    """For the sake of this exercise we want to create a token
    that lasts for quite a good amount of time. If someone steals this token
    they will be able to perform any operation against any Twin
    created with your Agent (Control Delegation)."""
    identity_helper.refresh_token(
        user_did=USER_DID, agent_identity=agent_identity, duration=600
    )

    ### 5. INSTANTIATE IOTICSviagRPC AND SETUP
    iotics_api = IOTICSviagRPC(auth=identity_helper)

    ### 6. CREATE TWIN RECEIVER IDENTITY, THEN DELEGATE
    """We are going to reuse the AGENT_SEED to create any new Twin Identity.
    Same as step 3, multiple creations of the Twin Identity won't (re-)create the Identity.
    Either take the 'did' field of the Twin Identity generated
    (i.e.: twin_identity_rec = twin_identity_rec.did) or
    copy-paste the same field when printed on the terminal."""
    twin_identity_rec = identity_helper.create_twin_identity(
        twin_key_name="TwinRec", twin_seed=AGENT_SEED, print_output=True
    )
    identity_helper.control_delegation(
        twin_identity=twin_identity_rec, agent_identity=agent_identity
    )
    twin_rec_did = twin_identity_rec.did

    ### 7. DESCRIBE TWIN RECEIVER
    """The description of a Twin without basic Structure won't work.
    In fact there's nothing to be described (Twin Identity != Digital Twin)"""
    twin_description = iotics_api.describe_twin(twin_did=twin_rec_did)
    print(twin_description)

    ### 8. UPSERT TWIN RECEIVER WITH LABEL AND INPUT, THEN DESCRIBE TWIN
    """The only way to create a Twin with an Input is through the Upsert operation.
    Let's start without AllowLists: the Twin won't be found from a remote Host.
    Then add hostMetadataAllowList: the Twin will be found but
    won't be able to interact with other Twins from a remote Host.
    Then add hostAllowList: the Twin will now correctly receive data."""
    iotics_api.upsert_twin(
        twin_did=twin_rec_did,
        properties=[
            create_property(
                key=PROPERTY_KEY_LABEL, value="Twin Receiver - LP", language="en"
            ),
            create_property(
                key=PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
                value=PROPERTY_VALUE_ALLOW_ALL_HOSTS,
                is_uri=True,
            ),
            create_property(
                key=PROPERTY_KEY_HOST_ALLOW_LIST,
                value=PROPERTY_VALUE_ALLOW_ALL_HOSTS,
                is_uri=True,
            ),
            # Specific Host ID
            create_property(key=PROPERTY_KEY_HOST_ALLOW_LIST, value="", is_uri=True),
        ],
        inputs=[
            create_input_with_meta(
                input_id="on_off_switch",
                values=[
                    create_value(
                        label="light_on",
                        comment="Turn ON/OFF light",
                        data_type="boolean",
                    )
                ],
            )
        ],
    )
    twin_description = iotics_api.describe_twin(twin_did=twin_rec_did)
    print(twin_description)

    ### 9. WAIT FOR INPUT MESSAGES
    input_listener = iotics_api.receive_input_messages(
        twin_id=twin_rec_did, input_id="on_off_switch"
    )

    print("Waiting for Input messages...")
    for message in input_listener:
        data = json.loads(message.payload.message.data)
        input_msg_received = data["light_on"]
        if input_msg_received:
            print("The light bulb turns ON")
        else:
            print("The light bulb turns OFF")

    ### 10. DELETE TWIN RECEIVER
    """Let's delete the Twin to conclude the exercise"""
    iotics_api.delete_twin(twin_did=twin_rec_did)


if __name__ == "__main__":
    main()
