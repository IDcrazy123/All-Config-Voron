"""Exercise the installer in a temporary filesystem with fake Moonraker/rsync.

No printer access. Set VORON_TEST_BASH to Git Bash on Windows if necessary.
The rsync stub records arguments; it does not test rsync's copying algorithm.
"""
import copy
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASH = os.environ.get('VORON_TEST_BASH', shutil.which('bash') or '')
BASE = {'print_stats': {'state': 'standby'}, 'pause_resume': {'is_paused': False},
        'toolchanger': {'status': 'ready'}, 'idle_timeout': {'state': 'Ready'},
        'gcode_macro _PRINT_STATE': {'state': 'idle'},
        'gcode_macro _DRYER_STATUS': {'is_drying': 0},
        'gcode_macro _TOOL_HEATUP_VARS': {'is_running': 0}}


class Handler(http.server.BaseHTTPRequestHandler):
    state = BASE

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({'result': {'status': self.state}}).encode())

    def log_message(self, *args):
        pass


@unittest.skipUnless(BASH, 'Bash is required')
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = self.root / 'payload'
        shutil.copytree(ROOT / 'config', self.payload)
        self.home = self.root / 'home'
        self.config = self.home / 'printer_data/config'
        links = self.config / 'toolchanger/readonly-configs'
        links.mkdir(parents=True)
        for filename in (self.payload / 'toolchanger/readonly-configs').glob('*.cfg'):
            target = links / ('target-' + filename.name)
            shutil.copyfile(filename, target)
            result = subprocess.run([BASH, '-c', 'ln -s "$1" "$2"', 'test',
                                     target.name, filename.name], cwd=links,
                                    env={**os.environ, 'MSYS': 'winsymlinks:lnk'},
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.runtime = self.home / 'klipper/klippy/extras/tool_crash.py'
        self.runtime.parent.mkdir(parents=True)
        self.runtime.write_text('# Every tool detection pin is registered with this same callback\n')
        (self.config / 'my-machine.cfg').write_text('[gcode_macro PRIVATE_MACRO]\ngcode:\n G4 P1\n')
        (self.config / 'local-notes.md').write_text('Keep me')
        self.backups = self.home / 'printer_data/config_backups'
        for n in range(7):
            old = self.backups / ('config-install-20200101-00000%d' % n)
            old.mkdir(parents=True)
            (old / 'printer.cfg').write_text('original')
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        python_exe = Path(sys.executable).as_posix().replace("'", "'\"'\"'")
        (bin_dir / 'python3').write_text("#!/bin/bash\nexec '" + python_exe + "' \"$@\"\n", newline='\n')
        self.calls = self.root / 'rsync-calls.txt'
        (bin_dir / 'rsync').write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$VORON_TEST_CALLS"\n', newline='\n')
        for p in bin_dir.iterdir():
            p.chmod(0o755)
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        Handler.state = copy.deepcopy(BASE)
        self.env = {**os.environ, 'HOME': self.home.as_posix(), 'MSYS': 'winsymlinks:lnk',
                    'VORON_TEST_BIN': bin_dir.as_posix(), 'VORON_TEST_CALLS': self.calls.as_posix(),
                    'VORON_CONFIG_DIR': self.config.as_posix(),
                    'VORON_BACKUP_ROOT': self.backups.as_posix(),
                    'VORON_MOONRAKER_URL': 'http://127.0.0.1:%d' % self.server.server_port}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.temp.cleanup()

    def run_install(self, dry=False):
        env = {**self.env, 'VORON_DEPLOY_DRY_RUN': '1' if dry else '0'}
        command = ('test_bin="$VORON_TEST_BIN"; '
                   'if command -v cygpath >/dev/null; then test_bin="$(cygpath -u "$test_bin")"; fi; '
                   'PATH="$test_bin:$PATH"; export PATH; bash "$1"')
        return subprocess.run([BASH, '-c', command,
                               'test', (self.payload / 'scripts/install.sh').as_posix()],
                              env=env, capture_output=True, text=True)

    def test_busy_and_missing_status_stop_before_writes(self):
        cases = [('print_stats', 'state', 'printing'), ('pause_resume', 'is_paused', True),
                 ('toolchanger', 'status', 'changing'), ('idle_timeout', 'state', 'Printing'),
                 ('gcode_macro _PRINT_STATE', 'state', 'starting'),
                 ('gcode_macro _DRYER_STATUS', 'is_drying', 1),
                 ('gcode_macro _TOOL_HEATUP_VARS', 'is_running', 1)]
        for section, key, value in cases:
            Handler.state = copy.deepcopy(BASE)
            Handler.state[section][key] = value
            result = self.run_install()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('verified idle printer', result.stderr)
            self.assertFalse(self.calls.exists())
            self.assertEqual(len(list(self.backups.iterdir())), 7)
        Handler.state = {}
        self.assertNotEqual(self.run_install().returncode, 0)
        self.assertFalse(self.calls.exists())
        for section, key in [('print_stats', 'state'), ('pause_resume', 'is_paused'),
                             ('toolchanger', 'status'), ('idle_timeout', 'state')]:
            Handler.state = copy.deepcopy(BASE)
            del Handler.state[section][key]
            result = self.run_install()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('state is unknown', result.stderr)
            self.assertFalse(self.calls.exists())

    def test_missing_runtime_refuses_payload(self):
        self.runtime.unlink()
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('tool_crash.py is required', result.stderr)
        self.assertFalse(self.calls.exists())

    def test_dry_run_preserves_files_and_backups(self):
        result = self.run_install(dry=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(self.backups.iterdir())), 7)
        calls = self.calls.read_text()
        self.assertIn('--dry-run', calls)
        self.assertNotIn('--delete', calls)
        self.assertTrue((self.config / 'my-machine.cfg').exists())
        self.assertTrue((self.config / 'local-notes.md').exists())

    def test_real_mode_keeps_old_backups_and_unique_new_paths(self):
        for _ in range(2):
            result = self.run_install()
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(self.backups.iterdir())), 9)
        self.assertNotIn('--delete', self.calls.read_text())
        self.assertTrue((self.config / 'my-machine.cfg').exists())
        self.assertTrue((self.config / 'local-notes.md').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
