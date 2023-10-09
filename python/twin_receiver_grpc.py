import json

from helpers.constants import (
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_ALLOW_ALL,
    RADIATOR_ONTOLOGY,
    USER_KEY_NAME,
    USER_SEED,
    AGENT_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import (
    create_input_with_meta,
    create_location,
    create_property,
    create_value,
)
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinReceiver"


def main():
    print("Morning Session - Twin Receiver")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
