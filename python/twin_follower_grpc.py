import json

from helpers.constants import (
    AGENT_SEED,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_property
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinFollower"


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

    ### 5. CREATE TWIN FOLLOWER IDENTITY WITH CONTROL DELEGATION
    twin_follower_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinFollower",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )

    ### 6. DEFINE TWIN'S STRUCTURE
    properties = [
        create_property(
            key=PROPERTY_KEY_LABEL, value="Twin Follower - LP", language="en"
        ),
        create_property(
            key=PROPERTY_KEY_COMMENT, value="This is a Twin Follower", language="en"
        ),
    ]

    ### 7. CREATE DIGITAL TWIN FOLLOWER
    iotics_api.upsert_twin(twin_did=twin_follower_identity.did, properties=properties)
    print(f"Twin {twin_follower_identity.did} created")

    ##### TWIN INTERACTION #####
    ### 8. SEARCH FOR TWIN PUBLISHER
    twins_found_list = []
    payload = iotics_api.get_search_payload(
        text="LP",
        properties=[
            create_property(
                key=PROPERTY_KEY_TYPE,
                value=SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
                is_uri=True,
            )
        ],
        response_type="FULL",
    )

    print("Searching for Twin Publisher...")

    for response in iotics_api.search_iter(
        client_app_id="twin_follower", payload=payload, scope="GLOBAL"
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    print(f"Found {len(twins_found_list)} Twins")

    twin_publisher = twins_found_list[0]

    feed_listener = iotics_api.fetch_interests(
        follower_twin_did=twin_follower_identity.did,
        followed_twin_did=twin_publisher.twinId.id,
        remote_host_id=twin_publisher.twinId.hostId,
        followed_feed_id=twin_publisher.feeds[0].feedId.id,
    )

    try:
        for latest_feed_data in feed_listener:
            data = json.loads(latest_feed_data.payload.feedData.data)
            temperature = data["sensor_reading"]
            print(f"Received {temperature} from Twin {twin_publisher.twinId.id}")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
