#!/usr/bin/env python3
"""research_site 모니터링 탭 스모크 체크 (빌드 산출물 문자열 검증, stdlib).
사용: python watch/smoke.py  (research_site/ 에서)"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")


def main():
    w = io.open(os.path.join(SITE, "watch.html"), encoding="utf-8").read()
    t = io.open(os.path.join(SITE, "tsf.html"), encoding="utf-8").read()
    i = io.open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
    checks = [
        ("watch: algo 섹션", "RL 알고리즘 트렌드" in w),
        ("watch: 논문 카드 존재", 'class="paper' in w),
        ("watch: 메타바", "최근 수집" in w),
        ("watch: nav 탭", "tsf.html" in w and "watch.html" in w),
        ("watch: 2열 레이아웃", 'class="cols"' in w),
        ("watch: RL 축 헤더", "RL 축" in w),
        ("watch: 예측 축 헤더", "예측 축" in w),
        ("tsf: ILI 표", "ILI 논문성적" in t),
        ("tsf: gift 표", "GIFT-Eval top 15" in t),
        ("tsf: fev 표", "fev-bench top 15" in t),
        ("tsf: 델타 섹션", "최근 변화" in t),
        ("index: watch 카드", "watch.html" in i),
        ("index: tsf 카드", "TSF 트렌드" in i),
    ]
    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print("ALL_PASS" if not bad else "FAILED: " + str(bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
