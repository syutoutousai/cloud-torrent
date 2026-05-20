#!/usr/bin/env python3
"""
Seed Extractor & Integrator CLI for Cloud Torrent EX
Enables passing magnets, torrent file URLs, local torrent files, infohashes,
or auto-selecting search query results directly into the cloud-torrent-ex daemon.
"""

import sys
import argparse
import urllib.request
import urllib.parse
import json
import os

DEFAULT_SERVER = "http://localhost:3006"

def post_to_server(endpoint, data, content_type="text/plain"):
    url = f"{DEFAULT_SERVER.rstrip('/')}{endpoint}"
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": content_type},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            return True, res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return False, str(e)

def add_magnet(magnet_uri):
    print(f"[*] Posting magnet URI to server: {magnet_uri[:60]}...")
    ok, err = post_to_server("/api/magnet", magnet_uri.encode('utf-8'))
    if ok:
        print("[+] Success: Magnet link registered successfully.")
    else:
        print(f"[-] Error registering magnet: {err}")
    return ok

def add_torrent_url(torrent_url):
    print(f"[*] Posting torrent URL to server: {torrent_url}...")
    ok, err = post_to_server("/api/url", torrent_url.encode('utf-8'))
    if ok:
        print("[+] Success: Torrent URL registered successfully.")
    else:
        print(f"[-] Error registering torrent URL: {err}")
    return ok

def add_torrent_file(filepath):
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return False
    print(f"[*] Reading local torrent file: {filepath}...")
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"[-] Error reading file: {e}")
        return False
        
    print(f"[*] Posting raw torrent file bytes ({len(data)} bytes)...")
    ok, err = post_to_server("/api/torrentfile", data, content_type="application/x-bittorrent")
    if ok:
        print("[+] Success: Torrent file loaded successfully.")
    else:
        print(f"[-] Error registering torrent file: {err}")
    return ok

def add_infohash(infohash):
    infohash = infohash.strip()
    if len(infohash) != 40:
        print("[-] Error: Infohash must be a 40-character hex string.")
        return False
    # Construct standard magnet link with basic public trackers
    trackers = [
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://tracker.openbittorrent.com:80/announce",
        "udp://open.demonii.com:1337/announce",
        "udp://tracker.opentrackr.org:1337/announce"
    ]
    magnet_uri = f"magnet:?xt=urn:btih:{infohash}"
    for t in trackers:
        magnet_uri += f"&tr={urllib.parse.quote(t)}"
        
    print(f"[*] Constructed magnet from infohash: {magnet_uri[:60]}...")
    return add_magnet(magnet_uri)

def search_and_add(query, provider="nyaa"):
    print(f"[*] Querying server search endpoint for '{query}' using provider '{provider}'...")
    search_url = f"{DEFAULT_SERVER.rstrip('/')}/search/{provider}?query={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(search_url) as res:
            results = json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"[-] Failed to execute search: {e}")
        return False
        
    if not results or not isinstance(results, list):
        print(f"[-] No search results returned for query: '{query}'")
        return False
        
    print(f"[+] Found {len(results)} search results.")
    # Sort or find the first working result with seeds/peers
    # In cloud-torrent-ex, peers and seeds are strings (e.g. "5" or "12")
    def get_seed_count(item):
        try:
            return int(item.get("seeds", 0))
        except:
            return 0

    # Sort results descending by seeds
    sorted_results = sorted(results, key=get_seed_count, reverse=True)
    best_result = sorted_results[0]
    
    name = best_result.get("name", "Unknown Name")
    seeds = best_result.get("seeds", "0")
    peers = best_result.get("peers", "0")
    size = best_result.get("size", "Unknown Size")
    magnet = best_result.get("magnet", "")
    
    if not magnet:
        # Check if there is a path/url we can add instead
        path = best_result.get("path", "")
        if path and path.startswith("http"):
            print(f"[*] Selected Best Result (URL-based): {name} (Seeds: {seeds}, Size: {size})")
            return add_torrent_url(path)
        else:
            print("[-] Best search result does not contain a magnet link or valid torrent URL.")
            return False
            
    print(f"[+] Selected Best Result: {name}")
    print(f"    Size: {size} | Seeds: {seeds} | Peers: {peers}")
    return add_magnet(magnet)

def main():
    global DEFAULT_SERVER
    parser = argparse.ArgumentParser(description="Seed Extractor & Integrator CLI for Cloud Torrent EX")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--magnet", help="Raw Magnet URI to pass to the webapp")
    group.add_argument("-u", "--url", help="HTTP/HTTPS URL pointing to a .torrent file to download and load")
    group.add_argument("-f", "--file", help="Path to a local .torrent file to load")
    group.add_argument("-i", "--infohash", help="40-character hex infohash to convert and load")
    group.add_argument("-s", "--search", help="Search term to auto-query, select best result, and download")
    
    parser.add_argument("-p", "--provider", default="nyaa", help="Search provider to use when --search is specified (default: nyaa)")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"Cloud Torrent EX server URL (default: {DEFAULT_SERVER})")
    
    args = parser.parse_args()
    
    DEFAULT_SERVER = args.server
    
    if args.magnet:
        add_magnet(args.magnet)
    elif args.url:
        add_torrent_url(args.url)
    elif args.file:
        add_torrent_file(args.file)
    elif args.infohash:
        add_infohash(args.infohash)
    elif args.search:
        search_and_add(args.search, args.provider)

if __name__ == "__main__":
    main()
