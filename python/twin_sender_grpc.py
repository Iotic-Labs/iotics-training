from random import randint
from time import sleep

from helpers.constants import (
    MOTION_SENSOR_ONTOLOGY,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_TYPE,
    RADIATOR_ONTOLOGY,
    USER_KEY_NAME,
    USER_SEED,
)
from helpers.identity_auth import Identity
from helpers.utilities import get_host_endpoints
from iotics.lib.grpc.helpers import create_property
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

from python.synthesiser_connector_rest_stomp import AGENT_SEED

HOST_URL = ""  # IOTICSpace URL
AGENT_KEY_NAME = "TwinSender"


def main():
    print("Morning Session - Twin Sender")
    ##### IDENTITY MANAGEMENT #####
    ##### TWIN SETUP #####
    ##### TWIN INTERACTION #####


if __name__ == "__main__":
    main()
