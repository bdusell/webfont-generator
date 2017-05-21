#!/bin/bash

# Setup script for webfont-generator. Fetches and builds third-party
# libraries.

BASE_DIR=$(dirname "${BASH_SOURCE-$0}")
VENDOR_DIR="$BASE_DIR"/vendor
SFNTLY_DIR="$VENDOR_DIR"/sfntly
WOFF2_DIR="$VENDOR_DIR"/woff2
JAVA_DIR="$BASE_DIR"/src/java

print_ansi_code() {
  printf '\033[%sm' "$1"
}

print_color() {
  print_ansi_code "0;$1"
  printf '%s' "$2"
  print_ansi_code '0'
}

stamp() {
  printf '[%s]' "$(date '+%F %r')"
}

log() {
  { print_color '33' "$(stamp)"; echo " $1"; } >&2
}

warn() {
  { print_color '31' "$(stamp) $1"; echo; } >&2
}

command_exists() {
  which "$1" 2>&1 > /dev/null
}

require_command() {
  local COMMAND=$1
  local NAME=${2-$COMMAND}
  if command_exists "$COMMAND"; then
    log "Found ${COMMAND}."
  else
    warn "You do not have $NAME installed. Please install $NAME."
    false
  fi
}

fetch_sfntly() {
  if [ ! -d $SFNTLY_DIR ]; then
    log 'Fetching sfntly...'
    git clone https://github.com/googlei18n/sfntly.git "$SFNTLY_DIR"
  fi
}

build_sfntly() {
  log 'Building sfntly...'
  (cd "$SFNTLY_DIR"/java && ant)
}

fetch_woff2() {
  if [ ! -d $WOFF2_DIR ]; then
    log 'Fetching woff2...'
    git clone http://github.com/google/woff2.git "$WOFF2_DIR" &&
    (
      cd "$WOFF2_DIR" &&
      git submodule init &&
      git submodule update
    )
  fi
}

build_woff2() {
  log 'Building woff2...'
  make -C "$WOFF2_DIR" all
}

build_java() {
  log 'Building java classes...'
  make -C "$JAVA_DIR"
}

main() {
  require_command 'git' &&
  require_command 'java' &&
  require_command 'javac' &&
  require_command 'ant' &&
  require_command 'python' &&
  require_command 'make' &&
  require_command 'fontforge' 'FontForge' &&
  mkdir -p "$VENDOR_DIR" &&
  fetch_sfntly &&
  build_sfntly &&
  fetch_woff2 &&
  build_woff2 &&
  build_java &&
  log 'Good to go!'
}

main "$@"
