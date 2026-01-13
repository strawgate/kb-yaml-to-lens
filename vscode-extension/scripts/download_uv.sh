#!/usr/bin/env bash
# Download uv binaries for all supported platforms from GitHub releases.
# The binaries are placed in bin/{platform}/uv for bundling with the extension.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$EXTENSION_ROOT/bin"

# uv version to download (pin for reproducibility)
UV_VERSION="${UV_VERSION:-0.9.18}"

# Platform configurations: platform -> (download_name, binary_name)
declare -A PLATFORMS=(
    ["linux-x64"]="uv-x86_64-unknown-linux-gnu"
    ["darwin-x64"]="uv-x86_64-apple-darwin"
    ["darwin-arm64"]="uv-aarch64-apple-darwin"
    ["win32-x64"]="uv-x86_64-pc-windows-msvc"
)

download_uv() {
    local platform="$1"
    local download_name="${PLATFORMS[$platform]}"
    local target_dir="$BIN_DIR/$platform"
    local binary_name="uv"
    local archive_ext=".tar.gz"

    # Windows uses .zip and .exe
    if [[ "$platform" == win32-* ]]; then
        archive_ext=".zip"
        binary_name="uv.exe"
    fi

    local archive_name="${download_name}${archive_ext}"
    local download_url="https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/${archive_name}"
    local temp_dir
    temp_dir="$(mktemp -d)"
    local archive_path="$temp_dir/$archive_name"

    echo "Downloading uv ${UV_VERSION} for $platform..."

    # Download the archive
    if ! curl -fsSL --retry 3 --retry-delay 2 "$download_url" -o "$archive_path"; then
        echo "Error: Failed to download $download_url"
        rm -rf "$temp_dir"
        return 1
    fi

    # Extract the binary
    mkdir -p "$target_dir"
    if [[ "$archive_ext" == ".zip" ]]; then
        # Windows zip archive
        unzip -q -o "$archive_path" -d "$temp_dir/extracted"
        # The binary is inside a directory with the same name as the archive (without extension)
        cp "$temp_dir/extracted/$binary_name" "$target_dir/$binary_name"
    else
        # Unix tar.gz archive
        tar -xzf "$archive_path" -C "$temp_dir"
        # The binary is inside a directory with the same name as the archive (without extension)
        cp "$temp_dir/${download_name}/$binary_name" "$target_dir/$binary_name"
        chmod +x "$target_dir/$binary_name"
    fi

    # Clean up
    rm -rf "$temp_dir"

    local size_kb
    size_kb=$(du -k "$target_dir/$binary_name" | cut -f1)
    echo "  ✓ $platform: $target_dir/$binary_name (${size_kb}KB)"
}

download_current_platform() {
    # Detect current platform
    local os arch platform
    os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    arch="$(uname -m)"

    case "$os" in
        msys*|mingw*|cygwin*) os="win32" ;;
        darwin*) os="darwin" ;;
        linux*) os="linux" ;;
    esac

    case "$arch" in
        x86_64|amd64) arch="x64" ;;
        aarch64|arm64) arch="arm64" ;;
    esac

    platform="${os}-${arch}"

    if [[ -z "${PLATFORMS[$platform]:-}" ]]; then
        echo "Error: Unsupported platform: $platform"
        exit 1
    fi

    download_uv "$platform"
}

main() {
    local mode="${1:-all}"

    case "$mode" in
        all)
            echo "Downloading uv ${UV_VERSION} for all platforms..."
            mkdir -p "$BIN_DIR"
            for platform in "${!PLATFORMS[@]}"; do
                download_uv "$platform"
            done
            echo ""
            echo "✓ All uv binaries downloaded successfully"
            ;;
        current)
            echo "Downloading uv ${UV_VERSION} for current platform..."
            mkdir -p "$BIN_DIR"
            download_current_platform
            echo ""
            echo "✓ uv binary downloaded for current platform"
            ;;
        *)
            echo "Usage: $0 [all|current]"
            echo "  all     - Download uv for all supported platforms (default)"
            echo "  current - Download uv for current platform only"
            exit 1
            ;;
    esac
}

main "$@"
