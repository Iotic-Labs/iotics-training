import json
import threading

from helpers.constants import (
    AGENT_SEED,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
    SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_property
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "SynthesiserConnector"


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
