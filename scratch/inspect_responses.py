import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = {
    "eztv": "https://eztv.ag/search/ubuntu",
    "1337x": "https://1337x.ws/sort-search/ubuntu/seeders/desc/1/",
    "tpb": "https://thepiratebay.org/search/ubuntu/0/7//",
    "zq": "https://zooqle.com/search?q=ubuntu"
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
            print("Headers:")
            for k, v in response.info().items():
                print(f"  {k}: {v}")
            print("\nFirst 500 chars of HTML:")
            print(html[:500])
    except Exception as e:
        print(f"Error fetching {url}: {e}")
