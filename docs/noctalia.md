# Noctalia Dock 交互说明

**简体中文** | [English](noctalia.en.md)

## 两个独立问题

1. 脚本负责把可见窗口、托盘实例、冷启动三种情况衔接起来。
2. Noctalia Dock 在没有可见窗口时建立待聚焦目标，可能在脚本唤醒完成后再补发聚焦。

不能因为兼容补丁写在 Noctalia，就把 QQ 原始单实例问题归因于 Noctalia；也不能在没有具体规范条款与证据时断言 QQ 或打包方违反规范。

## 实测与源码证据

Noctalia v5.4.0 的 `activateOrLaunchItem` 在没有窗口时建立最长 8 秒的 PendingLaunchFocus。`tryFulfillPendingLaunchFocus` 找到窗口后会先清除该状态，再调用激活接口。这不是持续 8 秒反复聚焦。

在 Niri 后端，该操作最终发送 `FocusWindow`。现场跟踪曾记录单实例脚本退出约 1.2 秒后，Noctalia 主进程补发该命令。源码中的跨屏移动分支只针对 Hyprland，不在本次 Niri 路径执行。

直接从 QQ 托盘打开没有复现；从原 Dock 入口打开可复现。独立入口与 QQ 窗口不再归组后，用户确认问题消失。微信后续独立入口也通过相同现象验收。不能据此推断所有版本或其他 Dock 都存在同样问题。

仅修改 desktop ID 和 StartupWMClass，而仍将入口显示名设置为 QQ，不足以确保身份分离：Noctalia 也会用显示名称匹配运行应用。

## 单图标方案

本地曾基于 v5.4.0 验证一个通用候选补丁：目标已获得焦点时不再补发聚焦；等待期间焦点转到其他窗口时取消待聚焦。完整构建和两组针对性测试通过，用户确认 QQ 单图标场景不再复现。随后按用户要求恢复发行版，继续使用独立入口。

此候选尚未完成广泛回归或上游评审，本仓库不分发编译后的 Noctalia 或自动修改其服务。仅通过焦点状态判断无法完全区分用户输入与应用自行激活，因此不将候选视为普遍正确的最终方案。

删除输入法参数未解决本次问题；XWayland 对照因无可见窗口而未能完成。不要将它们描述为已验证解决方法。

## 上游参考

- [Dock v5.4.0](https://github.com/noctalia-dev/noctalia/blob/v5.4.0/src/shell/dock/dock.cpp)
- [应用身份匹配 v5.4.0](https://github.com/noctalia-dev/noctalia/blob/v5.4.0/src/system/app_identity.cpp)
- [Niri 聚焦后端 v5.4.0](https://github.com/noctalia-dev/noctalia/blob/v5.4.0/src/compositors/niri/niri_workspace_backend.cpp)
