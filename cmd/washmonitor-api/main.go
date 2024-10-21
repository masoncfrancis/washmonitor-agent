package washmonitor_api

import (
	"fmt"
	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/mongo"
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
			Message  string `json:"message"`
			DeviceId string `json:"deviceId"`
		}

		// Parse the request body
		apiKey := c.Get("X-API-Key")

		var requestBody RequestMessageBody
		if err := c.BodyParser(&requestBody); err != nil {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": err.Error(),
			})
		}

		// Connect to mongodb, check if the device exists, and verify auth key
		// If the device exists, send a message to the discord webhook
		// If the device does not exist, return an error message
		// If the auth key is invalid, return an error message
		// TODO finish this

	})

}
