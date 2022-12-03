from helpers.constants import PROPERTY_KEY_LABEL
from helpers.identity_helper import IdentityHelper
from iotics.lib.grpc.helpers import create_property
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

    ### 2. CREATE AGENT IDENTITY, THEN DELEGATE
    """The creation of the User is only used to retrieve the User Identity info.
    The User Identity in fact won't be (re-)created if the same creds will be used."""
    identity_helper.create_seed()  # Create a new Agent Seed
    agent_identity = identity_helper.create_agent_identity(
        agent_key_name=AGENT_KEY_NAME, agent_seed=AGENT_SEED, print_output=True
    )
    user_identity = identity_helper.create_user_identity(
        user_key_name=USER_KEY_NAME, user_seed=USER_SEED
    )
    identity_helper.authentication_delegation(
        user_identity=user_identity, agent_identity=agent_identity
    )

    ### 3. GENERATE NEW TOKEN
    """The default (according to the IdentityHelper class) duration of the Token
    should be enough for this exercise."""
    identity_helper.refresh_token(user_did=USER_DID, agent_identity=agent_identity)

    ### 4. INSTANTIATE IOTICSviagRPC AND SETUP
    iotics_api = IOTICSviagRPC(auth=identity_helper)

    ### 5. CREATE TWIN SENDER IDENTITY WITH CONTROL DELEGATION
    """Let's use the HighLevel Identity library to create the Twin Identity
    and delegate the Agent in a single step.
    Same as step 2, multiple creations of the Twin Identity won't (re-)create the Identity.
    Either take the 'did' field of the Twin Identity generated
    (i.e.: twin_sender_did = twin_sender_identity.did) or
    copy-paste the same field when printed on the terminal."""
    twin_sender_identity = identity_helper.create_twin_with_control_delegation(
        twin_key_name="TwinSend",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
        print_output=True,
    )
    twin_sender_did = twin_sender_identity.did

    ### 6. CREATE TWIN SENDER'S BASIC STRUCTURE, THEN DESCRIBE TWIN
    """For the sake of the training, the Twin Sender only needs the Basic Structure
    (no Properties/Feeds/Inputs) to send Input messages."""
    iotics_api.create_twin(twin_did=twin_sender_did)
    twin_description = iotics_api.describe_twin(twin_did=twin_sender_did)
    print(twin_description)

    ### 7. SEARCH FOR TWIN RECEIVER BY LABEL
    """We need to Search in the entire Network of Spaces (scope=GLOBAL)
    rather than locally (scope=LOCAL) in order to find Twins in a remote Host.
    The only search parameter we want to use for the sake of this exercise is the Twin's Label
    which must match exactly the Label of the Twin we want to find (and then take all the info we need)."""
    twins_found_list = []
    payload = iotics_api.get_search_payload(
        properties=[
            create_property(
                key=PROPERTY_KEY_LABEL, value="Twin Receiver - LP", language="en"
            )
        ],
        response_type="FULL",
    )
    for response in iotics_api.search_iter(
        client_app_id="twin_sender", payload=payload, scope="GLOBAL"
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    print(twins_found_list)

    """The search result will return an empty list of Twins found.
    In fact the Twin we want to search is not 'findable' from other Hosts
    unless its hostMetadataAllowList is set either to All Host or
    the Host ID from which we are searching for."""

    ### 8. SEND INPUT MESSAGES
    """Once the Twin Receiver has been found,
    we can take all the info needed to send the Input message."""
    iotics_api.send_input_message(
        sender_twin_id=twin_sender_did,
        receiver_twin_id="",
        remote_host_id="",
        input_id="",
        message={"light_on": True},
    )

    ### 9. DELETE TWIN SENDER
    """Let's delete the Twin to conclude the exercise"""
    iotics_api.delete_twin(twin_did=twin_sender_did)


if __name__ == "__main__":
    main()
