# Network off during sleep, on at unlock (macOS)

This tool is a small launch agent for macOS. It does these things:

- When the Mac goes to sleep, it turns off all network services that have a network interface. Examples are Wi-Fi, Ethernet, and Thunderbolt Bridge.
- When you unlock the screen, it turns on the services that it turned off.
- When it starts, for example after a restart and a login, it also turns on the services that it turned off.

It does nothing at other times.

Tested on macOS 27.2.1 on a MacBook with Apple silicon.

## Why use it

On macOS 27.2, some Macs have system-wide DNS failures after sleep. The reported Macs use network extensions. Apps cannot resolve host names, but `ping 8.8.8.8` and `nslookup` continue to work.

During sleep, the Mac wakes for short periods (DarkWake) and uses the network. With this tool, the Mac has no network connection for the full sleep period.

This tool is a workaround. It does not fix the cause of the DNS failures. There is no proof yet that it prevents them.

## How it works

The tool uses `networksetup -setnetworkserviceenabled`.

- At sleep, it turns off each network service that is on and has a network interface. It adds the name of each service to the file `disabled-services`.
- At unlock, it turns on each service in `disabled-services`. Then it deletes the file.
- It does not change VPN services, because they do not have a network interface.
- A service that you turned off yourself stays off, because it is not in `disabled-services`.

## Requirements

- The Xcode Command Line Tools are installed, because the tool uses `/usr/bin/python3`. To install them, run `xcode-select --install`.
- An administrator password is not necessary. `networksetup` has a system entitlement that permits it to change network services.

## Install

```bash
./install.sh
```

The script does these steps:

1. It copies `network-sleep-listener.py`, `sleep.sh`, and `unlock.sh` to `~/Library/Application Support/network-sleep/`.
2. It creates the launch agent `~/Library/LaunchAgents/local.network-sleep.plist` and starts it.

macOS can show the notification "Background Items Added". Keep this item on in System Settings > General > Login Items & Extensions. If you turn it off, the tool does not start after a restart.

## Make sure that it works

```bash
tail -n 5 ~/Library/Logs/network-sleep.log
```

After the installation, the log shows `listener started`. Then do these steps:

1. Close the lid.
2. Open the lid.
3. Unlock the Mac.

The log then shows lines like these:

```text
2026-11-16 10:00:01 sleep: off [USB 10/100/1000 LAN, Thunderbolt Bridge, Wi-Fi]
2026-11-16 10:00:40 unlock event
2026-11-16 10:00:41 unlock: on [USB 10/100/1000 LAN, Thunderbolt Bridge, Wi-Fi]
```

## Turn the network on by hand

If the network stays off, run this command:

```bash
"$HOME/Library/Application Support/network-sleep/unlock.sh" manual
```

## Limitations

- During sleep, the Mac has no network connection. Mail, messages, Find My, and remote access to the Mac do not work until you unlock the Mac.
- If the Mac restarts while the network is off, the network stays off until you log in.

## Uninstall

```bash
./uninstall.sh
```

The script stops the launch agent. Then it turns on the services that the tool turned off, and removes the installed files. It keeps the log file.

## Files

| File | Function |
| --- | --- |
| `network-sleep-listener.py` | Receives the sleep and unlock events from macOS. Runs `sleep.sh` at sleep. Runs `unlock.sh` at unlock and when it starts. |
| `sleep.sh` | Turns off the network services and records their names. |
| `unlock.sh` | Turns on the recorded network services. |
| `install.sh` | Installs and starts the launch agent. |
| `uninstall.sh` | Stops the launch agent, turns on the network services, and removes the installed files. |
