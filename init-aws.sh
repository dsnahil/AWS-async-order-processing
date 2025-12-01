#!/bin/bash
echo "Initializing LocalStack resources..."

# Create SNS Topic
aws --endpoint-url=http://localhost:4566 sns create-topic --name order-processing-events

# Create SQS Queue
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name order-processing-queue

# Subscribe Queue to Topic
aws --endpoint-url=http://localhost:4566 sns subscribe \
    --topic-arn arn:aws:sns:us-west-2:000000000000:order-processing-events \
    --protocol sqs \
    --notification-endpoint arn:aws:sqs:us-west-2:000000000000:order-processing-queue

echo "Resources created successfully."