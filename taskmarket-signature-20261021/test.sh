#!/usr/bin/env bash
set -euo pipefail
umask 077
kit_dir=$(cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$kit_dir/.scratch"
run_dir=$(mktemp -d "$kit_dir/.scratch/test.XXXXXXXX")
trap 'rm -rf -- "$run_dir"' EXIT
mkdir -p "$run_dir/home" "$run_dir/config" "$run_dir/data" "$run_dir/cache" "$run_dir/tmp"
env -i PATH="$PATH" HOME="$run_dir/home" XDG_CONFIG_HOME="$run_dir/config" XDG_DATA_HOME="$run_dir/data" XDG_CACHE_HOME="$run_dir/cache" TMPDIR="$run_dir/tmp" python3 "$kit_dir/prepare.py" --offline
env -i PATH="$PATH" HOME="$run_dir/home" XDG_CONFIG_HOME="$run_dir/config" XDG_DATA_HOME="$run_dir/data" XDG_CACHE_HOME="$run_dir/cache" TMPDIR="$run_dir/tmp" node --experimental-permission --allow-fs-read="$kit_dir" "$kit_dir/signatures.test.mjs"
env -i PATH="$PATH" HOME="$run_dir/home" XDG_CONFIG_HOME="$run_dir/config" XDG_DATA_HOME="$run_dir/data" XDG_CACHE_HOME="$run_dir/cache" TMPDIR="$run_dir/tmp" PYTHONDONTWRITEBYTECODE=1 python3 "$kit_dir/prepare.test.py"
