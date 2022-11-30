from time import sleep

from helpers.constants import (
    PROPERTY_KEY_COLOR,
    PROPERTY_KEY_COMMENT,
    PROPERTY_KEY_CREATED_BY,
    PROPERTY_KEY_HOST_ALLOW_LIST,
    PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
    PROPERTY_KEY_LABEL,
    PROPERTY_KEY_SPACE_NAME,
    PROPERTY_VALUE_ALLOW_ALL_HOSTS,
    UNIT_DEGREE_CELSIUS,
)
from helpers.identity_helper import IdentityHelper
from iotics.lib.grpc.helpers import create_feed_with_meta, create_property, create_value
from iotics.lib.grpc.iotics_api import IoticsApi as IOTICSviagRPC

RESOLVER_URL = ""  # IOTICSpace_URL/index.json
HOST = ""  # IOTICSpace URL

USER_KEY_NAME = ""
USER_SEED = ""  # Copy-paste SEED string generated
USER_DID = ""  # Copy-paste DID string generated

AGENT_KEY_NAME = ""
AGENT_SEED = ""  # Copy-paste SEED string generated


def main():
    ### 1.  SETUP IDENTITIES
    """In order to generate a new token, we just need the USER_DID and the Agent Identity."""
    identity_helper = IdentityHelper(
        resolver_url=RESOLVER_URL, host_url=HOST, grpc=True
    )
    agent_identity = identity_helper.create_agent_identity(
        agent_key_name=AGENT_KEY_NAME, agent_seed=AGENT_SEED
    )
    identity_helper.refresh_token(
        user_did=USER_DID, agent_identity=agent_identity, duration=600
    )

    ### 2.  SETUP IOTICSviagRPC
    iotics_api = IOTICSviagRPC(auth=identity_helper)

    ### 3.  CREATE TWIN PUBLISHER
    forecast_twin_identity = identity_helper.create_twin_with_control_delegation(
        twin_key_name="ForecastTwin",
        twin_seed=AGENT_SEED,
        agent_identity=agent_identity,
    )
    forecast_twin_did = forecast_twin_identity.did
    iotics_api.upsert_twin(
        twin_did=forecast_twin_did,
        properties=[
            create_property(
                key=PROPERTY_KEY_LABEL, value="Forecast Twin - LP", language="en"
            ),
            create_property(
                key=PROPERTY_KEY_COMMENT,
                value="Temperature Forecast Twin",
                language="en",
            ),
            create_property(key=PROPERTY_KEY_SPACE_NAME, value="Space A"),
            create_property(key=PROPERTY_KEY_COLOR, value="#9aceff"),
            create_property(key=PROPERTY_KEY_CREATED_BY, value="Lorenzo"),
            # Sensor Ontology
            # Some of the properties of this ontology can be used to add more description to the Sensor
            create_property(
                key="https://data.iotics.com/app#defines",
                value="https://saref.etsi.org/core/TemperatureSensor",
                is_uri=True,
            ),
            # Add "hasModel" property
            create_property(
                key="https://saref.etsi.org/core/hasModel", value="T_forecast"
            ),
            create_property(
                key=PROPERTY_KEY_HOST_METADATA_ALLOW_LIST,
                value=PROPERTY_VALUE_ALLOW_ALL_HOSTS,
                is_uri=True,
            ),
            create_property(
                key=PROPERTY_KEY_HOST_ALLOW_LIST,
                value=PROPERTY_VALUE_ALLOW_ALL_HOSTS,
                is_uri=True,
            ),
        ],
        feeds=[
            create_feed_with_meta(
                feed_id="forecast",
                properties=[
                    create_property(
                        key=PROPERTY_KEY_LABEL, value="Forecast", language="en"
                    ),
                    create_property(
                        key=PROPERTY_KEY_COMMENT,
                        value="Forecast temperature in 1h",
                        language="en",
                    ),
                ],
                values=[
                    create_value(
                        label="forecast",
                        comment="Temperature in degrees Celsius",
                        unit=UNIT_DEGREE_CELSIUS,
                        data_type="integer",
                    )
                ],
            )
        ],
    )

    ### 5.  SHARE DATA
    while True:
        for temp in range(18, 23):
            iotics_api.share_feed_data(
                twin_did=forecast_twin_did, feed_id="forecast", data={"forecast": temp}
            )
            print(f"Shared forecast {temp}")
            sleep(5)

        for temp in range(23, 18, -1):
            iotics_api.share_feed_data(
                twin_did=forecast_twin_did, feed_id="forecast", data={"forecast": temp}
            )
            print(f"Shared forecast {temp}")
            sleep(5)

    ### 6.  DELETE TWINS
    """Let's delete all the Twins to conclude the exercise"""
    iotics_api.delete_twin(twin_did=forecast_twin_did)


if __name__ == "__main__":
    main()
