import json
import threading

from helpers.constants import (
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_TYPE,
    PROPERTY_VALUE_MODEL,
)
from helpers.identity_helper import IdentityHelper
from iotics.lib.grpc.helpers import (
    create_input_with_meta,
    create_property,
    create_value,
)
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

RESOLVER_URL = ""  # IOTICSpace_URL/index.json
HOST = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated
USER_DID = ""  # Copy-paste DID string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    print("Afternoon Session - Follower Connector")


if __name__ == "__main__":
    main()
