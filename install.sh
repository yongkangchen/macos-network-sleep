#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

if ! xcode-select -p >/dev/null 2>&1; then
  echo "The Xcode Command Line Tools are not installed. Run: xcode-select --install"
  exit 1
fi

dir="$HOME/Library/Application Support/network-sleep"
mkdir -p "$dir" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
install -m 755 sleep.sh unlock.sh "$dir/"
install -m 644 network-sleep-listener.py "$dir/"

plist="$HOME/Library/LaunchAgents/local.network-sleep.plist"
cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>local.network-sleep</string>
	<key>ProgramArguments</key>
	<array>
		<string>/usr/bin/python3</string>
		<string>$dir/network-sleep-listener.py</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>KeepAlive</key>
	<true/>
	<key>StandardErrorPath</key>
	<string>$HOME/Library/Logs/network-sleep.err</string>
</dict>
</plist>
EOF

domain="gui/$(id -u)"
if launchctl print "$domain/local.network-sleep" >/dev/null 2>&1; then
  launchctl bootout "$domain/local.network-sleep" || true
  sleep 1
fi
launchctl bootstrap "$domain" "$plist"
echo "Installed. Log file: ~/Library/Logs/network-sleep.log"
