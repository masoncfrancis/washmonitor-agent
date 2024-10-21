package washmonitor_api

import (
	"fmt"
	"github.com/gofiber/fiber/v2"
)

// Main function
func main() {
	println("Hello, World!")

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

		// Connect to mongodb and check

	})

}
