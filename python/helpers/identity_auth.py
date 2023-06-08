import logging
from datetime import datetime, timedelta
from typing import Optional

from iotics.lib.grpc.auth import AuthInterface
from iotics.lib.identity.api.high_level_api import (
    HighLevelIdentityApi,
    RegisteredIdentity,
    get_rest_high_level_identity_api,
)


class Identity(AuthInterface):
    def __init__(self, resolver_url: str, grpc_endpoint: str):
        self._identity_api: HighLevelIdentityApi = get_rest_high_level_identity_api(
            resolver_url=resolver_url
        )
        self._grpc_endpoint: str = grpc_endpoint
        self._user_identity: RegisteredIdentity = None
        self._agent_identity: RegisteredIdentity = None
        self._token: str = None

    def get_host(self) -> str:
        return self._grpc_endpoint

    def get_token(self) -> str:
        return self._token

    def refresh_token(self, duration: int = 60):
        self._token: str = self._identity_api.create_agent_auth_token(
            agent_registered_identity=self._agent_identity,
            user_did=self._user_identity.did,
            duration=duration,
        )

        logging.debug(
            "New token generated. Expires at %s",
            datetime.now() + timedelta(seconds=duration),
        )

    def create_user_and_agent_with_auth_delegation(
        self,
        user_seed: bytes,
        user_key_name: str,
        agent_seed: bytes,
        agent_key_name: str,
    ):
        (
            self._user_identity,
            self._agent_identity,
        ) = self._identity_api.create_user_and_agent_with_auth_delegation(
            user_seed=user_seed,
            user_key_name=user_key_name,
            agent_seed=agent_seed,
            agent_key_name=agent_key_name,
        )

    def create_twin_with_control_delegation(
        self, twin_key_name: str, twin_seed: bytes
    ) -> RegisteredIdentity:
        twin_identity: RegisteredIdentity = (
            self._identity_api.create_twin_with_control_delegation(
                twin_seed=twin_seed,
                twin_key_name=twin_key_name,
                agent_registered_identity=self._agent_identity,
            )
        )

        logging.debug(
            "Twin Identity %s created with Control delegation", twin_identity.did
        )

        return twin_identity
