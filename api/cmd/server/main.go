package main

import (
    "github.com/gofiber/fiber/v2"
)

var agentStatus = "idle"

func main() {
    app := fiber.New()

    app.Post("/setAgentStatus", func(c *fiber.Ctx) error {
        type request struct {
            Status string `json:"status"`
        }
        var body request
        if err := c.BodyParser(&body); err != nil {
            return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
                "error": "Malformed request",
            })
        }
        if body.Status != "monitor" && body.Status != "idle" {
            return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
                "error": "Status must be 'monitor' or 'idle'",
            })
        }
        agentStatus = body.Status
        return c.Status(fiber.StatusOK).JSON(fiber.Map{
            "message": "Agent status set successfully",
            "status":  agentStatus,
        })
    })

    app.Get("/getAgentStatus", func(c *fiber.Ctx) error {
        return c.Status(fiber.StatusOK).JSON(fiber.Map{
            "status": agentStatus,
        })
    })

    app.Listen(":8001")
}