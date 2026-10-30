#!/usr/bin/env python3
"""Focus a Niri window, activate an identified tray item, or launch an app."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def run(argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None


def window_choice(windows, app_ids):
    matches = [w for w in windows if w.get('app_id') in app_ids]
    return max(matches, key=lambda w: (w.get('is_focused', False),
               w.get('focus_timestamp', {}).get('secs', 0),
               w.get('focus_timestamp', {}).get('nanos', 0)), default=None)


def tray_target(item):
    service, slash, path = item.partition('/')
    if not slash or not re.fullmatch(r'[:A-Za-z0-9_.-]+', service):
        return None
    return service, '/' + path


def proc_matches(pid, profile):
    try:
        proc = Path('/proc') / str(int(pid))
        if proc.stat().st_uid != os.getuid():
            return False
        cgroup = (proc / 'cgroup').read_text()
        cmd = (proc / 'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace')
        return (any(app in cgroup for app in profile.get('flatpak_ids', []))
                or cmd in profile.get('executables', []))
    except (OSError, ValueError):
        return False


def activate(profile, args, dry_run=False):
    # URI/file arguments must retain the application's native open semantics.
    if args:
        return launch(profile, args, dry_run)
    result = run(['niri', 'msg', '-j', 'windows'])
    if result and result.returncode == 0:
        try:
            window = window_choice(json.loads(result.stdout), profile['app_ids'])
        except (ValueError, TypeError):
            window = None
        if window:
            command = ['niri', 'msg', 'action', 'focus-window', '--id', str(window['id'])]
            if dry_run:
                print(json.dumps({'action': 'focus', 'command': command})); return 0
            outcome = run(command)
            if outcome and outcome.returncode == 0:
                return 0
    result = run(['busctl', '--user', '--json=short', 'get-property',
                  'org.kde.StatusNotifierWatcher', '/StatusNotifierWatcher',
                  'org.kde.StatusNotifierWatcher', 'RegisteredStatusNotifierItems'])
    if result and result.returncode == 0:
        try:
            items = json.loads(result.stdout)['data']
        except (ValueError, KeyError, TypeError):
            items = []
        for item in items:
            if not isinstance(item, str):
                continue
            target = tray_target(item)
            if not target:
                continue
            service, path = target
            owner = run(['busctl', '--user', 'call', 'org.freedesktop.DBus',
                         '/org/freedesktop/DBus', 'org.freedesktop.DBus',
                         'GetConnectionUnixProcessID', 's', service])
            if not owner or owner.returncode or not owner.stdout.split() or not proc_matches(owner.stdout.split()[-1], profile):
                continue
            command = ['busctl', '--user', 'call', service, path,
                       'org.kde.StatusNotifierItem', 'Activate', 'ii', '0', '0']
            if dry_run:
                print(json.dumps({'action': 'tray', 'command': command})); return 0
            outcome = run(command)
            if outcome and outcome.returncode == 0:
                return 0
    if profile.get('guard_running'):
        for proc in Path('/proc').iterdir():
            if proc.name.isdigit() and proc_matches(proc.name, profile):
                print('App is running but cannot be activated; refusing a duplicate launch.', file=sys.stderr)
                return 2
    return launch(profile, [], dry_run)


def launch(profile, args, dry_run):
    command = profile['launch'] + args + profile.get('launch_suffix', [])
    if dry_run:
        print(json.dumps({'action': 'launch', 'command': command})); return 0
    os.execvp(command[0], command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--profiles', type=Path, default=Path(__file__).resolve().with_name('profiles.json'))
    parser.add_argument('app')
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    ns = parser.parse_args()
    profiles = json.loads(ns.profiles.read_text())
    if ns.app not in profiles:
        parser.error('unknown app profile')
    # Serialize clicks; exec inherits no lock fd. Application startup may outlive
    # this lock, so this alone does not guarantee single-instance cold launches.
    runtime = os.environ.get('XDG_RUNTIME_DIR')
    if not runtime:
        parser.error('XDG_RUNTIME_DIR is required')
    if ns.dry_run:
        args = ns.arguments[1:] if ns.arguments[:1] == ['--'] else ns.arguments
        return activate(profiles[ns.app], args, True)
    with (Path(runtime) / ('dock-activate-' + re.sub(r'[^a-zA-Z0-9_-]', '_', ns.app) + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        args = ns.arguments[1:] if ns.arguments[:1] == ['--'] else ns.arguments
        return activate(profiles[ns.app], args, ns.dry_run)


if __name__ == '__main__':
    sys.exit(main())
