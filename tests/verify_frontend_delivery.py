import urllib.request
import re

def verify():
    url = "http://localhost:8000/"
    html = urllib.request.urlopen(url).read().decode("utf-8")
    print("[OK] Root index.html loaded successfully! (Status 200, length:", len(html), ")")

    js_match = re.search(r'src="(/assets/[^"]+\.js)"', html)
    css_match = re.search(r'href="(/assets/[^"]+\.css)"', html)

    if js_match:
        js_url = "http://localhost:8000" + js_match.group(1)
        js_data = urllib.request.urlopen(js_url).read()
        print(f"[OK] JavaScript bundle loaded! ({js_url}, {len(js_data)} bytes)")

    if css_match:
        css_url = "http://localhost:8000" + css_match.group(1)
        css_data = urllib.request.urlopen(css_url).read()
        print(f"[OK] CSS bundle loaded! ({css_url}, {len(css_data)} bytes)")

    # Test API
    sys_status = urllib.request.urlopen("http://localhost:8000/api/system/status").read().decode("utf-8")
    print("[OK] Backend System API active:", sys_status)

if __name__ == "__main__":
    verify()
