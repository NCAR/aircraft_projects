#!/bin/bash
#
# Tests for createMovies.sh camera directory resolution: unpacked flight
# directories, flight tarfiles that need extracting, and flights with no
# images at all.
#
# Everything happens in a scratch directory - no project data is touched and
# combineCameras.pl is never run (we always answer "n" at the prompt). Run
# from anywhere:
#
#     ./testCreateMovies.sh
#
# Exits 0 if all tests pass, 1 otherwise.

test_dir=$(cd "$(dirname "$0")" && pwd)
cam_src=$(dirname "$test_dir")	# .../scripts/camera
script="${cam_src}/createMovies.sh"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

# assert_contains <description> <haystack> <needle>
assert_contains() {
    case "$2" in
        *"$3"*) pass "$1" ;;
        *) fail "$1 (expected to find: $3)" ;;
    esac
}

# assert_not_contains <description> <haystack> <needle>
assert_not_contains() {
    case "$2" in
        *"$3"*) fail "$1 (did not expect to find: $3)" ;;
        *) pass "$1" ;;
    esac
}

assert_dir() {
    if [ -d "$2" ]; then pass "$1"; else fail "$1 (no such directory: $2)"; fi
}

assert_file() {
    if [ -f "$2" ]; then pass "$1"; else fail "$1 (no such file: $2)"; fi
}

assert_no_file() {
    if [ -f "$2" ]; then fail "$1 (file should not exist: $2)"; else pass "$1"; fi
}

# ------------------------------- Fixtures --------------------------------
# Scratch tree mimicking the two dirs createMovies.sh reads:
#   RAW_DATA_DIR/PROJECT/camera_images/flight_number_<flight>/<direction>/
#   PROJ_DIR/PROJECT/AIRCRAFT/scripts/	  (where param files are written)
# PROJ_DIR/scripts/camera is symlinked to the real scripts so the script
# finds movieParamFile.template.

tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/testCreateMovies.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT

export PROJECT="TESTPROJ"
export AIRCRAFT="N123AB"
export RAW_DATA_DIR="${tmp_dir}/raw"
export PROJ_DIR="${tmp_dir}/proj"

cam_data="${RAW_DATA_DIR}/${PROJECT}/camera_images"
param_dir="${PROJ_DIR}/${PROJECT}/${AIRCRAFT}/scripts"
mkdir -p "$cam_data" "$param_dir" "${PROJ_DIR}/scripts"
ln -s "$cam_src" "${PROJ_DIR}/scripts/camera"

# The script builds its template paths from PROJ_DIR, so it reports them
# through the symlink above rather than as the real scripts/camera path.
tmpl_path="${PROJ_DIR}/scripts/camera"

# make_flight_dirs <flight> [direction ...] - unpacked flight dir with one
# image per direction. Defaults to all four directions.
make_flight_dirs() {
    local flight=$1
    shift
    local dirs=("$@")
    if [ ${#dirs[@]} -eq 0 ]; then
        dirs=(forward left right down)
    fi
    local dir
    for dir in "${dirs[@]}"; do
        mkdir -p "${cam_data}/flight_number_${flight}/${dir}"
        : > "${cam_data}/flight_number_${flight}/${dir}/20260728_120000.jpg"
    done
}

# rf01: unpacked directories, no tarfile.
make_flight_dirs rf01

# rf02: tarfile only - built from real dirs, which are then removed.
make_flight_dirs rf02
tar -cf "${cam_data}/flight_number_rf02.tar" -C "$cam_data" flight_number_rf02/
rm -rf "${cam_data}/flight_number_rf02"

# rf03: nothing at all.

# rf04: a file named like a tarfile but not actually one, so tar fails.
echo "this is not a tarfile" > "${cam_data}/flight_number_rf04.tar"

# rf05: forward camera only, and still tarred - the case the forward-only
# template exists for, with the directions only knowable after extraction.
make_flight_dirs rf05 forward
tar -cf "${cam_data}/flight_number_rf05.tar" -C "$cam_data" flight_number_rf05/
rm -rf "${cam_data}/flight_number_rf05"

# rf06: forward and down only - a combination with no template.
make_flight_dirs rf06 forward down

# run_flight <flight> - answer "n" at the prompt so combineCameras.pl is
# never invoked. Returns combined stdout/stderr.
#
# Note the prompt text itself never appears in the output: bash only writes a
# "read -p" prompt when stdin is a terminal, and we pipe the answer in. So the
# marker for "the flight got as far as the prompt" is the "Skipping flight:
# <flight>" line printed after answering "n" - distinct from the earlier
# "No camera images found for flight <flight>. Skipping." bail-out.
run_flight() {
    printf 'n\n' | "$script" "$1" 2>&1
}

# ------------------------------ The tests --------------------------------

echo "Test 1: unpacked flight directories are used as-is"
out=$(run_flight rf01)
assert_not_contains "no extraction attempted" "$out" "Extracting"
assert_not_contains "flight not skipped for missing images" "$out" \
    "No camera images found for flight rf01"
assert_contains "reached the combineCameras.pl prompt" "$out" \
    "Skipping flight: rf01"

echo "Test 2: flight tarfile is extracted and directions found on rescan"
out=$(run_flight rf02)
assert_contains "reports extracting the tarfile" "$out" \
    "Extracting ${cam_data}/flight_number_rf02.tar"
assert_dir "flight directory was unpacked" "${cam_data}/flight_number_rf02/forward"
assert_not_contains "flight not skipped after extraction" "$out" \
    "No camera images found for flight rf02"
assert_contains "reached the combineCameras.pl prompt" "$out" \
    "Skipping flight: rf02"
assert_file "param file was created" "${param_dir}/movieParamFile_rf02"

echo "Test 3: no directories and no tarfile skips the flight"
out=$(run_flight rf03)
assert_contains "reports the missing tarfile" "$out" \
    "No tarfile ${cam_data}/flight_number_rf03.tar found"
assert_contains "skips the flight" "$out" \
    "No camera images found for flight rf03. Skipping."
assert_not_contains "never reaches the prompt" "$out" "Skipping flight: rf03"
assert_no_file "no param file created" "${param_dir}/movieParamFile_rf03"

echo "Test 4: unextractable tarfile is reported and the flight is skipped"
out=$(run_flight rf04)
assert_contains "reports the extraction failure" "$out" \
    "Error: couldn't extract ${cam_data}/flight_number_rf04.tar"
assert_contains "skips the flight" "$out" \
    "No camera images found for flight rf04. Skipping."
assert_not_contains "never reaches the prompt" "$out" "Skipping flight: rf04"
assert_no_file "no param file created" "${param_dir}/movieParamFile_rf04"

echo "Test 5: multiple flights - a skipped flight doesn't stop the next one"
out=$(printf 'n\nn\n' | "$script" rf03 rf01 2>&1)
assert_contains "skips the flight with no images" "$out" \
    "No camera images found for flight rf03. Skipping."
assert_contains "still processes the following flight" "$out" \
    "Skipping flight: rf01"

echo "Test 6: all four directions use the four camera template"
# Test 1 already generated this one, and an existing param file is never
# regenerated, so clear it to exercise template selection.
rm -f "${param_dir}/movieParamFile_rf01" "${param_dir}/movieParamFile_rf01.bak"
out=$(run_flight rf01)
assert_contains "picks movieParamFile.template" "$out" \
    "Using template ${tmpl_path}/movieParamFile.template for cameras: forward left right down"
assert_contains "param file has four cameras" \
    "$(cat "${param_dir}/movieParamFile_rf01")" "numCameras = 4"

echo "Test 7: a forward-only tarred flight uses the forward-only template"
out=$(run_flight rf05)
assert_contains "extracts before deciding on a template" "$out" \
    "Extracting ${cam_data}/flight_number_rf05.tar"
assert_contains "picks movieParamFile_fwd.template" "$out" \
    "Using template ${tmpl_path}/movieParamFile_fwd.template for cameras: forward"
assert_contains "param file has one camera" \
    "$(cat "${param_dir}/movieParamFile_rf05")" "numCameras = 1"
assert_contains "param file points at the forward dir" \
    "$(cat "${param_dir}/movieParamFile_rf05")" "flight_number_rf05/forward"
assert_contains "reached the combineCameras.pl prompt" "$out" \
    "Skipping flight: rf05"

echo "Test 8: a direction combination with no template skips the flight"
out=$(run_flight rf06)
assert_contains "reports the unhandled combination" "$out" \
    "No template for cameras: forward down"
assert_not_contains "never reaches the prompt" "$out" "Skipping flight: rf06"
assert_no_file "no param file created" "${param_dir}/movieParamFile_rf06"

echo "Test 9: an existing param file is used whatever the directions are"
: > "${param_dir}/movieParamFile_rf06"
out=$(run_flight rf06)
assert_contains "uses the existing param file" "$out" \
    "Using existing ${param_dir}/movieParamFile_rf06"
assert_contains "reached the combineCameras.pl prompt" "$out" \
    "Skipping flight: rf06"

echo
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ]
