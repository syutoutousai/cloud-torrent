import urllib.request
import urllib.error
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

url = "https://bitlordsearch.com/main.dart.js"
print(f"Streaming {url} to find potential API endpoints...")

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        # Read stream in chunks and search for keywords
        chunk_size = 1024 * 1024  # 1MB chunks
        chunk_num = 0
        potential_urls = set()
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            chunk_str = chunk.decode('utf-8', errors='ignore')
            chunk_num += 1
            print(f"Processing chunk {chunk_num}...")
            
            # Find URLs or domain strings
            # Look for things like http://... or https://... or api/... or bitlord...
            found = re.findall(r'(https?://[a-zA-Z0-9_\-\./\?&\+=]+)', chunk_str)
            for f in found:
                if "bitlord" in f.lower() or "api" in f.lower() or "search" in f.lower():
                    potential_urls.add(f)
            
            # Print a few samples if we have too many
            if len(potential_urls) > 100:
                print("Found too many URLs, stopping download...")
                break
                
        print(f"\n--- Found {len(potential_urls)} potential URLs/endpoints: ---")
        for u in sorted(list(potential_urls)):
            print(f"  {u}")
except Exception as e:
    print(f"Error fetching main.dart.js: {e}")
