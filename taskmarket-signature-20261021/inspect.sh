#!/usr/bin/env bash
set -euo pipefail
umask 077
kit_dir=$(cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$kit_dir/.scratch"
run_dir=$(mktemp -d "$kit_dir/.scratch/inspect.XXXXXXXX")
trap 'rm -rf -- "$run_dir"' EXIT
mkdir -p "$run_dir/home" "$run_dir/config" "$run_dir/data" "$run_dir/cache" "$run_dir/tmp"
env -i PATH="$PATH" HOME="$run_dir/home" XDG_CONFIG_HOME="$run_dir/config" XDG_DATA_HOME="$run_dir/data" XDG_CACHE_HOME="$run_dir/cache" TMPDIR="$run_dir/tmp" python3 "$kit_dir/prepare.py" --offline >&2
env -i PATH="$PATH" HOME="$run_dir/home" XDG_CONFIG_HOME="$run_dir/config" XDG_DATA_HOME="$run_dir/data" XDG_CACHE_HOME="$run_dir/cache" TMPDIR="$run_dir/tmp" node --experimental-permission --allow-fs-read="$kit_dir" "$kit_dir/inspect.mjs"
