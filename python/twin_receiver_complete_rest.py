from time import sleep

from helpers.constants import (
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_VALUE_ALLOW_ALL_HOSTS,
)
from helpers.identity_helper import IdentityHelper
from helpers.iotics_via_rest import IOTICSviaREST

RESOLVER_URL = ""  # IOTICSpace_URL/index.json
HOST = ""  # IOTICSpace URL
STOMP_ENDPOINT = ""  # HOST/index.json

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated
USER_DID = ""  # Copy-paste DID string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    ### 1. INSTANTIATE AN IDENTITY HELPER
    identity_helper = IdentityHelper(resolver_url=RESOLVER_URL, host_url=HOST)

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
        user_key_name=USER_KEY_NAME, user_seed=USER_SEED
    )
    agent_identity = identity_helper.create_agent_identity(
        agent_key_name=AGENT_KEY_NAME, agent_seed=AGENT_SEED
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

    ### 5. INSTANTIATE IOTICSviaREST AND SETUP
    """Here we need to setup the Stomp Client as
    the Twin Receiver will have to wait for incoming Input messages."""
    iotics = IOTICSviaREST(host_url=HOST, stomp_url=STOMP_ENDPOINT)
    iotics.setup(token=identity_helper.get_token())

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
    twin_description = iotics.describe_twin(twin_did=twin_rec_did)
    print(twin_description)

    ### 8. UPSERT TWIN RECEIVER WITH LABEL AND INPUT, THEN DESCRIBE TWIN
    """The only way to create a Twin with an Input via REST is through the Upsert operation.
    Let's start without AllowLists: the Twin won't be found from a remote Host.
    Then add hostMetadataAllowList: the Twin will be found but
    won't be able to interact with other Twins from a remote Host.
    Then add hostAllowList: the Twin will now correctly receive data."""
    iotics.upsert_twin(
        twin_did=twin_rec_did,
        properties=[
            {
                "key": PROPERTY_KEY_LABEL,
                "langLiteralValue": {"value": "Twin Receiver - LP", "lang": "en"},
            },
            {
                "key": PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
                "uriValue": {"value": PROPERTY_VALUE_ALLOW_ALL_HOSTS},
            },
            {
                "key": PROPERTY_KEY_HOST_ALLOW_LIST,
                "uriValue": {"value": PROPERTY_VALUE_ALLOW_ALL_HOSTS},
            },
            {
                "key": PROPERTY_KEY_HOST_ALLOW_LIST,
                "uriValue": {"value": ""},
            },
        ],
        inputs=[
            {
                "id": "on_off_switch",
                "values": [
                    {
                        "comment": "Turn ON/OFF light",
                        "dataType": "boolean",
                        "label": "light_on",
                    }
                ],
            }
        ],
    )
    twin_description = iotics.describe_twin(twin_did=twin_rec_did)
    print(twin_description)

    ### 9. WAIT FOR INPUT MESSAGES
    """Here is where STOMP comes into action.
    The 'receiver_callback' will simply print received messages on the terminal."""
    iotics.wait_for_input_messages(
        twin_receiver_did=twin_rec_did, input_id="on_off_switch"
    )
    while True:
        sleep(10)

    ### 10. DELETE TWIN RECEIVER
    """Let's delete the Twin to conclude the exercise"""
    iotics.delete_twin(twin_did=twin_rec_did)


if __name__ == "__main__":
    main()
