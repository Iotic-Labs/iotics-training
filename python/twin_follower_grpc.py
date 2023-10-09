import json

from helpers.constants import (
    AGENT_SEED,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    SAREF_TEMPERATURE_SENSOR_ONTOLOGY,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_property
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinFollower"


def main():
    print("Morning Session - Twin Follower")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
