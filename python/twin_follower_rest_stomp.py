import json
from time import sleep

from helpers.constants import (
    AGENT_SEED,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    SEARCH_TWINS,
    SUBSCRIBE_TO_FEED,
    UPSERT_TWIN,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.stomp_client import StompClient
from helpers.utilities import (
    decode_data,
    generate_headers,
    get_host_endpoints,
    make_api_call,
    search_twins,
)
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinFollower"


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
        user_seed=USER_SEED,
        user_key_name=USER_KEY_NAME,
        agent_seed=AGENT_SEED,
        agent_key_name=AGENT_KEY_NAME,
    )

    ### 3. GENERATE NEW TOKEN AND HEADERS
    token = identity_api.create_agent_auth_token(
        agent_registered_identity=agent_identity,
        user_did=user_identity.did,
        duration=600,
    )

    headers = generate_headers(token=token)

    ##### TWIN SETUP #####
    ### 4. CREATE TWIN FOLLOWER IDENTITY WITH CONTROL DELEGATION
    twin_follower_identity = identity_api.create_twin_with_control_delegation(
        twin_key_name="TwinFollower",
        twin_seed=AGENT_SEED,
        agent_registered_identity=agent_identity,
    )

    ### 5. DEFINE TWIN'S STRUCTURE
    properties = [
        {
            "key": PROPERTY_KEY_LABEL,
            "langLiteralValue": {"value": "Twin Follower - LP", "lang": "en"},
        },
        {
            "key": PROPERTY_KEY_COMMENT,
            "langLiteralValue": {"value": "This is a Twin Follower", "lang": "en"},
        },
    ]

    ### 6. CREATE DIGITAL TWIN FOLLOWER
    upsert_twin_payload = {
        "twinId": {"id": twin_follower_identity.did},
        "properties": properties,
    }
    make_api_call(
        method=UPSERT_TWIN.method,
        endpoint=UPSERT_TWIN.url.format(host=HOST_URL),
        headers=headers,
        payload=upsert_twin_payload,
    )

    print(f"Twin {twin_follower_identity.did} created")

    ##### TWIN INTERACTION #####
    ### 7. SEARCH FOR TWIN PUBLISHER
    payload = {
        "responseType": "FULL",
        "filter": {
            "text": "LP",
            "properties": [
                {
                    "key": PROPERTY_KEY_TYPE,
                    "uriValue": {"value": SAREF_TEMPERATURE_SENSOR_ONTOLOGY},
                }
            ],
        },
    }

    print("Searching for Twin Publisher...")

    twins_found_list = search_twins(
        method=SEARCH_TWINS.method,
        endpoint=SEARCH_TWINS.url.format(host=HOST_URL),
        headers=headers,
        payload=payload,
        scope="GLOBAL",
    )

    print(f"Found {len(twins_found_list)} Twins")

    twin_publisher = twins_found_list[0]

    @staticmethod
    def receiver_callback(headers, feed_data):
        encoded_data = json.loads(feed_data)

        try:
            data = encoded_data["feedData"]["data"]
            twin_publisher_id = encoded_data["interest"]["followedFeedId"]["twinId"]
        except KeyError:
            print("A KeyError occurred in the receiver_callback")
        else:
            decoded_feed_data = decode_data(data=data)
            print(f"Received {decoded_feed_data} from Twin {twin_publisher_id}")

    stomp_client = StompClient(
        stomp_endpoint=endpoints.get("stomp"), callback=receiver_callback, token=token
    )

    ### 8. SUBSCRIBE TO FEED DATA
    twin_publisher_host_id = twin_publisher["twinId"]["hostId"]
    twin_publisher_id = twin_publisher["twinId"]["id"]
    feed_id = twin_publisher["feeds"][0]["feedId"]["id"]

    stomp_client.subscribe(
        topic=SUBSCRIBE_TO_FEED.url.format(
            twin_follower_id=twin_follower_identity.did,
            twin_publisher_host_id=twin_publisher_host_id,
            twin_publisher_id=twin_publisher_id,
            feed_id=feed_id,
        ),
        subscription_id=f"{twin_publisher_id}-{feed_id}",
    )

    print("Waiting for Feed data...")

    while True:
        try:
            sleep(10)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
