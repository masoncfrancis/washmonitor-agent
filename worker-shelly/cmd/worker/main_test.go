package main

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"
)

func TestShellyClientReadPower(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(response http.ResponseWriter, request *http.Request) {
		if request.URL.Path != "/rpc/Shelly.GetStatus" {
			t.Fatalf("unexpected path %q", request.URL.Path)
		}
		_, _ = response.Write([]byte(`{"switch:0":{"apower":137.4}}`))
	}))
	defer server.Close()

	client := ShellyClient{
		baseURL:   server.URL,
		component: "switch:0",
		client:    server.Client(),
	}
	watts, err := client.ReadPower(context.Background())
	if err != nil {
		t.Fatalf("ReadPower returned error: %v", err)
	}
	if watts != 137.4 {
		t.Fatalf("ReadPower returned %v watts, want 137.4", watts)
	}
}

func TestShellyClientReadPowerRejectsMissingComponent(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(response http.ResponseWriter, request *http.Request) {
		_, _ = response.Write([]byte(`{"switch:1":{"apower":10}}`))
	}))
	defer server.Close()

	client := ShellyClient{baseURL: server.URL, component: "switch:0", client: server.Client()}
	if _, err := client.ReadPower(context.Background()); err == nil {
		t.Fatal("ReadPower returned nil error for missing component")
	}
}

func TestPowerMonitorRequiresActiveReading(t *testing.T) {
	monitor := NewPowerMonitor(20, 5, 10*time.Second)
	start := time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC)

	if monitor.Observe(start, 0, nil) {
		t.Fatal("monitor completed without an active reading")
	}
	if monitor.Observe(start.Add(10*time.Second), 0, nil) {
		t.Fatal("monitor completed without an active reading")
	}
	if monitor.State() != inactive {
		t.Fatalf("state = %v, want inactive", monitor.State())
	}
}

func TestPowerMonitorCompletesAfterContinuousInactivePower(t *testing.T) {
	monitor := NewPowerMonitor(20, 5, 10*time.Second)
	start := time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC)

	monitor.Observe(start, 100, nil)
	if monitor.Observe(start.Add(5*time.Second), 3, nil) {
		t.Fatal("monitor completed too early")
	}
	if !monitor.Observe(start.Add(15*time.Second), 3, nil) {
		t.Fatal("monitor did not complete after inactive duration")
	}
}

func TestPowerMonitorHysteresisAndErrorPause(t *testing.T) {
	monitor := NewPowerMonitor(20, 5, 10*time.Second)
	start := time.Date(2026, time.January, 1, 0, 0, 0, 0, time.UTC)

	monitor.Observe(start, 100, nil)
	monitor.Observe(start.Add(1*time.Second), 3, nil)
	monitor.Observe(start.Add(5*time.Second), 10, nil)
	if monitor.State() != inactive {
		t.Fatalf("state in hysteresis band = %v, want inactive", monitor.State())
	}
	monitor.Observe(start.Add(6*time.Second), 0, context.Canceled)
	if monitor.Observe(start.Add(7*time.Second), 0, nil) {
		t.Fatal("monitor counted the failed sample toward completion")
	}
	if monitor.Observe(start.Add(11*time.Second), 0, nil) {
		t.Fatal("monitor counted the error gap toward completion")
	}
	if !monitor.Observe(start.Add(13*time.Second), 0, nil) {
		t.Fatal("monitor did not complete after remaining valid inactive time")
	}
}

func TestLoadConfigRoleAndDefaults(t *testing.T) {
	values := map[string]string{
		"APPLIANCE_ROLE": "dryer",
		"API_SERVER_URL": "http://api:8001",
		"SHELLY_URL":     "http://shelly.local",
	}
	config, err := loadConfig(func(key string) string { return values[key] })
	if err != nil {
		t.Fatalf("loadConfig returned error: %v", err)
	}
	if config.Role != "dryer" || config.ShellyComponent != "switch:0" {
		t.Fatalf("unexpected config: %+v", config)
	}
}

func TestLoadUsers(t *testing.T) {
	file, err := os.CreateTemp(t.TempDir(), "config-*.json")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := file.WriteString(`[{"id":7,"phone":"+10000000000"}]`); err != nil {
		t.Fatal(err)
	}
	if err := file.Close(); err != nil {
		t.Fatal(err)
	}
	users, err := loadUsers(file.Name())
	if err != nil {
		t.Fatal(err)
	}
	if users[7] != "+10000000000" {
		t.Fatalf("unexpected users: %#v", users)
	}
}
