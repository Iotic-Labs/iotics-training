import base64
import json
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL,
    RADIATOR_ONTOLOGY,
    SUBSCRIBE_TO_INPUT,
    UPSERT_TWIN,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.stomp_client import StompClient
from helpers.utilities import get_host_endpoints, make_api_call
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    print("Morning Session - Twin Receiver")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
