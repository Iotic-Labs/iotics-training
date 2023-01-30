package helpers

import (
	"encoding/hex"
	"log"
	"time"

	identityApi "github.com/Iotic-Labs/iotics-identity-go/pkg/api"
	"github.com/Iotic-Labs/iotics-identity-go/pkg/register"
)

func CreateUserIdentity(resolver register.ResolverClient, keyName string, seed string) register.RegisteredIdentity {
	seedBytes, _ := hex.DecodeString(seed)

	userIdentity, err := identityApi.CreateUserIdentity(
		resolver,
		&identityApi.CreateIdentityOpts{
			Seed:    seedBytes,
			KeyName: keyName,
		},
	)
	if err != nil {
		log.Fatalf("Could not create User Identity: %v", err)
	}

	return userIdentity
}

func CreateAgentIdentity(resolver register.ResolverClient, keyName string, seed string) register.RegisteredIdentity {
	seedBytes, _ := hex.DecodeString(seed)

	agentIdentity, err := identityApi.CreateAgentIdentity(
		resolver,
		&identityApi.CreateIdentityOpts{
			Seed:    seedBytes,
			KeyName: keyName,
		},
	)
	if err != nil {
		log.Fatalf("Could not create Agent Identity: %v", err)
	}

	return agentIdentity
}

func CreateTwinIdentity(resolver register.ResolverClient, keyName string, seed string) register.RegisteredIdentity {
	seedBytes, _ := hex.DecodeString(seed)

	twinIdentity, err := identityApi.CreateTwinIdentity(
		resolver,
		&identityApi.CreateIdentityOpts{
			Seed:    seedBytes,
			KeyName: keyName,
		},
	)
	if err != nil {
		log.Fatalf("Could not create Twin Identity: %v", err)
	}

	return twinIdentity
}

func AuthenticationDelegation(resolver register.ResolverClient, userIdentity register.RegisteredIdentity, agentIdentity register.RegisteredIdentity) {
	authErr := identityApi.UserDelegatesAuthenticationToAgent(resolver, userIdentity, agentIdentity, "#authDeleg")
	if authErr != nil {
		log.Fatalf("Could not auth delegate Agent: %v", authErr)
	}
}

func ControlDelegation(resolver register.ResolverClient, twinIdentity register.RegisteredIdentity, agentIdentity register.RegisteredIdentity) {
	ctrlErr := identityApi.TwinDelegatesControlToAgent(resolver, twinIdentity, agentIdentity, "#controlDeleg")

	if ctrlErr != nil {
		log.Fatalf("Could not ctrl delegate Agent: %v", ctrlErr)
	}
}

func CreateUserAndAgentWithAuthDelegation(
	resolver register.ResolverClient,
	userSeed string, userKeyName string,
	agentSeed string, agentKeyName string,
) (register.RegisteredIdentity, register.RegisteredIdentity) {
	userSeedBytes, _ := hex.DecodeString(userSeed)
	agentSeedBytes, _ := hex.DecodeString(agentSeed)

	userIdentity, agentIdentity, err := identityApi.CreateUserAndAgentWithAuthDelegation(
		resolver,
		&identityApi.CreateUserAndAgentWithAuthDelegationOpts{
			UserSeed:       userSeedBytes,
			UserKeyName:    userKeyName,
			AgentSeed:      agentSeedBytes,
			AgentKeyName:   agentKeyName,
			DelegationName: "#authDeleg",
		},
	)
	if err != nil {
		log.Fatalf("Could not create User and Agent with Auth deleg: %v", err)
	}

	return userIdentity, agentIdentity
}

func CreateTwinWithControlDelegation(resolver register.ResolverClient, twinSeed string, twinKeyName string, agentIdentity register.RegisteredIdentity) register.RegisteredIdentity {
	seedBytes, _ := hex.DecodeString(twinSeed)

	twinIdentity, err := identityApi.CreateTwinWithControlDelegation(
		resolver, &identityApi.CreateTwinOpts{
			Seed:           seedBytes,
			KeyName:        twinKeyName,
			AgentID:        agentIdentity,
			DelegationName: "#controlDeleg",
		},
	)
	if err != nil {
		log.Fatalf("Could not create Twin Identity with Ctrl deleg: %v", err)
	}

	return twinIdentity
}

func GetToken(agentIdentity register.RegisteredIdentity, userIdentity register.RegisteredIdentity, duration time.Duration) string {
	token, err := identityApi.CreateAgentAuthToken(agentIdentity, userIdentity.Did(), time.Second*duration, "audience")
	if err != nil {
		log.Fatalf("Failed to create Agent auth token %v ", err)
	}

	return string(token)
}
