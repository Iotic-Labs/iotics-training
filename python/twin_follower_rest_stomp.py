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
    print("Morning Session - Twin Follower")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
