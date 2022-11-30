import json
import threading

from helpers.constants import (
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_MODEL,
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


def get_feed_data(
    feed_listener,
    publisher_twin_did: str,
    feeds_value_label: str,
    event: threading.Event,
):
    for latest_feed_data in feed_listener:
        data = json.loads(latest_feed_data.payload.feedData.data)
        temperature = data[feeds_value_label]
        print(f"Received temperature {temperature} from Twin {publisher_twin_did}")
        if temperature < 20:
            event.set()
        else:
            event.clear()


def get_input_data(input_listener):
    for message in input_listener:
        data = json.loads(message.payload.message.data)
        input_msg_received = data["turn_on"]
        if input_msg_received:
            print("The radiator turns ON")
        else:
            print("The radiator turns OFF")


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
    thermostat_twin_identity = identity_helper.create_twin_with_control_delegation(
        twin_key_name="TwinFol",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )
    thermostat_twin_did = thermostat_twin_identity.did
    iotics_api.create_twin(twin_did=thermostat_twin_did)

    ### 4.  CREATE TWIN RECEIVER
    radiator_twin_identity = identity_helper.create_twin_with_control_delegation(
        twin_key_name="RadiatorTwin",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )
    radiator_twin_did = radiator_twin_identity.did
    radiator_input_id = "radiator_switch"

    iotics_api.upsert_twin(
        twin_did=radiator_twin_did,
        inputs=[
            create_input_with_meta(
                input_id=radiator_input_id,
                values=[
                    create_value(
                        label="turn_on",
                        comment="Whether the radiator is ON/OFF",
                        data_type="boolean",
                    )
                ],
            )
        ],
    )

    ### 5.  SEARCH FOR TWINS PUBLISHER
    """We need to find the 2 Twins Publisher. To do that we need to define:
    1. One or more search criteria
    2. The type of the response
    3. The scope of the Search."""
    twins_found_list = []
    payload = iotics_api.get_search_payload(
        properties=[create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo")],
        response_type="FULL",
    )
    for response in iotics_api.search_iter(
        client_app_id="follower_connector", payload=payload, scope="GLOBAL"
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    ### 6.  FOLLOW PUBLISHERS' FEED DATA
    """In order to follow a Twin's Feed we need to know:
    1. The Twin DID
    2. The Host ID of the Twin Pulbisher (if remote)
    3. The Feed ID.
    We don't want to Follow the Twin Model's Feed as it won't share any data.
    The 'fetch_interests' method will return a generator that waits until a new message is received.
    We can create a Thread for each Twin Publisher that takes as input the 'feed_listener' generator
    and set/unset a flag according to the message shared by the related Twin Publisher."""
    events_list = []
    for twin in twins_found_list:
        if (
            create_property(
                key=PROPERTY_KEY_TYPE, value=PROPERTY_VALUE_MODEL, is_uri=True
            )
            not in twin.properties
        ):
            # print("Host ID:", host_id)
            # print("DID:", twin.twinId.id)
            # print("Location:", twin.location)
            # print("Properties:", twin.properties)
            # print("Feed:", twin.feeds)
            # print("Inputs:", twin.inputs)
            # print("---")
            feed_of_interest = twin.feeds[0]
            host_id = feed_of_interest.feedId.hostId
            twin_id = feed_of_interest.feedId.twinId
            feed_id = feed_of_interest.feedId.id

            feed_description = iotics_api.describe_feed(
                twin_did=twin_id, feed_id=feed_id, remote_host_id=host_id
            )
            feeds_value_label = feed_description.payload.result.values[0].label

            feed_listener = iotics_api.fetch_interests(
                follower_twin_did=thermostat_twin_did,
                followed_twin_did=twin_id,
                followed_feed_id=feed_id,
                remote_host_id=host_id,
            )

            event = threading.Event()

            threading.Thread(
                target=get_feed_data,
                args=(
                    feed_listener,
                    twin_id,
                    feeds_value_label,
                    event,
                ),
            ).start()
            events_list.append(event)

    ### 6.  GET INPUT DATA
    input_listener = iotics_api.receive_input_messages(
        twin_id=radiator_twin_did, input_id=radiator_input_id
    )
    threading.Thread(target=get_input_data, args=(input_listener,)).start()

    ### 7.  THERMOSTAT LOGIC
    status_on = False
    while True:
        if status_on:
            iotics_api.send_input_message(
                sender_twin_id=thermostat_twin_did,
                receiver_twin_id=radiator_twin_did,
                input_id=radiator_input_id,
                message={"turn_on": False},
            )
            status_on = False

        while any(eve.is_set() for eve in events_list):
            if not status_on:
                iotics_api.send_input_message(
                    sender_twin_id=thermostat_twin_did,
                    receiver_twin_id=radiator_twin_did,
                    input_id=radiator_input_id,
                    message={"turn_on": True},
                )
                status_on = True

    ### 7.  BONUS
    twins_found_list = []
    event_bonus = threading.Event()
    payload = iotics_api.get_search_payload(
        properties=[create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo")],
        response_type="FULL",
    )
    for response in iotics_api.search_iter(
        client_app_id="follower_connector", payload=payload, scope="GLOBAL"
    ):
        twins = response.payload.twins
        twins_found_list.extend(twins)

    for twin in twins_found_list:
        feed_of_interest = twin.feeds[0]
        host_id = feed_of_interest.feedId.hostId
        twin_id = feed_of_interest.feedId.twinId
        feed_id = feed_of_interest.feedId.id

        feed_listener = iotics_api.fetch_interests(
            follower_twin_did=thermostat_twin_did,
            followed_twin_did=twin_id,
            followed_feed_id=feed_id,
            remote_host_id=host_id,
        )

        feed_description = iotics_api.describe_feed(
            twin_did=twin_id, feed_id=feed_id, remote_host_id=host_id
        )
        feeds_value_label = feed_description.payload.result.values[0].label

        threading.Thread(
            target=get_feed_data,
            args=(
                feed_listener,
                twin_id,
                feeds_value_label,
                event_bonus,
            ),
        ).start()

    status_on = False
    while True:
        if status_on and not event_bonus.is_set():
            iotics_api.send_input_message(
                sender_twin_id=thermostat_twin_did,
                receiver_twin_id=radiator_twin_did,
                input_id=radiator_input_id,
                message={"turn_on": False},
            )
            status_on = False

        while any(eve.is_set() for eve in events_list):
            if not status_on and event_bonus.is_set():
                iotics_api.send_input_message(
                    sender_twin_id=thermostat_twin_did,
                    receiver_twin_id=radiator_twin_did,
                    input_id=radiator_input_id,
                    message={"turn_on": True},
                )
                status_on = True

    ### 8.  DELETE TWIN
    """Let's delete the Twins to conclude the exercise"""
    iotics_api.delete_twin(twin_did=thermostat_twin_did)
    iotics_api.delete_twin(twin_did=radiator_twin_did)


if __name__ == "__main__":
    main()
