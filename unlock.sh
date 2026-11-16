#!/bin/bash
state="$(dirname "$0")/disabled-services"
[ -f "$state" ] || exit 0
names=""
while IFS= read -r service; do
  /usr/sbin/networksetup -setnetworkserviceenabled "$service" on
  names="$names${names:+, }$service"
done < <(awk '!seen[$0]++' "$state")
rm -f "$state"
echo "$(date '+%F %T') ${1:-unlock}: on [$names]" >> "$HOME/Library/Logs/network-sleep.log"
