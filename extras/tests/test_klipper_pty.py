"""Exercise the installed GCodeIO class with isolated PTYs, never hardware.

On Linux, optionally set VORON_GCODE_SOURCE to an already patched runtime copy
and VORON_GCODE_BASELINE to its unmodified backup. Windows runs structural tests;
the real nonblocking PTY tests must also pass on Linux before deployment.
"""
import ast
import collections
import contextlib
import logging
import os
from pathlib import Path
import re
import select
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
BASELINE = Path(os.environ.get(
    "VORON_GCODE_BASELINE",
    str(ROOT / "extras/backups/pre-startup-response-20261009-213009/gcode.py")))
PATCH = ROOT / "config/scripts/patches/klipper-pty-client-gate.patch"


def patch_context():
    lines = PATCH.read_text().splitlines(keepends=True)[3:]
    before = "".join(line[1:] for line in lines if line[0] in " -")
    after = "".join(line[1:] for line in lines if line[0] in " +")
    return before, after


def sources():
    original = BASELINE.read_text()
    before, after = patch_context()
    if "VORON_GCODE_SOURCE" in os.environ:
        changed = Path(os.environ["VORON_GCODE_SOURCE"]).read_text()
    else:
        if original.count(before) != 1:
            raise AssertionError("Patch context is not unique in baseline")
        changed = original.replace(before, after, 1)
    return original, changed


def load_io(source):
    node = next(node for node in ast.parse(source).body
                if isinstance(node, ast.ClassDef) and node.name == "GCodeIO")
    namespace = dict(os=os, logging=logging, collections=collections, re=re)
    exec(compile(ast.Module(body=[node], type_ignores=[]), "GCodeIO", "exec"),
         namespace)
    return namespace["GCodeIO"]


class FakeGcode:
    def __init__(self):
        self.handlers = []
        self.api_output = []
        self.commands = []
        self.register_output_handler(self.api_output.append)

    def get_mutex(self):
        return contextlib.nullcontext()

    def register_output_handler(self, handler):
        self.handlers.append(handler)

    def respond(self, message):
        for handler in self.handlers:
            handler(message)

    def _process_commands(self, commands):
        self.commands.extend(commands)
        for command in commands:
            if command.strip() == "M115":
                self.respond("FIRMWARE_NAME:isolated-fixture")
                self.respond("ok")


class FakePrinter:
    def __init__(self, fd, fileinput=False):
        self.args = dict(gcode_fd=fd)
        if fileinput:
            self.args["debuginput"] = True
        self.gcode = FakeGcode()
        self.reactor = mock.Mock()
        self.events = {}

    def lookup_object(self, name):
        assert name == "gcode"
        return self.gcode

    def get_start_args(self):
        return self.args

    def get_reactor(self):
        return self.reactor

    def register_event_handler(self, event, callback):
        self.events[event] = callback


@contextlib.contextmanager
def isolated_pty():
    import pty
    import tty
    master, slave = pty.openpty()
    try:
        tty.setraw(slave)
        os.set_blocking(master, False)
        os.set_blocking(slave, False)
        yield master, slave
    finally:
        os.close(master)
        os.close(slave)


class PatchStructureTests(unittest.TestCase):
    def test_patch_only_changes_initial_output_gate_and_comments(self):
        original, changed = sources()
        before, after = patch_context()
        self.assertEqual(original.replace(before, after, 1), changed)
        self.assertEqual(load_io(changed)(FakePrinter(-1)).pipe_is_active, False)

    def test_command_processing_error_handler_and_debuginput_unchanged(self):
        original, changed = sources()
        old_node = ast.parse(original)
        new_node = ast.parse(changed)
        old_class = next(n for n in old_node.body
                         if isinstance(n, ast.ClassDef) and n.name == "GCodeIO")
        new_class = next(n for n in new_node.body
                         if isinstance(n, ast.ClassDef) and n.name == "GCodeIO")
        for name in ("_process_data", "_respond_raw", "_handle_ready"):
            old_method = next(n for n in old_class.body if getattr(n, "name", None) == name)
            new_method = next(n for n in new_class.body if getattr(n, "name", None) == name)
            self.assertEqual(ast.dump(old_method), ast.dump(new_method))
        printer = FakePrinter(-1, fileinput=True)
        io = load_io(changed)(printer)
        self.assertEqual(len(printer.gcode.handlers), 1)
        printer.reactor.register_fd.assert_not_called()
        io._handle_ready()
        printer.reactor.register_fd.assert_called_once()


@unittest.skipUnless(os.name == "posix", "Requires a real Linux/POSIX PTY")
class RealPtyTests(unittest.TestCase):
    def setUp(self):
        original, changed = sources()
        self.baseline_io = load_io(original)
        self.patched_io = load_io(changed)

    def test_baseline_reproduces_unread_startup_buffer_error(self):
        with isolated_pty() as (master, slave):
            printer = FakePrinter(master)
            io = self.baseline_io(printer)
            with mock.patch.object(logging, "exception") as error:
                for _ in range(3000):
                    printer.gcode.respond("startup plugin message " + "x" * 128)
                error.assert_called_once_with("Write g-code response")
            self.assertFalse(io.pipe_is_active)

    def test_unread_startup_and_repeated_restart_keep_api_output(self):
        with isolated_pty() as (master, slave):
            with mock.patch.object(logging, "exception") as error:
                with mock.patch.object(os, "write", wraps=os.write) as write:
                    for _ in range(4):
                        printer = FakePrinter(master)
                        io = self.patched_io(printer)
                        for _ in range(3000):
                            printer.gcode.respond("startup plugin message " + "x" * 128)
                        self.assertEqual(len(printer.gcode.api_output), 3000)
                        self.assertFalse(io.pipe_is_active)
                    write.assert_not_called()
                error.assert_not_called()
            self.assertEqual(select.select([slave], [], [], 0)[0], [])

    def test_legacy_client_first_command_enables_response(self):
        with isolated_pty() as (master, slave):
            printer = FakePrinter(master)
            io = self.patched_io(printer)
            os.write(slave, b"M115\n")
            self.assertEqual(select.select([master], [], [], 1)[0], [master])
            io._process_data(1.0)
            self.assertTrue(io.pipe_is_active)
            self.assertEqual(printer.gcode.commands, ["M115"])
            self.assertEqual(select.select([slave], [], [], 1)[0], [slave])
            self.assertEqual(os.read(slave, 4096),
                             b"FIRMWARE_NAME:isolated-fixture\nok\n")
            self.assertEqual(printer.gcode.api_output,
                             ["FIRMWARE_NAME:isolated-fixture", "ok"])

    def test_io_error_still_disables_pipe_and_next_command_recovers(self):
        with isolated_pty() as (master, slave):
            printer = FakePrinter(master)
            io = self.patched_io(printer)
            os.write(slave, b"M115\n")
            select.select([master], [], [], 1)
            io._process_data(1.0)
            select.select([slave], [], [], 1)
            os.read(slave, 4096)
            with mock.patch.object(os, "write", side_effect=BlockingIOError(11, "full")):
                with mock.patch.object(logging, "exception") as error:
                    io._respond_raw("later output")
                    error.assert_called_once_with("Write g-code response")
            self.assertFalse(io.pipe_is_active)
            os.write(slave, b"M115\n")
            select.select([master], [], [], 1)
            io._process_data(2.0)
            self.assertTrue(io.pipe_is_active)
            self.assertEqual(select.select([slave], [], [], 1)[0], [slave])
            self.assertIn(b"FIRMWARE_NAME:", os.read(slave, 4096))


if __name__ == "__main__":
    unittest.main(verbosity=2)
