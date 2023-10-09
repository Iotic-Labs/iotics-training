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
        self._token: str = None

    def get_host(self) -> str:
        return self._grpc_endpoint

    def get_token(self) -> str:
        return self._token

    def refresh_token(
        self, agent_identity: RegisteredIdentity, user_did: str, duration: int
    ):
        self._token: str = self._identity_api.create_agent_auth_token(
            agent_registered_identity=agent_identity,
            user_did=user_did,
            duration=duration,
        )

    def create_user_and_agent_with_auth_delegation(
        self,
        user_seed: bytes,
        user_key_name: str,
        agent_seed: bytes,
        agent_key_name: str,
    ) -> (RegisteredIdentity, RegisteredIdentity):
        (
            user_identity,
            agent_identity,
        ) = self._identity_api.create_user_and_agent_with_auth_delegation(
            user_seed=user_seed,
            user_key_name=user_key_name,
            agent_seed=agent_seed,
            agent_key_name=agent_key_name,
        )

        return user_identity, agent_identity

    def create_twin_with_control_delegation(
        self, twin_key_name: str, twin_seed: bytes, agent_identity: RegisteredIdentity
    ) -> RegisteredIdentity:
        twin_identity: RegisteredIdentity = (
            self._identity_api.create_twin_with_control_delegation(
                twin_seed=twin_seed,
                twin_key_name=twin_key_name,
                agent_registered_identity=agent_identity,
            )
        )

        return twin_identity
