#!/usr/bin/env python3
"""빌드된 site/ 를 임시 서버로 띄워 watch/tsf 페이지 스크린샷 (Playwright).
사용: python watch/shot.py  → watch/state/shot_{watch,tsf}.png"""
import http.server
import os
import threading

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
PORT = 8796  # 스모크 전용 임시 포트 (8791 상시 서버와 충돌 방지)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)

    def log_message(self, *a):
        pass


def main():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        for name in ("watch", "tsf", "index", "rl_algos"):
            pg.goto(f"http://127.0.0.1:{PORT}/{name}.html", wait_until="networkidle")
            out = os.path.join(HERE, "state", f"shot_{name}.png")
            pg.screenshot(path=out, full_page=(name != "index"))
            print("shot:", out)
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
