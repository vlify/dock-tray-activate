#!/usr/bin/env python3
"""Install or remove opt-in launchers without changing existing desktop entries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'uninstall'])
    parser.add_argument('--apps', nargs='+', choices=['qq', 'wechat'], default=['qq', 'wechat'])
    ns = parser.parse_args()
    data = Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))
    target = data/'dock-tray-activate'
    manifest = target/'installed.json'
    if ns.action == 'uninstall':
        if not manifest.exists():
            parser.error('No installation manifest found')
        entries = json.loads(manifest.read_text())
        for name, expected in entries.items():
            path = Path(name)
            if path.is_file() and digest(path) == expected:
                path.unlink()
            elif path.exists():
                print('Preserving changed file:', path)
        manifest.unlink()
        try:
            target.rmdir()
        except OSError:
            pass
        return
    if manifest.exists():
        parser.error('Already installed; uninstall first (modified files will be preserved)')
    root = Path(__file__).resolve().parent
    files = {target/name: (root/name).read_bytes() for name in ['dock-activate.py','profiles.json']}
    for app in ns.apps:
        name = {'qq':'QQ Tray Wake','wechat':'WeChat Tray Wake'}[app]
        icon = {'qq':'com.qq.QQ','wechat':'com.tencent.WeChat'}[app]
        script = str(target/'dock-activate.py').replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')
        text = f'''[Desktop Entry]
Type=Application
Name={name}
Exec=python3 "{script}" {app} -- %U
Icon={icon}
Terminal=false
StartupNotify=false
StartupWMClass=dock-tray-{app}
Categories=Network;InstantMessaging;
'''
        files[data/'applications'/f'dock-tray-{app}.desktop'] = text.encode()
    collisions = [str(p) for p in files if p.exists() or p.is_symlink()]
    if collisions:
        parser.error('Refusing to overwrite existing files: '+', '.join(collisions))
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    manifest.write_text(json.dumps({str(p):digest(p) for p in files},indent=2)+'\n')
    print('Installed opt-in launchers. Existing Dock pins and launchers were not changed.')
    updater = shutil.which('update-desktop-database')
    if updater:
        import subprocess
        subprocess.run([updater,str(data/'applications')],check=False)


if __name__ == '__main__':
    main()
