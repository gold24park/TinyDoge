#!/bin/zsh

mkdir -p dist/dmg

rm -r dist/dmg/*

cp -r "dist/TinyDoge.app" dist/dmg

test -f "dist/TinyDoge.dmg" && rm "dist/TinyDoge.dmg"

create-dmg \
  --volname "TinyDoge" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "TinyDoge.app" 175 120 \
  --hide-extension "TinyDoge.app" \
  --app-drop-link 425 120 \
  "dist/TinyDoge.dmg" \
  "dist/dmg/"