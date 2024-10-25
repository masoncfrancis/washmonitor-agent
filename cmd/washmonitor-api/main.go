package washmonitor_api

import (
	"context"
    "fmt"
    "github.com/gofiber/fiber/v2"
    "github.com/joho/godotenv"
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
    "net/http"
    "os"
    "strings"
)

// Main function
func main() {
    // Load the .env file
    if err := godotenv.Load(); err != nil {
        fmt.Println("Error loading .env file")
    }

    app := fiber.New()

    app.Post("/sendMessage", func(c *fiber.Ctx) error {

        // Define the request body
        type RequestMessageBody struct {
            Message string `json:"message"`
        }

        // Parse the request body
        apiKey := c.Get("X-API-Key")

        var requestBody RequestMessageBody
        if err := c.BodyParser(&requestBody); err != nil {
            return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
                "error": err.Error(),
            })
        }

        // Create a context
        ctx := context.TODO()

        // Connect to mongodb, check if the device exists, and verify auth key
        // Mongo connection string is found in env var MONGO_CONNECTION_STRING
        // If the device exists, send a message to the discord webhook
        // If the device does not exist, return an error message
        // If the auth key is invalid, return an error message

        mongoConnectionString := os.Getenv("MONGO_CONNECTION_STRING")
        client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoConnectionString))
        if err != nil {
            return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
                "error": err.Error(),
            })
        }

        // Connect to the database
        db := client.Database("washmonitor")
        collection := db.Collection("devices")

        // Check for api key in the database. it will be in a document in a field called "apiKey"
        // If the api key is not found, return an error message
        // If the api key is found, send a message to the discord webhook

        filter := bson.D{{"apiKey", apiKey}}

        type DBRecord struct {
            DeviceId string `json:"deviceid"`
            ApiKey   string `json:"apiKey"`
        }

        var result DBRecord
        err = collection.FindOne(ctx, filter).Decode(&result)
        if err != nil {
            if err == mongo.ErrNoDocuments {
                return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
                    "error": "Invalid API key",
                })
            }
            return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
                "error": "Failed to query MongoDB",
            })
        }

        // Send the message to the discord webhook
        // Discord webhook URL is in env var DISCORD_WEBHOOK

        webhookRequestContent := fmt.Sprintf(`{"content": "%s"}`, requestBody.Message)
        // Send request to url
        _, err = http.Post(os.Getenv("DISCORD_WEBHOOK"), "application/json", strings.NewReader(webhookRequestContent))
        if err != nil {
            return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
                "error": "Failed to send message to Discord",
            })
        }

        return c.JSON(fiber.Map{
            "message": "Message sent successfully",
        })
    })

    app.Listen(":3000")
}