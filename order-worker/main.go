package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sqs"
	"github.com/aws/aws-sdk-go-v2/service/sqs/types"
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

// --- SQS Message Body (SNS wraps the message) ---
type SnsMessage struct {
	Message string `json:"Message"`
}

var sqsClient *sqs.Client
var queueURL string

// Simulates the 3-second payment verification
func processOrder(order Order) {
	log.Println("WORKER: Processing order", order.OrderID, "...")
	time.Sleep(3 * time.Second)
	log.Println("WORKER: ✅ Successfully processed order", order.OrderID)
}

// This function runs in its own goroutine
func startWorker(id int, wg *sync.WaitGroup, messages <-chan types.Message) {
	defer wg.Done()
	log.Printf("Worker %d started\n", id)

	for msg := range messages {
		log.Printf("Worker %d: Received message %s\n", id, *msg.MessageId)

		// 1. SNS wraps the message, so we must unwrap it
		var snsMsg SnsMessage
		if err := json.Unmarshal([]byte(*msg.Body), &snsMsg); err != nil {
			log.Printf("Worker %d: ERROR - Could not unmarshal SNS wrapper: %v\n", id, err)
			continue // Don't delete, let it timeout and retry
		}

		// 2. Now unwrap the actual order
		var order Order
		if err := json.Unmarshal([]byte(snsMsg.Message), &order); err != nil {
			log.Printf("Worker %d: ERROR - Could not unmarshal order payload: %v\n", id, err)
			continue // Don't delete
		}

		// 3. Process the order (3s delay)
		processOrder(order)

		// 4. Delete the message from SQS
		_, err := sqsClient.DeleteMessage(context.TODO(), &sqs.DeleteMessageInput{
			QueueUrl:      aws.String(queueURL),
			ReceiptHandle: msg.ReceiptHandle,
		})
		if err != nil {
			log.Printf("Worker %d: ERROR - Failed to delete message: %v\n", id, err)
		}
	}
	log.Printf("Worker %d stopped\n", id)
}

func main() {
	// --- Load AWS Config ---
	sdkConfig, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatal("Cannot load AWS config: ", err)
	}
	sqsClient = sqs.NewFromConfig(sdkConfig)

	// --- Get Env Vars ---
	queueURL = os.Getenv("SQS_QUEUE_URL")
	if queueURL == "" {
		log.Fatal("SQS_QUEUE_URL environment variable is not set")
	}

	workerCountStr := os.Getenv("WORKER_GOROUTINES")
	if workerCountStr == "" {
		workerCountStr = "1" // Default to 1
	}
	workerCount, err := strconv.Atoi(workerCountStr)
	if err != nil || workerCount <= 0 {
		log.Fatalf("Invalid WORKER_GOROUTINES value: %s", workerCountStr)
	}

	log.Println("Starting worker service...")
	log.Println("Queue URL:", queueURL)
	log.Printf("Spawning %d worker goroutines\n", workerCount)

	// --- Setup Goroutines ---
	var wg sync.WaitGroup
	messageChannel := make(chan types.Message, workerCount) // Buffered channel

	// Start the workers
	for i := 1; i <= workerCount; i++ {
		wg.Add(1)
		go startWorker(i, &wg, messageChannel)
	}

	// --- SQS Polling Loop ---
	log.Println("Starting SQS polling...")
	for {
		// Long poll for messages
		resp, err := sqsClient.ReceiveMessage(context.TODO(), &sqs.ReceiveMessageInput{
			QueueUrl:            aws.String(queueURL),
			MaxNumberOfMessages: 10, // Get up to 10 messages
			WaitTimeSeconds:     20, // Long polling
		})

		if err != nil {
			log.Println("ERROR - Failed to receive from SQS:", err)
			time.Sleep(5 * time.Second) // Backoff on error
			continue
		}

		if len(resp.Messages) > 0 {
			log.Printf("Received %d messages from SQS\n", len(resp.Messages))
			for _, msg := range resp.Messages {
				messageChannel <- msg
			}
		}
	}
	// Note: This part is never reached, but good for completeness
	close(messageChannel)
	wg.Wait()
	log.Println("All workers finished. Exiting.")
}
