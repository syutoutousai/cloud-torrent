package server

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/jpillora/cloud-torrent/engine"
)

func (s *Server) stream(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	
	// /api/stream/<infohash>/<file_path>
	path := strings.TrimPrefix(r.URL.Path, "/api/stream/")
	parts := strings.SplitN(path, "/", 2)
	if len(parts) != 2 {
		http.Error(w, "Invalid stream path", 400)
		return
	}
	infohash := parts[0]
	filepath := parts[1]

	torrents := s.engine.GetTorrents()
	t, ok := torrents[infohash]
	if !ok {
		http.Error(w, "Torrent not found", 404)
		return
	}

	// Find the underlying anacrolix file
    var targetFile *engine.File
	for _, f := range t.Files {
		if f.Path == filepath {
            targetFile = f
			break
		}
	}

	if targetFile == nil || targetFile.AnacrolixFile() == nil {
		http.Error(w, "File not found or not loaded", 404)
		return
	}

	reader := targetFile.AnacrolixFile().NewReader()
	defer reader.Close()

	fmt.Printf("Streaming file: %s from %s\n", filepath, infohash)
	http.ServeContent(w, r, targetFile.Path, t.UpdatedAt(), reader)
}
