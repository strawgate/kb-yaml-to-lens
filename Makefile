# Minimal Makefile for CI environments that don't have just pre-installed.
# The primary build system is justfile — this only provides bootstrap helpers.
# NOTE: install-just is Linux x86_64 only and intended as a local fallback.
# Cross-platform CI should use extractions/setup-just@v2.

JUST_VERSION := 1.46.0

.PHONY: install-just

install-just:
	@echo "Installing just $(JUST_VERSION)..."
	wget -qO- "https://github.com/casey/just/releases/download/$(JUST_VERSION)/just-$(JUST_VERSION)-x86_64-unknown-linux-musl.tar.gz" | tar xz -C /usr/local/bin just
	@just --version
