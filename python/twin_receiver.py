from time import sleep

from helpers.constants import (
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_VALUE_ALLOW_ALL_HOSTS,
)
from helpers.identity_helper import IdentityHelper
from helpers.iotics_via_rest import IOTICSviaREST

RESOLVER_URL = ""  # IOTICSpace_URL/index.json
HOST = ""  # IOTICSpace URL
STOMP_ENDPOINT = ""  # HOST/index.json

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated
USER_DID = ""  # Copy-paste DID string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    print("Morning Session - Twin Receiver")


if __name__ == "__main__":
    main()
