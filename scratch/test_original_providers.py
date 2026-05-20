import urllib.request
import urllib.error
import ssl

providers = {
    "zooqle": "https://zooqle.com/",
    "rarbg": "https://rarbg.to/",
    "tpb": "https://thepiratebay.org/"
}

mirrors = {
    "zooqle": ["https://zooqle.nocensor.lol/", "https://zooqle.nocensor.club/", "https://zooqle.com.se/"],
    "rarbg": ["https://rarbg.is/", "https://rarbg.to/", "https://rarbgmirror.org/"],
    "tpb": ["https://thepiratebay.org/", "https://tpb.party/", "https://thepiratebay10.org/", "https://piratebayproxy.info/"]
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test_url(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            return response.getcode(), None
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except urllib.error.URLError as e:
        return None, str(e.reason)
    except Exception as e:
        return None, str(e)

print("=== Testing Original Providers ===")
for name, url in providers.items():
    code, err = test_url(url)
    if code == 200 or code == 301 or code == 302:
        print(f"[OK] {name}: {url} -> HTTP {code}")
    else:
        print(f"[FAIL] {name}: {url} -> Code: {code}, Error: {err}")
        print(f"     Checking mirrors for {name}...")
        found_mirror = False
        for mirror in mirrors[name]:
            m_code, m_err = test_url(mirror)
            if m_code == 200 or m_code == 301 or m_code == 302:
                print(f"     [OK-MIRROR] {mirror} -> HTTP {m_code}")
                found_mirror = True
            else:
                print(f"     [FAIL-MIRROR] {mirror} -> Code: {m_code}, Error: {m_err}")
        if not found_mirror:
            print(f"     [WARN] No working mirrors found for {name}")
