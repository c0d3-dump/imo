# imo

# installation steps on linux

### dependencies

- flatpak (https://flatpak.org/setup)
- ollama (https://ollama.com)
- qwen3 (ollama pull qwen3:8b)
- nomic-embed-text (ollama pull nomic-embed-text)
- gemma3 (ollama pull gemma3:4b)

### get latest app from release

[vectorchat.flatpak](https://github.com/c0d3-dump/imo/releases/download/v1.0.0/vectorchat.flatpak)

### install flatpak

```sh
flatpak install vectorchat.flatpak
```

# build from source

### build flatpak

```sh
flatpak-builder build-dir io.github.c0d3dump.vectorchat.yml --user --install --force-clean
```

# distribution

```sh
flatpak build-export repo build-dir

flatpak build-bundle repo vectorchat.flatpak io.github.c0d3dump.vectorchat
```
