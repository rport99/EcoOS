#!/bin/bash
for f in ~/Desktop/*.desktop; do
    [ -f "$f" ] || continue  # Skip if no .desktop files exist
    chmod +x "$f"
    gio set -t string "$f" metadata::xfce-exe-checksum "$(sha256sum "$f" | awk '{print $1}')"
done


#rm -f "$HOME/Desktop/calamares.desktop" || true
