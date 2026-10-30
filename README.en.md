# Dock Tray Activate

[简体中文](README.md) | **English**

An explicit Dock launcher for applications that keep running in the system tray after their windows are closed.

```text
Visible window exists → Focus the existing window
Matching tray exists  → Activate the tray instance
App is not running    → Run the native launch command
```

This is a small **Niri + StatusNotifierItem integration tool**, with profiles for Flatpak QQ and WeChat. It is not a universal single-instance manager for every desktop or application.

## Requirements and usage

Requires Python 3, Niri, systemd's `busctl`, and the corresponding Flatpak application. No pip dependencies, sudo, or persistent background service are required.

```bash
python3 dock-activate.py --dry-run qq
python3 dock-activate.py qq
python3 dock-activate.py wechat
```

`--dry-run` reports the selected action without focusing windows or launching applications.

## Installation and removal

```bash
python3 install.py install
# Or install only one launcher:
# python3 install.py install --apps qq
```

Installs to `$XDG_DATA_HOME/dock-tray-activate` (default: `~/.local/share/dock-tray-activate`) and adds **QQ Tray Wake** and **WeChat Tray Wake** to the application menu. Pin the desired launcher to your Dock manually. The installer does not replace existing launchers or change Dock settings, and refuses to overwrite existing files.

```bash
python3 install.py uninstall
```

Uninstallation deletes only files whose hashes still match the installed versions, preserving manually modified files. Remove the corresponding Dock pins manually. The installer does not change other versions previously deployed on your machine.

## Noctalia: read this first

In the tested environment, the stock Noctalia Dock could focus a window again after tray activation, overriding the user's subsequent switch to another application. This tool uses a launcher identity distinct from the running window to avoid that matching path.

**The tradeoff is that two icons may appear while the application is running.** Restoring the application's original display name or window matching identity may reintroduce the issue. Installing this tool does not fix Noctalia itself; compiling Noctalia is not required to use the separate launcher.

See the [Noctalia compatibility notes](docs/noctalia.en.md) for the single-icon approach and the limits of the evidence.

## Scope and limitations

- The separate-launcher and tray-activation combination was tested for QQ and WeChat in one personal environment with Niri 26.04, Noctalia 5.4.0, and native Wayland. The user confirmed that the original focus-stealing symptom disappeared. Other desktops and versions have not been verified.
- Applications such as Steam that already support native reactivation generally do not need this tool. Input methods, hardware indicators, and ordinary applications without close-to-tray behavior are outside its scope.
- Only Niri window focusing is implemented. Tray detection can still be attempted without window IPC, but support for other desktops is not promised.
- With multiple windows, the focused window takes priority, followed by the most recently focused window. There is no window picker.
- URI or file arguments are passed directly to the native application to preserve opening behavior. This path does not guarantee duplicate prevention. QQ retains Flatpak file-forwarding arguments.
- Argument-free calls are serialized with a file lock, but strict single-instance behavior is not guaranteed while a cold launch has not yet registered its process or tray item.
- If an identified background instance cannot be activated, the tool returns exit code 2 rather than blindly launching a duplicate. It does not terminate applications or restart services automatically.
- Tray ownership is identified through the D-Bus owner's Flatpak cgroup or an explicitly configured executable. Use trusted profiles only; `profiles.json` contains executable launch commands.

## Testing and development

```bash
python3 test_activate.py
python3 -m py_compile dock-activate.py install.py
```

`profiles.json` describes application differences: window app IDs, Flatpak IDs or executable paths, and launch commands. Before declaring support for another application, verify window focusing, tray activation, cold launches, repeated clicks, and argument forwarding.

## License

MIT. This project is not affiliated with Tencent, Flathub, Niri, or Noctalia.
