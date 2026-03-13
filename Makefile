# Minimal Makefile for local development environments that don't have just pre-installed.
# The primary build system is justfile — this only provides bootstrap helpers.
#
# NOTE: The install-just target is Linux x86_64 only. For CI environments,
# use the extractions/setup-just@v2 GitHub Action which supports all platforms.

JUST_VERSION := 1.46.0

.PHONY: install-just

install-just:
	@echo "Installing just $(JUST_VERSION)..."
	wget -qO- "https://github.com/casey/just/releases/download/$(JUST_VERSION)/just-$(JUST_VERSION)-x86_64-unknown-linux-musl.tar.gz" | tar xz -C /usr/local/bin just
	@just --version
