#!/bin/bash
state="$(dirname "$0")/disabled-services"
names=""
while IFS= read -r service; do
  if /usr/sbin/networksetup -setnetworkserviceenabled "$service" off; then
    echo "$service" >> "$state"
    names="$names${names:+, }$service"
  fi
done < <(/usr/sbin/networksetup -listnetworkserviceorder | awk '
  /^\([0-9]+\) / { name = substr($0, index($0, ") ") + 2); next }
  /^\(Hardware Port: / { if (name != "" && $0 !~ /Device: \)$/) print name; name = "" }
')
echo "$(date '+%F %T') sleep: off [$names]" >> "$HOME/Library/Logs/network-sleep.log"
