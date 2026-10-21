#!/usr/bin/env bash
set -euo pipefail
pet_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -d "$pet_root/.venv" ]]; then
  python3 -m venv "$pet_root/.venv"
fi
if ! "$pet_root/.venv/bin/python" -c 'import PySide6' >/dev/null 2>&1; then
  "$pet_root/.venv/bin/pip" install -r "$pet_root/requirements.txt"
fi
export QT_QPA_PLATFORM=xcb
exec "$pet_root/.venv/bin/python" "$pet_root/updater.py" "$@"
