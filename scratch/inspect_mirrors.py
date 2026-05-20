import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = {
    "1337x_so": "https://1337x.so/sort-search/ubuntu/seeders/desc/1/",
    "tpb_party": "https://tpb.party/search/ubuntu/0/7//",
    "tpb_10": "https://thepiratebay10.org/search/ubuntu/0/7//",
    "rarbg_mirror": "https://rarbgmirror.org/torrents.php?search=ubuntu"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

for name, url in urls.items():
    print(f"\n==================== Inspecting {name} ====================")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            print(f"HTTP Status: {response.getcode()}")
            print(f"Content Length: {len(html)}")
            if "loading" in html.lower() and "window.location.replace" in html:
                print("Status: JS_CHALLENGE")
            elif "cloudflare" in html.lower() and ("ray id" in html.lower() or "checking your browser" in html.lower()):
                print("Status: CLOUDFLARE")
            else:
                print("Status: Standard HTML response")
                print("Snippet (first 500 chars):")
                print(html[:500])
                print("\nSnippet (containing tr or table elements, search result search):")
                if "table" in html:
                    idx = html.find("table")
                    print(html[idx:idx+500])
                elif "tr" in html:
                    idx = html.find("tr")
                    print(html[idx:idx+500])
    except Exception as e:
        print(f"Error fetching {url}: {e}")
