package server

import (
	"encoding/json"
	"net/http"
	"strings"

	"github.com/anacrolix/torrent/metainfo"
)

func (s *Server) check(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Access-Control-Allow-Origin", "*")
    query := r.URL.Query().Get("q")
    if query == "" {
        http.Error(w, "missing query", 400)
        return
    }

    result := map[string]interface{}{
        "is_magnet": strings.HasPrefix(query, "magnet:?"),
        "is_infohash": len(query) == 40 || len(query) == 32,
    }

    // Attempt to parse magnet to see if it's valid
    if result["is_magnet"].(bool) {
        _, err := metainfo.ParseMagnetURI(query)
        result["valid_magnet"] = (err == nil)
        if err != nil {
            result["error"] = err.Error()
        }
    }

    json.NewEncoder(w).Encode(result)
}
