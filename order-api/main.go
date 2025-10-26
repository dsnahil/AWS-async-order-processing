package main

import (
	"context"
	"encoding/json"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sns"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// --- Structs (from assignment) ---
type Item struct {
	ItemID   string `json:"item_id"`
	Quantity int    `json:"quantity"`
}

type Order struct {
	OrderID    string    `json:"order_id"`
	CustomerID int       `json:"customer_id"`
	Status     string    `json:"status"` // pending, processing, completed
	Items      []Item    `json:"items"`
	CreatedAt  time.Time `json:"created_at"`
}

// --- AWS Clients ---
var snsClient *sns.Client
var snsTopicArn string

// Simulates the 3-second payment verification
func verifyPayment() {
	time.Sleep(3 * time.Second)
}

// --- Handlers ---

// POST /orders/sync
// Implement synchronous order processing:
// POST /orders/sync → Verify Payment (3s delay) → Return 200 OK
func handleSyncOrder(c *gin.Context) {
	var order Order
	if err := c.BindJSON(&order); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid order payload"})
		return
	}

	// Set order details
	order.OrderID = uuid.New().String()
	order.Status = "pending"
	order.CreatedAt = time.Now()

	log.Println("SYNC: Received order", order.OrderID)

	// Simulate the 3-second bottleneck
	log.Println("SYNC: Verifying payment for", order.OrderID, "...")
	verifyPayment()
	log.Println("SYNC: Payment verified for", order.OrderID)

	order.Status = "completed"
	c.JSON(http.StatusOK, order)
}

// POST /orders/async
// POST /orders/async → Publish to SNS → Return 202 Accepted
func handleAsyncOrder(c *gin.Context) {
	var order Order
	if err := c.BindJSON(&order); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid order payload"})
		return
	}

	// Set order details
	order.OrderID = uuid.New().String()
	order.Status = "pending" // The worker will update this
	order.CreatedAt = time.Now()

	log.Println("ASYNC: Received order", order.OrderID)

	// Convert order to JSON
	messageBody, err := json.Marshal(order)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to serialize order"})
		return
	}

	// Publish to SNS
	_, err = snsClient.Publish(context.TODO(), &sns.PublishInput{
		Message:  aws.String(string(messageBody)),
		TopicArn: aws.String(snsTopicArn),
	})

	if err != nil {
		log.Println("ERROR: Failed to publish to SNS:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to queue order"})
		return
	}

	log.Println("ASYNC: Queued order", order.OrderID)

	// Return 202 Accepted
	c.JSON(http.StatusAccepted, gin.H{
		"message":  "Order accepted for processing",
		"order_id": order.OrderID,
	})
}

// GET /health
// Health check: /health endpoint returning 200
func handleHealth(c *gin.Context) {
	c.Status(http.StatusOK)
}

func main() {
	// --- Load AWS Config ---
	sdkConfig, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatal("Cannot load AWS config: ", err)
	}
	snsClient = sns.NewFromConfig(sdkConfig)

	// Get SNS topic ARN from environment variable (set by Terraform)
	snsTopicArn = os.Getenv("SNS_TOPIC_ARN")
	if snsTopicArn == "" {
		log.Fatal("SNS_TOPIC_ARN environment variable is not set")
	}

	log.Println("Successfully connected to SNS, topic ARN:", snsTopicArn)

	// --- Setup Webserver ---
	// Seed random generator
	rand.New(rand.NewSource(time.Now().UnixNano()))

	r := gin.Default()
	r.POST("/orders/sync", handleSyncOrder)
	r.POST("/orders/async", handleAsyncOrder)
	r.GET("/health", handleHealth)

	log.Println("Starting API server on :8081")
	r.Run(":8081") // Listen on port 8081
}
