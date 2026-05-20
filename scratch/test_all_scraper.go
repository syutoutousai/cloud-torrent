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
	configBytes, err := ioutil.ReadFile("test_all_providers.json")
	if err != nil {
		fmt.Printf("Failed to read config: %v\n", err)
		os.Exit(1)
	}

	handler := &scraper.Handler{}
	if err := handler.LoadConfig(configBytes); err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		os.Exit(1)
	}

	providers := []string{"zq", "rbg", "eztv", "1337x", "abb", "tpb", "lt", "nyaa"}
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

		var results []interface{}
		if err := json.Unmarshal(rr.Body.Bytes(), &results); err != nil {
			fmt.Printf("[FAIL] Failed to parse JSON results for %s: %v. Body was: %s\n", p, err, rr.Body.String())
			continue
		}

		if len(results) == 0 {
			fmt.Printf("[FAIL] Provider %s returned 0 results (nil/empty).\n", p)
		} else {
			fmt.Printf("[OK] Provider %s returned %d results successfully!\n", p, len(results))
			// Print first result
			firstResult, _ := json.MarshalIndent(results[0], "", "  ")
			fmt.Printf("First result sample:\n%s\n", string(firstResult))
		}
	}
}
