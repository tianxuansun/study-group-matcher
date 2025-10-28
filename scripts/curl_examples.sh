#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:8000/api"

echo "== Users (first page) =="
curl -s "$BASE/users/?limit=5" | jq .

echo "== Courses (first page) =="
curl -s "$BASE/courses/?limit=5" | jq .

echo "== Groups for DEMO101 =="
CID=$(curl -s "$BASE/courses/?limit=50" | jq '.[] | select(.code=="DEMO101") | .id')
curl -s "$BASE/groups/?course_id=$CID&limit=50" | jq .

echo "== Stats Overview =="
curl -s "$BASE/stats/overview" | jq .

echo "== Export: course groups CSV =="
curl -s -D /dev/stderr "$BASE/exports/courses/$CID/groups.csv" | head -n 5

echo "== Export: roster CSV of first group =="
GID=$(curl -s "$BASE/groups/?course_id=$CID&limit=50" | jq '.[0].id')
curl -s -D /dev/stderr "$BASE/exports/groups/$GID/roster.csv" | cat
