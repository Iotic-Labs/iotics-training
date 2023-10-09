from random import randint
from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    SHARE_FEED_DATA,
    UNIT_DEGREE_CELSIUS,
    UPSERT_TWIN,
    USER_KEY_NAME,
    USER_SEED,
    AGENT_SEED,
)
from helpers.utilities import get_host_endpoints, make_api_call, encode_data
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinPublisher"


def main():
    print("Morning Session - Twin Publisher")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
