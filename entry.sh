#!/usr/bin/env bash
set -euo pipefail
rc=0
trap 'rc=$?; echo >&2 "$0: Error on line "$LINENO": $BASH_COMMAND"; exit $rc' ERR

set -x
function main() {
    python3 /app/scrape.py
    python3 /app/output.py
    echo "Done. Press ctrl+c to exit"
}

main "$@"
