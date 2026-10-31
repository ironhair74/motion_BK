#!/bin/sh
# 파트 조립: head → 개요 → 수시 → 정시 → 비교·로드맵·FAQ
cd "$(dirname "$0")" && cat parts/head.html parts/overview.html parts/susi.html parts/jeongsi.html parts/tail.html > index.html
