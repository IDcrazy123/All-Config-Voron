#!/usr/bin/env bash
set -u

api="http://127.0.0.1:7125"
cmd="CALIBRATE_TOOL_OFFSETS TOOLS=0,1,2,3,4 CALIBRATE_XY=0 CALIBRATE_Z=1 ALLOW_SHUTTLE_Z=1 SAVE_CONFIG=0 DRY_RUN=0 CLEAN_NOZZLE=0 CONTINUE_ON_ERROR=1"
response="/tmp/tkc-30abb5-all-response.txt"
start_time=$(python3 -c 'import time; print(time.time())')

echo "=== command ==="
echo "$cmd"
echo "start_time=$start_time"
rm -f -- "$response"
curl -sS --max-time 900 -w '\nhttp_status=%{http_code}\n' \
  -X POST --data-urlencode "script=$cmd" "$api/printer/gcode/script" \
  >"$response" 2>&1 &
curl_pid=$!

poll=0
while kill -0 "$curl_pid" 2>/dev/null; do
  if (( poll % 10 == 0 )); then
    summary=$(curl -fsS "$api/printer/objects/query?webhooks&idle_timeout&tool_calibrator&toolchanger" 2>/dev/null | python3 -c '
import json, sys
s=json.load(sys.stdin)["result"]["status"]
c=s.get("tool_calibrator", {})
t=s.get("toolchanger", {})
r=c.get("run_record", {})
print("klipper=%s idle=%s tkc=%s phase=%s elapsed=%s calibrating=%s physical=%s active=%s tc=%s/%s/%s" % (
    s.get("webhooks", {}).get("state"), s.get("idle_timeout", {}).get("state"),
    c.get("status"), c.get("phase"), r.get("elapsed_sec", r.get("duration_sec")),
    c.get("calibrating_tool"), c.get("physical_tool"), c.get("active_tool"),
    t.get("status"), t.get("tool_number"), t.get("detected_tool_number")))
' 2>/dev/null || true)
    [ -n "$summary" ] && echo "monitor[$poll]=$summary"
  fi
  poll=$((poll + 1))
  sleep 1
done

wait "$curl_pid"
curl_rc=$?
echo "=== HTTP response ==="
cat "$response"
echo "curl_rc=$curl_rc"

for _ in $(seq 1 300); do
  state=$(curl -fsS "$api/printer/objects/query?webhooks&idle_timeout&tool_calibrator" 2>/dev/null | python3 -c '
import json, sys
s=json.load(sys.stdin)["result"]["status"]
print(s.get("webhooks",{}).get("state"), s.get("idle_timeout",{}).get("state"), s.get("tool_calibrator",{}).get("status"))
' 2>/dev/null || true)
  case "$state" in
    "ready Ready RUNNING") ;;
    "ready Ready "*) break ;;
  esac
  sleep 0.5
done

echo "=== final objects before recovery ==="
curl -fsS "$api/printer/objects/query?webhooks&idle_timeout&toolhead&toolchanger&tool_calibrator&heater_bed&extruder&extruder1&extruder2&extruder3&extruder4" | python3 -m json.tool

echo "=== G-code events for full run ==="
START_TIME="$start_time" curl -fsS "$api/server/gcode_store?count=600" | START_TIME="$start_time" python3 -c '
import json, os, sys
start=float(os.environ["START_TIME"])-1.0
for item in json.load(sys.stdin)["result"]["gcode_store"]:
    if float(item.get("time", 0)) >= start:
        print("%s %s: %s" % (item.get("time"), item.get("type"), item.get("message")))
'

tc_state=$(curl -fsS "$api/printer/objects/query?toolchanger" | python3 -c '
import json, sys
t=json.load(sys.stdin)["result"]["status"]["toolchanger"]
print(t.get("status"), t.get("tool_number"), t.get("detected_tool_number"))
')
if [ "$tc_state" != "ready 0 0" ]; then
  echo "=== recovery required: $tc_state ==="
  curl -fsS -X POST --data-urlencode 'script=G28' "$api/printer/gcode/script" >/dev/null
  for _ in $(seq 1 160); do
    tc_state=$(curl -fsS "$api/printer/objects/query?webhooks&idle_timeout&toolchanger" 2>/dev/null | python3 -c '
import json, sys
s=json.load(sys.stdin)["result"]["status"]
t=s["toolchanger"]
print(s["webhooks"]["state"], s["idle_timeout"]["state"], t.get("status"), t.get("tool_number"), t.get("detected_tool_number"))
' 2>/dev/null || true)
    case "$tc_state" in "ready Ready ready "*) break ;; esac
    sleep 0.5
  done
  current_tool=$(echo "$tc_state" | awk '{print $4}')
  if [ "$current_tool" != "0" ]; then
    curl -fsS -X POST --data-urlencode 'script=T0' "$api/printer/gcode/script" >/dev/null
  fi
  for _ in $(seq 1 160); do
    tc_state=$(curl -fsS "$api/printer/objects/query?webhooks&idle_timeout&toolchanger" 2>/dev/null | python3 -c '
import json, sys
s=json.load(sys.stdin)["result"]["status"]
t=s["toolchanger"]
print(s["webhooks"]["state"], s["idle_timeout"]["state"], t.get("status"), t.get("tool_number"), t.get("detected_tool_number"))
' 2>/dev/null || true)
    [ "$tc_state" = "ready Ready ready 0 0" ] && break
    sleep 0.5
  done
  echo "recovery_final=$tc_state"
else
  echo "recovery_required=no"
fi

rm -f -- "$response"
