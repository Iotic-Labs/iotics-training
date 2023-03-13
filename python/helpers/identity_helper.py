from datetime import datetime, timedelta

from iotics.lib.grpc.auth import AuthInterface
from iotics.lib.identity.api.high_level_api import get_rest_high_level_identity_api
from iotics.lib.identity.api.regular_api import (
    RegisteredIdentity,
    get_rest_identity_api,
)


class IdentityHelper(AuthInterface):
    def __init__(self, resolver_url: str, host_url: str):
        self._high_level_identity_api = get_rest_high_level_identity_api(
            resolver_url=resolver_url
        )
        self._identity_api = get_rest_identity_api(resolver_url=resolver_url)
        self._host_url = host_url
        self._token = None

    def get_host(self) -> str:
        return self._host_url

    def get_token(self) -> str:
        return self._token

    def refresh_token(
        self, user_did: str, agent_identity: RegisteredIdentity, duration: int = 60
    ):
        self._token = self._identity_api.create_agent_auth_token(
            agent_registered_identity=agent_identity,
            user_did=user_did,
            duration=duration,
        )

        print(
            f"New token generated. Expires at {datetime.now() + timedelta(seconds=duration)}"
        )

    def create_seed(self):
        seed = self._identity_api.create_seed()

        seed_hex = seed.hex()
        print(f"Seed = {seed_hex}")

    def create_user_identity(
        self, user_key_name: str, user_seed: str, print_output: bool = False
    ) -> RegisteredIdentity:
        user_identity = self._identity_api.create_user_identity(
            user_seed=bytes.fromhex(user_seed),
            user_key_name=user_key_name,
            user_name="#user-0",  # Use default value
        )

        if print_output:
            print(f"User DID = {user_identity.did}")

        return user_identity

    def create_agent_identity(
        self, agent_key_name: str, agent_seed: str, print_output: bool = False
    ) -> RegisteredIdentity:
        agent_identity = self._identity_api.create_agent_identity(
            agent_seed=bytes.fromhex(agent_seed),
            agent_key_name=agent_key_name,
            agent_name="#agent-0",  # Use default value
        )

        if print_output:
            print(f"Agent DID = {agent_identity.did}")

        return agent_identity

    def create_twin_identity(
        self, twin_key_name: str, twin_seed: str, print_output: bool = False
    ) -> RegisteredIdentity:
        twin_identity = self._identity_api.create_twin_identity(
            twin_seed=bytes.fromhex(twin_seed),
            twin_key_name=twin_key_name,
            twin_name="#twin-0",  # Use default value
        )

        if print_output:
            print(f"Twin DID = {twin_identity.did}")

        return twin_identity

    def authentication_delegation(
        self, user_identity: RegisteredIdentity, agent_identity: RegisteredIdentity
    ):
        self._identity_api.user_delegates_authentication_to_agent(
            user_registered_identity=user_identity,
            agent_registered_identity=agent_identity,
        )

        print("Authentication delegation succeeded")

    def control_delegation(
        self, twin_identity: RegisteredIdentity, agent_identity: RegisteredIdentity
    ):
        self._identity_api.twin_delegates_control_to_agent(
            twin_registered_identity=twin_identity,
            agent_registered_identity=agent_identity,
        )

        print("Control delegation suceeded")

    def get_user_identity(
        self, user_key_seed: str, user_key_name: str, user_did: str, user_name: str
    ) -> RegisteredIdentity:
        user_identity = self._identity_api.get_user_identity(
            key_seed=bytes.fromhex(user_key_seed),
            key_name=user_key_name,
            user_did=user_did,
            user_name=user_name,
        )

        return user_identity

    def get_agent_identity(
        self, agent_key_seed: str, agent_key_name: str, agent_did: str, agent_name: str
    ) -> RegisteredIdentity:
        agent_identity = self._identity_api.get_agent_identity(
            key_seed=bytes.fromhex(agent_key_seed),
            key_name=agent_key_name,
            agent_did=agent_did,
            agent_name=agent_name,
        )

        return agent_identity

    def create_user_and_agent_with_auth_delegation(
        self,
        user_key_name: str,
        user_seed: str,
        agent_key_name: str,
        agent_seed: str,
        print_output: bool = False,
    ) -> tuple[RegisteredIdentity, RegisteredIdentity]:
        (
            user_identity,
            agent_identity,
        ) = self._high_level_identity_api.create_user_and_agent_with_auth_delegation(
            user_seed=bytes.fromhex(user_seed),
            user_key_name=user_key_name,
            agent_seed=bytes.fromhex(agent_seed),
            agent_key_name=agent_key_name,
        )

        if print_output:
            print("User and Agent Identity created with Authorisation delegation")
            print(f"User DID = {user_identity.did}")
            print(f"Agent DID = {agent_identity.did}")

        return user_identity, agent_identity

    def create_twin_with_control_delegation(
        self,
        twin_key_name: str,
        twin_seed: str,
        agent_identity: RegisteredIdentity,
        print_output: bool = False,
    ) -> RegisteredIdentity:
        twin_identity = (
            self._high_level_identity_api.create_twin_with_control_delegation(
                twin_seed=bytes.fromhex(twin_seed),
                twin_key_name=twin_key_name,
                agent_registered_identity=agent_identity,
            )
        )

        if print_output:
            print("Twin Identity created with Control delegation")
            print(f"Twin DID = {twin_identity.did}")

        return twin_identity
