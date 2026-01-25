#!/usr/bin/env bash
# Download uv binaries for all supported platforms from GitHub releases.
# The binaries are placed in bin/{platform}/uv for bundling with the extension.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$EXTENSION_ROOT/bin"

# uv version to download (pin for reproducibility)
UV_VERSION="${UV_VERSION:-0.9.26}"

# Map platform to uv release name (compatible with bash 3.x on macOS)
get_uv_target() {
    local platform="$1"
    case "$platform" in
        linux-x64)    echo "uv-x86_64-unknown-linux-gnu" ;;
        darwin-x64)   echo "uv-x86_64-apple-darwin" ;;
        darwin-arm64) echo "uv-aarch64-apple-darwin" ;;
        win32-x64)    echo "uv-x86_64-pc-windows-msvc" ;;
        *) return 1 ;;
    esac
}

download_uv() {
    local platform="$1"
    local download_name
    download_name="$(get_uv_target "$platform")" || {
        echo "Error: Unknown platform: $platform"
        return 1
    }

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
        # Windows zip archive - binary is at root level
        unzip -q -o "$archive_path" -d "$temp_dir/extracted"
        cp "$temp_dir/extracted/$binary_name" "$target_dir/$binary_name"
    else
        # Unix tar.gz archive - binary is in subdirectory
        tar -xzf "$archive_path" -C "$temp_dir"
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
    local os arch platform
    os="$(uname -s)"
    arch="$(uname -m)"

    case "$os" in
        MSYS*|MINGW*|CYGWIN*) os="win32" ;;
        Darwin) os="darwin" ;;
        Linux) os="linux" ;;
        *) echo "Error: Unsupported OS: $os"; exit 1 ;;
    esac

    case "$arch" in
        x86_64|amd64) arch="x64" ;;
        aarch64|arm64) arch="arm64" ;;
        *) echo "Error: Unsupported architecture: $arch"; exit 1 ;;
    esac

    platform="${os}-${arch}"

    # Validate platform is supported
    if ! get_uv_target "$platform" > /dev/null 2>&1; then
        echo "Error: Unsupported platform: $platform"
        exit 1
    fi

    download_uv "$platform"
}

download_all_platforms() {
    local platforms="linux-x64 darwin-x64 darwin-arm64 win32-x64"
    for platform in $platforms; do
        download_uv "$platform"
    done
}

main() {
    local mode="${1:-all}"

    mkdir -p "$BIN_DIR"

    case "$mode" in
        all)
            echo "Downloading uv ${UV_VERSION} for all platforms..."
            download_all_platforms
            echo ""
            echo "✓ All uv binaries downloaded successfully"
            ;;
        current)
            echo "Downloading uv ${UV_VERSION} for current platform..."
            download_current_platform
            echo ""
            echo "✓ uv binary downloaded for current platform"
            ;;
        linux-x64|darwin-x64|darwin-arm64|win32-x64)
            echo "Downloading uv ${UV_VERSION} for $mode..."
            download_uv "$mode"
            echo ""
            echo "✓ uv binary downloaded for $mode"
            ;;
        *)
            echo "Usage: $0 [all|current|<platform>]"
            echo "  all            - Download uv for all supported platforms (default)"
            echo "  current        - Download uv for current platform only"
            echo "  <platform>     - Download for specific platform:"
            echo "                   linux-x64, darwin-x64, darwin-arm64, win32-x64"
            exit 1
            ;;
    esac
}

main "$@"
