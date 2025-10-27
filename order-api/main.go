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

// --- !! NEW BOTTLENECK SIMULATOR !! ---
// This buffered channel has a capacity of 1.
// It acts as a semaphore, ensuring only one goroutine
// can "hold the token" and process a payment at a time.
var paymentProcessorThrottle chan struct{}

// Simulates the 3-second payment verification
func verifyPayment() {
	// --- THIS IS THE NEW LOGIC ---
	log.Println("SYNC: Requesting payment processor lock...")
	// This line BLOCKS until there is space in the channel.
	paymentProcessorThrottle <- struct{}{}
	log.Println("SYNC: Lock acquired. Processing payment for 3s...")

	time.Sleep(3 * time.Second)

	// This line "returns" the token to the channel,
	// allowing the *next* waiting request to proceed.
	<-paymentProcessorThrottle
	log.Println("SYNC: Payment complete. Lock released.")
	// --- END NEW LOGIC ---
}

// --- Handlers ---

// POST /orders/sync
func handleSyncOrder(c *gin.Context) {
	var order Order
	if err := c.BindJSON(&order); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid order payload"})
		return
	}

	order.OrderID = uuid.New().String()
	order.Status = "pending"
	order.CreatedAt = time.Now()
	log.Println("SYNC: Received order", order.OrderID)

	// Simulate the 3-second bottleneck
	verifyPayment()

	order.Status = "completed"
	c.JSON(http.StatusOK, order)
}

// POST /orders/async
func handleAsyncOrder(c *gin.Context) {
	var order Order
	if err := c.BindJSON(&order); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid order payload"})
		return
	}

	order.OrderID = uuid.New().String()
	order.Status = "pending"
	order.CreatedAt = time.Now()
	log.Println("ASYNC: Received order", order.OrderID)

	messageBody, err := json.Marshal(order)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to serialize order"})
		return
	}

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
	c.JSON(http.StatusAccepted, gin.H{
		"message":  "Order accepted for processing",
		"order_id": order.OrderID,
	})
}

// GET /health
func handleHealth(c *gin.Context) {
	c.Status(http.StatusOK)
}

func main() {
	// --- !! INITIALIZE THE THROTTLE !! ---
	// Create the channel with a buffer size of 1
	paymentProcessorThrottle = make(chan struct{}, 1)

	sdkConfig, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatal("Cannot load AWS config: ", err)
	}
	snsClient = sns.NewFromConfig(sdkConfig)

	snsTopicArn = os.Getenv("SNS_TOPIC_ARN")
	if snsTopicArn == "" {
		log.Fatal("SNS_TOPIC_ARN environment variable is not set")
	}

	log.Println("Successfully connected to SNS, topic ARN:", snsTopicArn)

	rand.New(rand.NewSource(time.Now().UnixNano()))
	r := gin.Default()
	r.POST("/orders/sync", handleSyncOrder)
	r.POST("/orders/async", handleAsyncOrder)
	r.GET("/health", handleHealth)

	log.Println("Starting API server on :8081 with REAL bottleneck")
	r.Run(":8081")
}
