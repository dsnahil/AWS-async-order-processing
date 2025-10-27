package main

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

// --- Structs (must match the API's) ---
type Item struct {
	ItemID   string `json:"item_id"`
	Quantity int    `json:"quantity"`
}

type Order struct {
	OrderID    string    `json:"order_id"`
	CustomerID int       `json:"customer_id"`
	Status     string    `json:"status"`
	Items      []Item    `json:"items"`
	CreatedAt  time.Time `json:"created_at"`
}

// Simulates the 3-second payment verification
func processOrder(order Order) {
	log.Println("LAMBDA: Processing order", order.OrderID, "...")
	time.Sleep(3 * time.Second)
	log.Println("LAMBDA: ✅ Successfully processed order", order.OrderID)
}

// This is the main Lambda handler function
// It's triggered by an SNS event
func handler(ctx context.Context, snsEvent events.SNSEvent) {
	// An SNS event can contain multiple messages (records)
	for _, record := range snsEvent.Records {
		snsRecord := record.SNS

		log.Printf("Received SNS message ID = %s\n", snsRecord.MessageID)

		// 1. Unmarshal the Order from the SNS message body
		var order Order
		if err := json.Unmarshal([]byte(snsRecord.Message), &order); err != nil {
			log.Printf("ERROR - Could not unmarshal order payload: %v\n", err)
			continue // Go to the next record
		}

		// 2. Process the order (3s delay)
		processOrder(order)
	}
}

func main() {
	// This starts the Lambda handler
	lambda.Start(handler)
}
