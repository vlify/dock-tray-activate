# Dock Tray Activate

**简体中文** | [English](README.md)

为关闭窗口后仍驻留托盘的应用提供一个明确的 Dock 唤醒入口。

```text
已有可见窗口 → 聚焦已有窗口
已有匹配托盘 → 激活托盘实例
尚未运行     → 原生命令启动
```

当前是 **Niri + StatusNotifierItem 的小型适配工具**，附带 Flatpak QQ、微信配置。不是适用于所有桌面、所有应用的单实例管理器。

## 依赖与使用

需要 Python 3、Niri、systemd 的 `busctl`，以及相应 Flatpak 应用。无需 pip 依赖、sudo 或常驻后台服务。

```bash
python3 dock-activate.py --dry-run qq
python3 dock-activate.py qq
python3 dock-activate.py wechat
```

`--dry-run` 只报告动作，不激活窗口或启动应用。

## 安装与卸载

```bash
python3 install.py install
# 或只安装一个入口
# python3 install.py install --apps qq
```

安装到 `$XDG_DATA_HOME/dock-tray-activate`（默认 `~/.local/share/dock-tray-activate`），在应用菜单增加 **QQ Tray Wake** 和 **WeChat Tray Wake**。自行将所需入口固定到 Dock；安装器不会替换原启动器或改 Dock 设置，遇到同名文件会拒绝覆盖。

```bash
python3 install.py uninstall
```

卸载只删除与安装时哈希一致的文件，保留手工修改过的文件。请自行移除对应 Dock 固定项。安装器不会修改当前机器此前部署的其他版本。

## Noctalia：请先阅读

在实测环境中，原版 Noctalia 的 Dock 在托盘唤醒后可能额外聚焦窗口，覆盖用户刚进行的切换。本工具使用与运行窗口不同的入口身份，绕开这条匹配路径。

**代价是运行时可能显示两个图标。** 若改回应用的相同名称或窗口匹配标识，可能重新引入该问题。安装本工具不等于修复 Noctalia；无须为使用独立入口编译 Noctalia。

单图标方案及证据边界见 [Noctalia 兼容说明](docs/noctalia.md)。

## 范围与限制

- QQ、微信的独立入口托盘唤醒组合已在 Niri 26.04、Noctalia 5.4.0、原生 Wayland 的个人环境实测，用户确认原抢焦点现象消失。未验证其他桌面或所有版本。
- Steam 等已有原生唤回机制的应用通常不需要此工具。输入法、硬件指示器，以及没有关闭到托盘行为的普通应用不纳入。
- 当前只有 Niri 窗口聚焦后端。缺少窗口 IPC 时仍可尝试托盘识别，但不承诺其他桌面支持。
- 多窗口优先聚焦当前窗口，其次选择最近聚焦窗口，不提供窗口选择器。
- 带 URI／文件参数时直接转交原应用，保留打开目标语义；这条路径不承诺防多开。QQ 保留 Flatpak 文件转交参数。
- 无参数调用使用文件锁串行处理，但不保证冷启动尚未完成注册期间的严格单实例。
- 发现后台实例却无法激活时返回退出码 2，避免盲目多开；没有自动结束应用或重启服务的行为。
- 托盘归属依赖 D-Bus 所有者进程的 Flatpak cgroup 或明确配置的进程入口。只登记可信配置，不把 `profiles.json` 当作外部输入执行。

## 验证与开发

```bash
python3 test_activate.py
python3 -m py_compile dock-activate.py install.py
```

`profiles.json` 保存应用差异：窗口 app_id、Flatpak ID／进程入口、启动命令。后续应用需验证窗口聚焦、托盘唤醒、冷启动、重复点击及参数转交后再声明支持。

## 许可

MIT。此项目与腾讯、Flathub、Niri、Noctalia 无隶属关系。
