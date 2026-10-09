#!/usr/bin/env bash
set -euo pipefail

# Sharing: use absolute paths for a different printer_data layout. Point the
# Moonraker URL at the SAME printer; the idle check must not query another host.
CONFIG_DIR="${VORON_CONFIG_DIR:-${HOME}/printer_data/config}"
BACKUP_ROOT="${VORON_BACKUP_ROOT:-${HOME}/printer_data/config_backups}"
MOONRAKER_URL="${VORON_MOONRAKER_URL:-http://127.0.0.1:7125}"
DRY_RUN="${VORON_DEPLOY_DRY_RUN:-0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CONFIG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TOOL_CRASH_SOURCE="${HOME}/klipper/klippy/extras/tool_crash.py"
TOOL_CRASH_PATCH="${SCRIPT_DIR}/patches/tool_crash-active-tool-validation.patch"
TOOL_CRASH_PATCH_MARKER="Every tool detection pin is registered with this same callback"
TOOL_CRASH_PATCH_NEEDED=0
KTC_READONLY_DIR="${CONFIG_DIR}/toolchanger/readonly-configs"
KTC_READONLY_FILES=(
  "calibrate-offsets.cfg"
  "crash-detection.cfg"
  "homing.cfg"
  "toolchanger-include.cfg"
  "toolchanger-macros.cfg"
  "toolchanger.cfg"
)

if [[ ! -f "${SOURCE_CONFIG_DIR}/printer.cfg" ]]; then
  echo "ERROR: printer.cfg was not found in ${SOURCE_CONFIG_DIR}" >&2
  exit 1
fi

if [[ "${DRY_RUN}" != 0 && "${DRY_RUN}" != 1 ]]; then
  echo "ERROR: VORON_DEPLOY_DRY_RUN must be 0 or 1." >&2
  exit 1
fi
CONFIG_DIR="$(realpath -m "${CONFIG_DIR}")"
BACKUP_ROOT="$(realpath -m "${BACKUP_ROOT}")"
if [[ "${CONFIG_DIR}" == / || "${CONFIG_DIR}" == "${HOME}" ||
      "${CONFIG_DIR}" == "${SOURCE_CONFIG_DIR}" ||
      "${BACKUP_ROOT}" == "${CONFIG_DIR}" ||
      "${BACKUP_ROOT}" == "${CONFIG_DIR}/"* ]]; then
  echo "ERROR: unsafe destination or backup path." >&2
  exit 1
fi
KTC_READONLY_DIR="${CONFIG_DIR}/toolchanger/readonly-configs"

# Fail before backup, rsync, or runtime patching if printer state cannot be
# verified. No G-code is sent. Recheck immediately before the first write.
check_printer_idle() {
  python3 - "${MOONRAKER_URL}" <<'PY'
import json, sys, urllib.request
url = sys.argv[1].rstrip('/') + '/printer/objects/query?print_stats&pause_resume&toolchanger&idle_timeout&gcode_macro%20_PRINT_STATE&gcode_macro%20_DRYER_STATUS&gcode_macro%20_TOOL_HEATUP_VARS'
try:
    with urllib.request.urlopen(url, timeout=5) as response:
        state = json.load(response)['result']['status']
    required = ('print_stats', 'pause_resume', 'toolchanger', 'idle_timeout')
    if any(name not in state for name in required):
        raise ValueError('required printer state is unavailable')
    if state['print_stats'].get('state') not in ('standby', 'complete', 'cancelled', 'error', 'printing', 'paused'):
        raise ValueError('print state is unknown')
    if not isinstance(state['pause_resume'].get('is_paused'), bool):
        raise ValueError('pause state is unknown')
    if state['idle_timeout'].get('state') not in ('Idle', 'Ready', 'Printing'):
        raise ValueError('motion/idle state is unknown')
    if state['toolchanger'].get('status') not in ('uninitialized', 'initializing', 'ready', 'changing', 'error'):
        raise ValueError('toolchanger state is unknown')
    busy = (state['print_stats'].get('state') in ('printing', 'paused')
            or state['pause_resume']['is_paused']
            or state['idle_timeout'].get('state') == 'Printing'
            or state['toolchanger'].get('status') in ('changing', 'initializing')
            or state.get('gcode_macro _PRINT_STATE', {}).get('state') in ('starting', 'printing', 'paused', 'drying')
            or state.get('gcode_macro _DRYER_STATUS', {}).get('is_drying', 0)
            or state.get('gcode_macro _TOOL_HEATUP_VARS', {}).get('is_running', 0))
    if busy:
        raise ValueError('printer is moving, printing, paused, changing tools, drying, or benchmarking')
except Exception as error:
    sys.exit('ERROR: deployment requires a verified idle printer: ' + str(error))
PY
}
check_printer_idle

# KTC-Easy is the sole owner of readonly-configs. All-Config deploys only the
# user-owned toolchanger-config.cfg and tools/T*.cfg files. Refuse deployment
# when the official installer-managed links are missing or have broken targets.
KTC_INVALID_LINKS=()
for file in "${KTC_READONLY_FILES[@]}"; do
  path="${KTC_READONLY_DIR}/${file}"
  if [[ ! -L "${path}" || ! -e "${path}" ]]; then
    KTC_INVALID_LINKS+=("${path}")
  fi
done
if (( ${#KTC_INVALID_LINKS[@]} )); then
  echo "ERROR: KTC-Easy readonly links are missing, not symlinks, or broken:" >&2
  printf '  - %s\n' "${KTC_INVALID_LINKS[@]}" >&2
  echo "Run bash ~/klipper-toolchanger-easy/install.sh while the printer is idle," >&2
  echo "then retry this deployment. No configuration was changed." >&2
  exit 1
fi

# Preflight the machine-local tool_crash runtime before deploying config. The
# upstream plugin is an independent checkout/copy, so All-Config stores only a
# minimal downstream patch and reapplies it after a future upstream reinstall.
if [[ ! -f "${TOOL_CRASH_PATCH}" ]]; then
  echo "ERROR: reviewed tool_crash patch is missing; no configuration was changed." >&2
  exit 1
fi
if [[ -f "${TOOL_CRASH_PATCH}" ]]; then
  if [[ ! -f "${TOOL_CRASH_SOURCE}" ]]; then
    echo "ERROR: tool_crash.py is required by this payload; install the runtime first." >&2
    exit 1
  elif grep -Fq "${TOOL_CRASH_PATCH_MARKER}" "${TOOL_CRASH_SOURCE}"; then
    echo "tool_crash active-tool validation patch is already installed."
  elif patch --dry-run --fuzz=0 --forward --batch \
      -d "$(dirname "${TOOL_CRASH_SOURCE}")" -p1 \
      < "${TOOL_CRASH_PATCH}" >/dev/null; then
    TOOL_CRASH_PATCH_NEEDED=1
  else
    echo "ERROR: installed tool_crash.py does not match the reviewed upstream source." >&2
    echo "Refusing to deploy configuration without a valid crash-detector patch." >&2
    exit 1
  fi
fi

RSYNC_MODE=()
if [[ "${DRY_RUN}" == 1 ]]; then
  RSYNC_MODE+=(--dry-run)
  echo "Dry run: no config, backup, or runtime files will be written."
else
  check_printer_idle
  mkdir -p "${BACKUP_ROOT}"
  BACKUP_DIR="$(mktemp -d "${BACKUP_ROOT}/config-install-$(date +%Y%m%d-%H%M%S)-XXXXXX")"
  mkdir -p "${CONFIG_DIR}"
  if [[ -d "${CONFIG_DIR}" ]]; then
    rsync -a "${CONFIG_DIR}/" "${BACKUP_DIR}/"
  fi
fi

# Deploy only repository-owned configuration. On-printer backups, calibration
# state/results, ShakeTune output, downloaded snapshots, and printer-local
# files remain untouched. KTC-Easy owns readonly-configs and external Git
# runtimes live outside CONFIG_DIR.
rsync -a "${RSYNC_MODE[@]}" --itemize-changes \
  --exclude ".codex-backups/" \
  --exclude ".moonraker.conf.bkp" \
  --exclude "Generated-Data/" \
  --exclude "ShakeTune_results/" \
  --exclude "Nhat-ky-chinh-sua/" \
  --exclude "config-*.zip" \
  --exclude "moonraker.conf.pre-*" \
  --exclude "toolchanger/readonly-configs/" \
  --exclude "README.md" \
  --exclude "*.md" \
  "${SOURCE_CONFIG_DIR}/" "${CONFIG_DIR}/"

# Preserve destination-only files and every existing backup. Removing retired
# includes/configuration is a separate reviewed migration, never rsync --delete.

if (( TOOL_CRASH_PATCH_NEEDED )) && [[ "${DRY_RUN}" == 0 ]]; then
  mkdir -p "${BACKUP_DIR}/runtime"
  cp -a "${TOOL_CRASH_SOURCE}" "${BACKUP_DIR}/runtime/tool_crash.py"
  patch --fuzz=0 --forward --batch \
    -d "$(dirname "${TOOL_CRASH_SOURCE}")" -p1 \
    < "${TOOL_CRASH_PATCH}" >/dev/null
  echo "Installed tool_crash active-tool validation patch."
fi


if [[ "${DRY_RUN}" == 1 ]]; then
  echo "Dry run complete. Runtime patch required: ${TOOL_CRASH_PATCH_NEEDED}"
else
  echo "Installed configuration from ${SOURCE_CONFIG_DIR}"
  echo "Backup: ${BACKUP_DIR}"
fi
echo "KTC-Easy readonly symlinks were verified and preserved."
echo "Axiscope is externally managed and was not modified by this deployment."
echo "Review changes, then restart Moonraker and Klipper only while the printer is idle."
