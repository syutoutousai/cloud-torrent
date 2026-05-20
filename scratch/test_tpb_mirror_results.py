import urllib.request
import urllib.error
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://tpb.party/search/ubuntu/0/7//",
    "https://thepiratebay10.org/search/ubuntu/0/7//"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

for url in urls:
    print(f"\n==================== Testing TPB Mirror: {url} ====================")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            print(f"HTTP Status: {response.getcode()}")
            print(f"Content Length: {len(html)}")
            
            # Check if there is <table id="searchResult">
            if "searchResult" in html:
                print("[OK] Found 'searchResult' table id!")
                
                # Check for tr or detLink elements in html
                rows = re.findall(r'<tr[^>]*>', html)
                print(f"Found {len(rows)} <tr> tags in html")
                
                detlinks = re.findall(r'class="detLink"', html)
                print(f"Found {len(detlinks)} 'class=\"detLink\"' occurrences in html")
                
                magnets = re.findall(r'href="magnet:\?[^"]+"', html)
                print(f"Found {len(magnets)} magnet links in html")
                
                if len(detlinks) > 0:
                    print("Sample detLink:")
                    idx = html.find('class="detLink"')
                    print(html[max(0, idx-50):min(len(html), idx+200)])
            else:
                print("[FAIL] 'searchResult' table id NOT found in HTML!")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
