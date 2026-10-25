#!/bin/bash
cd ~/.hermes/reference || exit 1
repos="
printer-buddy https://github.com/sterling5241/printer-buddy
print-buddy-ui https://github.com/sterling5241/print-buddy-ui
print-buddy-notify https://github.com/sterling5241/print-buddy-notify
print-buddy-timelapse https://github.com/sterling5241/print-buddy-timelapse
print-buddy-streamer https://github.com/sterling5241/print-buddy-streamer
printer-buddy-docs https://github.com/sterling5241/printer-buddy-docs
mainsail https://github.com/mainsail-crew/mainsail
fluidd https://github.com/fluidd-core/fluidd
crowsnest https://github.com/mainsail-crew/crowsnest
moonraker https://github.com/Arksine/moonraker
klipper https://github.com/Klipper3d/klipper
kalico https://github.com/KalicoCrew/kalico
KlipperScreen https://github.com/KlipperScreen/KlipperScreen
moonraker-timelapse https://github.com/mainsail-crew/moonraker-timelapse
Spoolman https://github.com/Donkie/Spoolman
obico-server https://github.com/TheSpaghettiDetective/obico-server
moonraker-obico https://github.com/TheSpaghettiDetective/moonraker-obico
grumpyscreen https://github.com/pellcorp/grumpyscreen
"
changed=0
while read -r name url; do
  [ -z "$name" ] && continue
  if [ ! -d "$name/.git" ]; then
    git clone -q "$url" "$name" && echo "$name: added" || echo "$name: clone failed"
    changed=1
    continue
  fi
  old=$(git -C "$name" rev-parse HEAD)
  git -C "$name" pull -q --ff-only || { echo "$name: update failed"; changed=1; continue; }
  n=$(git -C "$name" rev-list --count "$old"..HEAD)
  [ "$n" -gt 0 ] && echo "$name: $n new commits" && changed=1
done <<< "$repos"
[ "$changed" = 0 ] && echo "no changes"
