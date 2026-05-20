package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"

	"github.com/jpillora/scraper/scraper"
)

func main() {
	// 1. Read local scraper-config.json
	configBytes, err := ioutil.ReadFile("scraper-config.json")
	if err != nil {
		fmt.Printf("Failed to read config: %v\n", err)
		os.Exit(1)
	}

	// 2. Create scraper handler
	handler := &scraper.Handler{}
	if err := handler.LoadConfig(configBytes); err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		os.Exit(1)
	}

	// 3. Test each provider
	providers := []string{"nyaa", "abb", "eztv", "1337x", "lt"}
	query := "ubuntu"

	fmt.Printf("=== Testing Go Scraper Engine with query: %s ===\n", query)
	for _, p := range providers {
		fmt.Printf("\n----------------------------------------\n")
		fmt.Printf("Testing provider: %s...\n", p)
		req, _ := http.NewRequest("GET", fmt.Sprintf("/%s?query=%s", p, url.QueryEscape(query)), nil)
		rr := httptest.NewRecorder()
		handler.ServeHTTP(rr, req)

		if rr.Code != http.StatusOK {
			fmt.Printf("[FAIL] Provider %s returned HTTP %d: %s\n", p, rr.Code, rr.Body.String())
			continue
		}

		var results interface{}
		if err := json.Unmarshal(rr.Body.Bytes(), &results); err != nil {
			fmt.Printf("[FAIL] Failed to parse JSON results for %s: %v\n", p, err)
			continue
		}

		// Print formatted JSON results
		prettyJSON, _ := json.MarshalIndent(results, "", "  ")
		fmt.Printf("[OK] Provider %s returned successfully!\n", p)
		
		// If results is nil or empty list
		if results == nil {
			fmt.Printf("     Result: nil\n")
		} else {
			lines := 0
			// print first 20 lines of prettyJSON
			for _, char := range string(prettyJSON) {
				fmt.Print(string(char))
				if char == '\n' {
					lines++
					if lines > 25 {
						fmt.Println("     ... [truncated]")
						break
					}
				}
			}
		}
	}
}
