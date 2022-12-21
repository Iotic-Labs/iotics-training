package main

import (
	"encoding/hex"
	"log"

	identityApi "github.com/Iotic-Labs/iotics-identity-go/pkg/api"
)

func main() {
	seed, seedErr := identityApi.CreateDefaultSeed()
	if seedErr != nil {
		log.Fatalf("Could not create Seed: %v", seedErr)
	}
	log.Printf("Seed: %s", hex.EncodeToString(seed))
}
