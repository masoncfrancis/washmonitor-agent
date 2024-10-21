# This Dockerfile works by first building the application in a container with the Golang Alpine image, and then copying the
# binary to a smaller image for running the application. The final image is has only the linux kernel and the bare minimum
# required to run an executable. The purpose of this is to reduce the size of the final image, and to make it more secure.

# Use the Golang Alpine image as the base image for building
# The Alpine one was chosen because it is a much smaller download than the main golang image and can accomplish the same thing
FROM golang:alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the source code to the builder container
COPY . .

# Build the binary, with all the dependencies included
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o washmonitor-api ./cmd/washmonitor-api

# Obtain CA certificates using an alpine image
FROM alpine:latest as certs
RUN apk --update add ca-certificates

# Create a new image from scratch for the final image, and copy the binary and the CA certificates to it
FROM scratch
WORKDIR /app
COPY --from=certs /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=builder /app/washmonitor-api /app/washmonitor-api

# Command to run the binary
CMD ["/app/washmonitor-api"]