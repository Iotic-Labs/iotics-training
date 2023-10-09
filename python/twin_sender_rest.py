from random import randint
from time import sleep

from helpers.constants import (
    AGENT_SEED,
    MOTION_SENSOR_ONTOLOGY,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
    SEARCH_TWINS,
    SEND_INPUT_MESSAGE,
    UPSERT_TWIN,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.utilities import (
    encode_data,
    generate_headers,
    get_host_endpoints,
    make_api_call,
    search_twins,
)
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinSender"


def main():
    print("Morning Session - Twin Sender")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
