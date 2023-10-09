from random import randint
from time import sleep

from helpers.constants import (
    AGENT_SEED,
    PROPERTY_KEY_COLOUR,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_DEFINES,
    PROPERTY_KEY_FROM_MODEL,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_SPACE_NAME,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_MODEL,
    SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    UNIT_DEGREE_CELSIUS,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_feed_with_meta, create_property, create_value
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "PublisherConnector"


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

    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
