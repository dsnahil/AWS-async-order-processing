# Stage 1: Build the Go binary
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy the go.mod and go.sum files and download dependencies
COPY go.mod ./
RUN go mod download

# Copy the source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -o /order-worker

# Stage 2: Create the final, small image
FROM alpine:latest

WORKDIR /

# Copy the built binary from the builder stage
COPY --from=builder /order-worker /order-worker

# Run the binary
ENTRYPOINT ["/order-worker"]