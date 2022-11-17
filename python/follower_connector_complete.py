import json
import threading

from helpers.constants import (
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_MODEL,
)
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


def get_feed_data(feed_listener, twin_did: str):
    for latest_feed_data in feed_listener:
        data = json.loads(latest_feed_data.payload.feedData.data)
        temperature = data["reading"]
        print(f"Received temperature {temperature} from Twin {twin_did}")


def main():
    ### 1.  SETUP IDENTITIES
    """In order to generate a new token, we just need the USER_DID and the Agent Identity."""
    identity_helper = IdentityHelper(
        resolver_url=RESOLVER_URL, host_url=HOST, grpc=True
    )
    agent_identity = identity_helper.create_agent_identity(
        agent_key_name=AGENT_KEY_NAME, agent_seed=AGENT_SEED
    )
    identity_helper.refresh_token(
        user_did=USER_DID, agent_identity=agent_identity, duration=600
    )

    ### 2.  SETUP IOTICSviagRPC
    iotics_api = IOTICSviagRPC(auth=identity_helper)

    ### 3.  CREATE TWIN FOLLOWER
    """There's no need to create a Twin Model for this exercise.
    If there was a need to create more than just a Twin Follower,
    then probably a Twin Model would be beneficial.
    We don't care abut changing the AllowLists either
    (no one needs to find, describe or send data to this Twin)."""
    follower_twin_identity = identity_helper.create_twin_with_control_delegation(
        twin_key_name="TwinFol",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )
    follower_twin_did = follower_twin_identity.did
    iotics_api.create_twin(twin_did=follower_twin_did)

    ### 4.  SEARCH FOR TWINS PUBLISHER
    """We need to find the 3 Twins Publisher. To do that we need to define:
    1. One or more search criteria
    2. The type of the response
    3. The scope of the Search."""
    twins_publisher_dict = {}
    payload = iotics_api.get_search_payload(
        properties=[create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo")],
        response_type="FULL",
    )
    for response in iotics_api.search_iter(
        client_app_id="follower_connector", payload=payload, scope="GLOBAL"
    ):
        hostId = response.payload.hostId
        twins = response.payload.twins
        twins_publisher_dict.update({hostId: twins})

    ### 5.  FOLLOW PUBLISHERS' FEED DATA
    """In order to follow a Twin's Feed we need to know:
    1. The Twin DID
    2. The Host ID of the Twin Pulbisher (if remote)
    3. The Feed ID.
    We don't want to Follow the Twin Model's Feed as it won't share any data.
    The 'fetch_interests' method will return a generator that waits until a new message is received.
    We can create a Thread for each Twin Publisher that takes as input the 'feed_listener' generator
    and prints on screen any new message shared by the related Twin Publisher."""
    for host_id, twins in twins_publisher_dict.items():
        # print("Host ID:", host_id)
        for twin in twins:
            publisher_twin_did = twin.twinId.id
            # print("Twin DID:", publisher_twin_did)
            # print("Location:", twin.location)
            # print("Properties:", twin.properties)
            # print("Feed:", twin.feeds)
            # print("Inputs:", twin.inputs)
            # print("---")
            if (
                create_property(
                    key=PROPERTY_KEY_TYPE, value=PROPERTY_VALUE_MODEL, is_uri=True
                )
                not in twin.properties
            ):
                feed_listener = iotics_api.fetch_interests(
                    follower_twin_did=follower_twin_did,
                    followed_twin_did=publisher_twin_did,
                    followed_feed_id="temperature",
                    remote_host_id=host_id,
                )
                threading.Thread(
                    target=get_feed_data, args=(feed_listener, publisher_twin_did)
                ).start()

    ### 6.  DELETE TWIN
    """Let's delete the Twin to conclude the exercise"""
    iotics_api.delete_twin(twin_did=follower_twin_did)


if __name__ == "__main__":
    main()
