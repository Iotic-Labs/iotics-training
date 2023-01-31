package main

import (
	"encoding/hex"
	"log"

	identityApi "github.com/Iotic-Labs/iotics-identity-go/pkg/api"
)

func main() {
	seed, err := identityApi.CreateDefaultSeed()
	if err != nil {
		log.Fatalf("Could not create Seed: %v", err)
	}
	log.Printf("Seed: %s", hex.EncodeToString(seed))
}
