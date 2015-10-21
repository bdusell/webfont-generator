#!/bin/bash

# Fetch and build third-party libraries

BASE_DIR=$(dirname "$(readlink -f "$BASH_SOURCE")")
VENDOR_DIR="$BASE_DIR"/vendor
SFNTLY_DIR="$VENDOR_DIR"/sfntly
WOFF2_DIR="$VENDOR_DIR"/woff2
JAVA_DIR="$BASE_DIR"/src/java

require_command() {
  local COMMAND=$1
  local NAME=$2
  [[ -n $NAME ]] || NAME=$COMMAND
  which "$COMMAND" 2>&1 > /dev/null || {
    echo "You do not have $NAME installed. Please install $NAME."
    false
  }
}

fetch_sfntly() {
  if [[ ! -d $SFNTLY_DIR ]]; then
    echo 'Fetching sfntly...'
    svn checkout http://sfntly.googlecode.com/svn/trunk/ "$SFNTLY_DIR"
  fi
}

build_sfntly() {
  echo 'Building sfntly...'
  (cd "$SFNTLY_DIR"/java && ant)
}

fetch_woff2() {
  if [[ ! -d $WOFF2_DIR ]]; then
    echo 'Fetching woff2...'
    git clone http://github.com/google/woff2.git "$WOFF2_DIR" && (
      cd "$WOFF2_DIR" && \
        git submodule init && \
        git submodule update
    )
  fi
}

build_woff2() {
  echo 'Building woff2...'
  make -C "$WOFF2_DIR" all
}

build_java() {
  echo 'Building java classes...'
  make -C "$JAVA_DIR"
}

{
  require_command 'python'
} && {
  require_command 'java'
} && {
  require_command 'svn'
} && {
  require_command 'git'
} && {
  require_command 'ant'
} && {
  require_command 'fontforge' 'FontForge'
} && {
  mkdir -p "$VENDOR_DIR"
} && {
  fetch_sfntly && build_sfntly
} && {
  fetch_woff2 && build_woff2
} && {
  build_java
} && {
  echo 'Good to go!'
}
