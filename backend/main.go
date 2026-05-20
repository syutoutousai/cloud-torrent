package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/anacrolix/torrent"
	"github.com/anacrolix/torrent/metainfo"
	"github.com/gorilla/websocket"
)

var (
	upgrader = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool { return true },
	}
	client *torrent.Client
)

func main() {
	cfg := torrent.NewDefaultClientConfig()
	cfg.DataDir = "./downloads"
	
	var err error
	client, err = torrent.NewClient(cfg)
	if err != nil {
		log.Fatalf("error creating client: %s", err)
	}
	defer client.Close()

	// API Endpoints
	http.HandleFunc("/api/stats", handleStats)
	http.HandleFunc("/api/stream", handleStream)
	http.HandleFunc("/api/add", handleAdd)

	port := "4000"
	fmt.Printf("Backend starting on port %s...\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func handleStats(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	defer conn.Close()

	for {
		// Periodically send stats
		stats := map[string]interface{}{
			"torrents": len(client.Torrents()),
		}
		if err := conn.WriteJSON(stats); err != nil {
			break
		}
		time.Sleep(1 * time.Second)
	}
}

func handleAdd(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Access-Control-Allow-Origin", "*")
	magnet := r.URL.Query().Get("magnet")
	if magnet == "" {
		http.Error(w, "missing magnet", 400)
		return
	}

	t, err := client.AddMagnet(magnet)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	<-t.GotInfo()
	t.DownloadAll()
	w.Write([]byte("added"))
}

func handleStream(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Access-Control-Allow-Origin", "*")
	infoHashHex := r.URL.Query().Get("hash")
    indexStr := r.URL.Query().Get("index")
	fileIndex := 0 
    if indexStr != "" {
        fmt.Sscanf(indexStr, "%d", &fileIndex)
    }

    var hash metainfo.Hash
    err := hash.FromHexString(infoHashHex)
    if err != nil {
        http.Error(w, "invalid hash", 400)
        return
    }

	t, ok := client.Torrent(hash)
	if !ok {
		http.Error(w, "torrent not found", 404)
		return
	}

	<-t.GotInfo()
    if fileIndex >= len(t.Files()) {
        http.Error(w, "file index out of range", 400)
        return
    }

	file := t.Files()[fileIndex]
    fmt.Printf("Serving file [%d]: %s\n", fileIndex, file.Path())
	
	reader := file.NewReader()
	defer reader.Close()

	http.ServeContent(w, r, file.Path(), time.Now(), reader)
}
