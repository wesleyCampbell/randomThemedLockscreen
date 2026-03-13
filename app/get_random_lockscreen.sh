#!/bin/bash

WALLPAPER_DIR="/home/wes/Pictures/Wallpapers"

APP_PATH=/home/wes/Applications/randomLockscreen

PYTHON_EXE="$APP_PATH/app/ColorPaletteEngine.py"
PYTHON_VENV="$APP_PATH/app/venv/bin/activate"
PYTHON_DEPS=(
	"Pillow" 
	"numpy" 
	"opencv-python" 
	"scikit-learn" 
	"colormath" 
	"typing" 
	"matplotlib" 
	)
download_deps=0


DATA_PATH="$APP_PATH/data"
IMG_PATH="$DATA_PATH/image"

ACCENT_NUM=4
DOM_NUM=2

random_bg=$(find "$WALLPAPER_DIR" -type f | shuf -n 1)

# Make sure the data directory exists
mkdir -p "$DATA_PATH"

# Make sure that the python VENV is installed
if [ ! -f "$PYTHON_VENV" ]; then
	python3 -m venv "$APP_PATH/app/venv"
	download_deps=1	
fi
source "$PYTHON_VENV"

# Downloads the necessary python dependencies, if needed
if [[ $download_deps -eq 1 ]]; then
	for dep in "${PYTHON_DEPS[@]}"; do
		pip install "$dep"
	done
fi

accent_list=$(python3 "$PYTHON_EXE" "$random_bg" accent "$ACCENT_NUM" | grep -Po '(?<=#).*')
dom_list=$(python3 "$PYTHON_EXE" "$random_bg" "dominant" "$DOM_NUM" | grep -Po '(?<=#).*')

# Put accent and dominant colors into arrays
accent_array=()
for accent in $accent_list; do
	accent_array+=($accent)
done
dom_array=()
dom_sum=0
for dom in $dom_list; do
	dom_array+=($dom)

	# Used for text color determination
	for (( j = 0; j<${#dom}; j=j+2 )); do
		digit="${dom:j:1}"
		dom_sum=$(( dom_sum + 16#$digit ))
	done
done

# If the average dominant color is greater than the halfway point (kinda), we need dark text.
# Light text otherwise.
text_color=""
if [[ $dom_sum -gt $(( 16 * DOM_NUM )) ]] ; then
	text_color=222222
else 
	text_color=cccccc
fi

echo "$random_bg" > "$IMG_PATH"
echo "${accent_array[0]}" > "$DATA_PATH/accent0"
echo "${accent_array[1]}" > "$DATA_PATH/accent1"
echo "${accent_array[2]}" > "$DATA_PATH/accent2"
echo "${accent_array[3]}" > "$DATA_PATH/accent3"

echo "${dom_array[0]}" > "$DATA_PATH/dominant0" 
echo "${dom_array[1]}" > "$DATA_PATH/dominant1"

echo "$text_color" > "$DATA_PATH/text_color"
