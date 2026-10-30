# Noctalia Dock interaction notes

[简体中文](noctalia.md) | **English**

## Two separate concerns

1. The script connects three states: visible windows, tray instances, and cold launches.
2. When there is no visible window, the Noctalia Dock creates a pending focus target and may issue another focus request after the script has activated the tray instance.

A compatibility patch being implemented in Noctalia does not make Noctalia responsible for QQ's original single-instance behavior. Likewise, claims that QQ or its packager violates a specification require concrete provisions and evidence.

## Observations and source evidence

In Noctalia v5.4.0, `activateOrLaunchItem` creates a `PendingLaunchFocus` with an eight-second deadline when there are no matching windows. After finding a window, `tryFulfillPendingLaunchFocus` clears this state before calling the activation interface. It does not repeatedly focus the window for eight seconds.

On the Niri backend, this operation ultimately sends `FocusWindow`. A local trace recorded Noctalia's main process sending that command about 1.2 seconds after the single-instance script exited. The source's cross-monitor move branch applies only to Hyprland, not the Niri path tested here.

Opening QQ directly from its tray icon did not reproduce the issue; using the original Dock launcher did. After the separate launcher stopped grouping with QQ's window, the user confirmed that the symptom disappeared. A separate WeChat launcher subsequently passed the same symptom check. This does not establish that all versions or other Docks have the same issue.

Changing only the desktop ID and `StartupWMClass`, while retaining QQ as the display name, does not ensure identity separation: Noctalia also uses display names to resolve running applications.

## Single-icon approach

A generic candidate patch based on v5.4.0 was tested locally: stop pending activation when the target already has focus, and cancel pending activation when focus changes to another window during the wait. The full build and two targeted test suites passed, and the user confirmed that the QQ single-icon scenario no longer reproduced the issue. The distribution version was later restored at the user's request, retaining separate launchers.

This candidate has not undergone broad regression testing or upstream review. This repository does not distribute a compiled Noctalia or automatically modify its service. Focus state alone cannot fully distinguish user input from an application's own activation, so the candidate is not presented as a universally correct final solution.

Removing input-method flags did not resolve this incident. The XWayland comparison could not be completed because no visible window appeared. Neither should be described as a verified solution.

## Upstream references

- [Dock v5.4.0](https://github.com/noctalia-dev/noctalia/blob/v5.4.0/src/shell/dock/dock.cpp)
- [Application identity matching v5.4.0](https://github.com/noctalia-dev/noctalia/blob/v5.4.0/src/system/app_identity.cpp)
- [Niri focus backend v5.4.0](https://github.com/noctalia-dev/noctalia/blob/v5.4.0/src/compositors/niri/niri_workspace_backend.cpp)
