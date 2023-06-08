import base64
import json
import threading
from datetime import datetime, timedelta, timezone

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
    SAREF_TEMPERATURE_SENSOR_HAS_MODEL_ONTOLOGY,
    SEARCH_TWINS,
    SEND_INPUT_MESSAGE,
    SUBSCRIBE_TO_FEED,
    UPSERT_TWIN,
)
from helpers.identity_auth import Identity
from helpers.stomp_client import StompClient
from helpers.utilities import get_host_endpoints, make_api_call, search_twins
from iotics.lib.grpc.helpers import create_property
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api

HOST_URL = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    print("Morning Session - Synthesiser Connector")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
