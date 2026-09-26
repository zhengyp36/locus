#!/usr/bin/env bash
# Build the screenlab research probe APK (no Gradle: aapt2 + javac + d8 + apksigner).
# Research-only artifact; does not touch the product app under cogos/screenlab/android.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK="${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}"
export JAVA_HOME="${JAVA_HOME:-$HOME/Android/jdk17}"
export PATH="$JAVA_HOME/bin:$PATH"
BT="$SDK/build-tools/34.0.0"
PLAT="$SDK/platforms/android-29/android.jar"
OUT="$HERE/build"
APK="$HERE/probe.apk"

for p in "$BT/aapt2" "$BT/d8" "$BT/zipalign" "$BT/apksigner" "$PLAT" "$JAVA_HOME/bin/javac"; do
    [ -e "$p" ] || { echo "missing: $p" >&2; exit 1; }
done

rm -rf "$OUT"; mkdir -p "$OUT/gen" "$OUT/classes"

echo "[1/6] aapt2 compile"
"$BT/aapt2" compile --dir "$HERE/res" -o "$OUT/res.zip"

echo "[2/6] aapt2 link"
"$BT/aapt2" link -o "$OUT/app-unsigned.apk" -I "$PLAT" \
    --manifest "$HERE/AndroidManifest.xml" \
    --java "$OUT/gen" \
    --min-sdk-version 29 --target-sdk-version 29 \
    "$OUT/res.zip"

echo "[3/6] javac"
find "$HERE/src" "$OUT/gen" -name '*.java' > "$OUT/sources.txt"
"$JAVA_HOME/bin/javac" -source 8 -target 8 -nowarn -encoding UTF-8 \
    -classpath "$PLAT" -d "$OUT/classes" @"$OUT/sources.txt"

echo "[4/6] d8"
find "$OUT/classes" -name '*.class' > "$OUT/classes.txt"
"$BT/d8" --lib "$PLAT" --min-api 29 --output "$OUT" @"$OUT/classes.txt"

echo "[5/6] package + align"
cp "$OUT/app-unsigned.apk" "$OUT/app.apk"
( cd "$OUT" && "$JAVA_HOME/bin/jar" uf app.apk classes.dex )
"$BT/zipalign" -f 4 "$OUT/app.apk" "$OUT/app-aligned.apk"

echo "[6/6] sign"
KS="$HERE/debug.keystore"
if [ ! -f "$KS" ]; then
    "$JAVA_HOME/bin/keytool" -genkeypair -keystore "$KS" -storepass android \
        -keypass android -alias androiddebugkey -keyalg RSA -keysize 2048 \
        -validity 10000 -dname "CN=Android Debug,O=Android,C=US" >/dev/null
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android --key-pass pass:android \
    --out "$APK" "$OUT/app-aligned.apk"
"$BT/apksigner" verify "$APK"
echo "OK -> $APK"
