import random
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COLOR,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_FROM_MODEL,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_SPACE_NAME,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL_HOSTS,
    PROPERTY_VALUE_MODEL,
    UNIT_DEGREE_CELSIUS,
)
from helpers.identity_helper import IdentityHelper
from iotics.lib.grpc.helpers import create_feed_with_meta, create_property, create_value
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

RESOLVER_URL = ""  # IOTICSpace_URL/index.json
HOST = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated
USER_DID = ""  # Copy-paste DID string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


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

    ### 3.  CREATE TWIN PUBLISHER MODEL
    """Let's use the HighLevel Identity library to create a new Twin Identity
    and perform the Control Delegation from Twin Identity to Agent Identity.
    For the sake of this exercise, the Twin Model doesn't need any change on the AllowLists' values.
    We want to use the Upsert operation as it combines multiple operations into a single one.
    The library we're using includes some helpful method to create Properties, Feeds and Values.
    Look at the UI (Models section)."""
    publisher_model_twin_identity = identity_helper.create_twin_with_control_delegation(
        twin_key_name="SensorTwinModel",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )
    publisher_model_twin_did = publisher_model_twin_identity.did
    iotics_api.upsert_twin(
        twin_did=publisher_model_twin_did,
        properties=[
            create_property(
                key=PROPERTY_KEY_TYPE, value=PROPERTY_VALUE_MODEL, is_uri=True
            ),
            create_property(
                key=PROPERTY_KEY_LABEL,
                value="Temperature Sensor Model - LP",
                language="en",
            ),
            create_property(
                key=PROPERTY_KEY_COMMENT,
                value="Model of a Temperature Sensor Twin",
                language="en",
            ),
            create_property(key=PROPERTY_KEY_SPACE_NAME, value="Space A"),
            create_property(key=PROPERTY_KEY_COLOR, value="#9aceff"),
            create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo"),
            # Sensor Ontology
            # Some of the properties of this ontology can be used to add more description to the Sensor
            create_property(
                key="https://data.iotics.com/app#defines",
                value="https://saref.etsi.org/core/TemperatureSensor",
                is_uri=True,
            ),
            # Add "hasModel" property
            create_property(
                key="https://saref.etsi.org/core/hasModel", value="SET-LATER"
            ),
        ],
        feeds=[
            create_feed_with_meta(
                feed_id="temperature",
                properties=[
                    create_property(
                        key=PROPERTY_KEY_LABEL, value="Temperature", language="en"
                    ),
                    create_property(
                        key=PROPERTY_KEY_COMMENT,
                        value="Current Temperature of a room",
                        language="en",
                    ),
                ],
                values=[
                    create_value(
                        label="reading",
                        comment="Temperature in degrees Celsius",
                        unit=UNIT_DEGREE_CELSIUS,
                        data_type="integer",
                    )
                ],
            )
        ],
    )

    print(f"Created Twin Model {publisher_model_twin_did}")

    ### 4.  CREATE 2 TWINs PUBLISHER FROM MODEL
    """Let's create a mapping between Sensor ID and Twin DID (eventually we'll need the latter info to share data).
    Let's copy-paste the entire Twin Model upsert info with the right changes:
    - twin_did
    - 1st Twin Property
    - Label
    - Comment
    - hostMetadataAllowList
    - hostAllowList.
    The Twins' setup phase ends here."""
    room_number_to_twin_did = {}
    for room_number in range(2):
        publisher_twin_identity = identity_helper.create_twin_with_control_delegation(
            twin_key_name=f"SensorTwin{room_number}",
            twin_seed=AGENT_SEED,
            agent_identity=agent_identity,
        )
        publisher_twin_did = publisher_twin_identity.did

        iotics_api.upsert_twin(
            twin_did=publisher_twin_did,
            properties=[
                create_property(
                    key=PROPERTY_KEY_FROM_MODEL,
                    value=publisher_model_twin_did,
                    is_uri=True,
                ),
                create_property(
                    key=PROPERTY_KEY_LABEL,
                    value=f"Temperature Sensor Twin {room_number+1}",
                    language="en",
                ),
                create_property(
                    key=PROPERTY_KEY_COMMENT,
                    value=f"Temperature Sensor Twin of Room {room_number+1}",
                    language="en",
                ),
                create_property(key=PROPERTY_KEY_SPACE_NAME, value="Space A"),
                create_property(key=PROPERTY_KEY_COLOR, value="#9aceff"),
                create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo"),
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
                # TemperatureSensor Ontology
                # Some of the properties of this ontology can be used to add more description to the Sensor
                create_property(
                    key="https://data.iotics.com/app#defines",
                    value="https://saref.etsi.org/core/TemperatureSensor",
                    is_uri=True,
                ),
                # Add "hasModel" property
                create_property(
                    key="https://saref.etsi.org/core/hasModel", value="T1234"
                ),
            ],
            feeds=[
                create_feed_with_meta(
                    feed_id="temperature",
                    properties=[
                        create_property(
                            key=PROPERTY_KEY_LABEL,
                            value="Temperature",
                            language="en",
                        ),
                        create_property(
                            key=PROPERTY_KEY_COMMENT,
                            value="Current Temperature of a room",
                            language="en",
                        ),
                    ],
                    values=[
                        create_value(
                            label="reading",
                            comment="Temperature in degrees Celsius",
                            unit=UNIT_DEGREE_CELSIUS,
                            data_type="integer",
                        )
                    ],
                )
            ],
        )

        print(f"Created Twin {publisher_twin_did}")

        room_number_to_twin_did.update({room_number: publisher_twin_did})

    ### 5.  SHARE DATA
    """For the Twins' interaction phase, let's create a loop in which, every 5s we:
    1. generate a random number (temperature) for each Sensor,
    2. share the data from the specific Twin."""
    while True:
        rand_temp_list = random.sample(range(0, 40), len(room_number_to_twin_did))
        for room_number, rand_temp in enumerate(rand_temp_list):
            iotics_api.share_feed_data(
                twin_did=room_number_to_twin_did[room_number],
                feed_id="temperature",
                data={"reading": rand_temp},
            )
            print(
                f"Shared temperature {rand_temp} from Twin {room_number_to_twin_did[room_number]}"
            )

        print("---")
        sleep(5)

    ### 6.  DELETE TWINS
    """Let's delete all the Twins to conclude the exercise"""
    iotics_api.delete_twin(twin_did=publisher_model_twin_did)
    for twin_did in room_number_to_twin_did.values():
        iotics_api.delete_twin(twin_did=twin_did)


if __name__ == "__main__":
    main()
