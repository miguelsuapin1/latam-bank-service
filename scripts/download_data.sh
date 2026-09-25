#!/usr/bin/env bash
# Mirror the organizer dataset (read-only S3) into data/raw/.
# Credentials: page 2 of the LATAM Bank Data Dictionary (Sept 2026 version).
# Configure once with `aws configure --profile factored` (region us-east-2). Never commit keys.
set -euo pipefail

BUCKET="s3://factored-datathon-2026-s3-157725502942-us-east-2-an/data/"
PROFILE="${AWS_PROFILE:-factored}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/data/raw/"

# digital_events (~3.6 GB) is skipped by default; pass --all to include it.
EXCLUDE=(--exclude "digital_events/*")
[[ "${1:-}" == "--all" ]] && EXCLUDE=()

aws s3 sync "$BUCKET" "$DEST" "${EXCLUDE[@]}" --only-show-errors --profile "$PROFILE"
echo "Synced to $DEST ($(du -sh "$DEST" | cut -f1), $(find "$DEST" -name '*.csv' | wc -l | tr -d ' ') CSV files)"
