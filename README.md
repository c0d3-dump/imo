# imo

flatpak-builder build-dir io.github.c0d3dump.vectorchat.yml --user --install --force-clean

flatpak run io.github.c0d3dump.vectorchat

<!-- custom distribution (no flathub) -->
flatpak build-export repo build-dir

flatpak build-bundle repo vectorchat.flatpak io.github.c0d3dump.vectorchat

flatpak install vectorchat.flatpak
