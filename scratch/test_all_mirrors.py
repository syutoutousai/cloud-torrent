import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

def test_url(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            status = response.getcode()
            if status == 200:
                if "loading" in html.lower() and "window.location.replace" in html:
                    return "JS_CHALLENGE", len(html), html[:200]
                if "cloudflare" in html.lower() and ("ray id" in html.lower() or "checking your browser" in html.lower()):
                    return "CLOUDFLARE", len(html), html[:200]
                if "hatalı deneme" in html.lower():
                    return "PARKED_DOMAIN", len(html), html[:200]
                return "OK", len(html), html[:200]
            return f"HTTP_{status}", len(html), html[:200]
    except urllib.error.HTTPError as e:
        return f"HTTP_ERR_{e.code}", 0, str(e)
    except Exception as e:
        return "ERROR", 0, str(e)

test_targets = {
    "zq": [
        "https://zooqle.com/search?q=ubuntu",
        "https://zooqle.nocensor.lol/search?q=ubuntu",
        "https://zooqle.com.se/search?q=ubuntu"
    ],
    "rbg": [
        "https://rarbg.to/torrents.php?search=ubuntu",
        "https://rarbgmirror.org/torrents.php?search=ubuntu",
        "https://rarbgbypass.org/torrents.php?search=ubuntu"
    ],
    "eztv": [
        "https://eztv.ag/search/ubuntu",
        "https://eztvx.to/search/ubuntu",
        "https://eztv.wf/search/ubuntu",
        "https://eztv.re/search/ubuntu"
    ],
    "1337x": [
        "https://1337x.to/sort-search/ubuntu/seeders/desc/1/",
        "https://1337x.ws/sort-search/ubuntu/seeders/desc/1/",
        "https://1337x.st/sort-search/ubuntu/seeders/desc/1/",
        "https://1337x.gd/sort-search/ubuntu/seeders/desc/1/",
        "https://1337x.so/sort-search/ubuntu/seeders/desc/1/"
    ],
    "tpb": [
        "https://thepiratebay.org/search/ubuntu/0/7//",
        "https://tpb.party/search/ubuntu/0/7//",
        "https://thepiratebay10.org/search/ubuntu/0/7//",
        "https://piratebayproxy.info/search/ubuntu/0/7//"
    ],
    "lt": [
        "https://www.limetorrents.cc/search/all/ubuntu/seeds/1/",
        "https://www.limetorrents.lol/search/all/ubuntu/seeds/1/",
        "https://www.limetorrents.co/search/all/ubuntu/seeds/1/"
    ],
    "nyaa": [
        "https://nyaa.si/?q=ubuntu",
        "https://nyaa.land/?q=ubuntu"
    ],
    "abb": [
        "https://audiobookbay.lu/page/1/?s=ubuntu",
        "https://audiobookbay.is/page/1/?s=ubuntu"
    ]
}

print("=== Running Detailed Mirror Availability Test ===")
for category, urls in test_targets.items():
    print(f"\n--- Category: {category} ---")
    for url in urls:
        status, length, snippet = test_url(url)
        print(f"  {url} -> {status} (Length: {length})")
        if status not in ["OK", "ERROR", "HTTP_ERR_403", "HTTP_ERR_404"]:
            print(f"    Snippet: {snippet.strip()}")
