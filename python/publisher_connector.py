import base64
import json
from random import randint
from time import sleep

from helpers.constants import (
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
    SHARE_FEED_DATA,
    UNIT_DEGREE_CELSIUS,
    UPSERT_TWIN,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints, make_api_call
from iotics.lib.grpc.helpers import create_feed_with_meta, create_property, create_value
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    print("Morning Session - Publisher Connector")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
