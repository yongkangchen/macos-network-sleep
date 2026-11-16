#!/bin/bash
set -uo pipefail
dir="$HOME/Library/Application Support/network-sleep"
launchctl bootout "gui/$(id -u)/local.network-sleep" 2>/dev/null
if [ -f "$dir/unlock.sh" ]; then
  /bin/bash "$dir/unlock.sh" uninstall
fi
rm -rf "$dir"
rm -f "$HOME/Library/LaunchAgents/local.network-sleep.plist"
echo "Uninstalled."
