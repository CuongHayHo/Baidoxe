#!/bin/bash

# Baidoxe Desktop App Build Script
# Supports Windows, macOS, Linux builds

set -e

echo "🔨 Baidoxe Desktop App - Build Script"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
PLATFORM=${1:-all}
OUTPUT_DIR=${2:-./dist}

case "$PLATFORM" in
  windows|win|w)
    echo -e "${GREEN}Building for Windows...${NC}"
    npm run react-build
    npx electron-builder --win
    ;;
  macos|mac|m)
    echo -e "${GREEN}Building for macOS...${NC}"
    npm run react-build
    npx electron-builder --mac
    ;;
  linux|l)
    echo -e "${GREEN}Building for Linux...${NC}"
    npm run react-build
    npx electron-builder --linux
    ;;
  all|a)
    echo -e "${GREEN}Building for All Platforms...${NC}"
    npm run react-build
    npx electron-builder -mwl
    ;;
  *)
    echo -e "${RED}Usage: ./build.sh [platform] [output-dir]${NC}"
    echo "Platforms: windows, macos, linux, all"
    echo "Default: all"
    exit 1
    ;;
esac

echo -e "${GREEN}✅ Build completed!${NC}"
echo "Output: $OUTPUT_DIR"
ls -lah "$OUTPUT_DIR"
