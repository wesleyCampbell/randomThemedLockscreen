#! /bin/bash

# WALLPAPER_DIR="/home/wes/Pictures/Wallpapers"
#
APP_PATH=/home/wes/Applications/randomLockscreen
GET_IMG_EXE="$APP_PATH/app/get_random_lockscreen.sh"
#
# PYTHON_EXE="$APP_PATH/app/ColorPaletteEngine.py"
# PYTHON_VENV="$APP_PATH/app/venv/bin/activate"
#
DATA_PATH="$APP_PATH/data"

ACCENT0_PATH="$DATA_PATH/accent0"
ACCENT1_PATH="$DATA_PATH/accent1"
ACCENT2_PATH="$DATA_PATH/accent2"
ACCENT3_PATH="$DATA_PATH/accent3"

DOMINANT0_PATH="$DATA_PATH/dominant0"
DOMINANT1_PATH="$DATA_PATH/dominant1"

TEXT_COLOR_PATH="$DATA_PATH/text_color"

IMAGE_PATH="$DATA_PATH/image"


# if one of the required files does not exist, run the creation script
if [ ! -f "$ACCENT0_PATH" ] ||
	[ ! -f "$ACCENT1_PATH" ] ||
	[ ! -f "$ACCENT2_PATH" ] ||
	[ ! -f "$ACCENT3_PATH" ] ||
	[ ! -f "$DOMINANT1_PATH" ] ||
	[ ! -f "$DOMINANT0_PATH" ] ||
	[ ! -f "$TEXT_COLOR_PATH" ] ||
	[ ! -f "$IMAGE_PATH" ] ; then
		bash "$GET_IMG_EXE"
fi

accent0="$(cat $ACCENT0_PATH)"
accent1="$(cat $ACCENT1_PATH)"
accent2="$(cat $ACCENT2_PATH)"
accent3="$(cat $ACCENT3_PATH)"

dominant0="$(cat $DOMINANT0_PATH)"
dominant1="$(cat $DOMINANT1_PATH)"

text_color="$(cat $TEXT_COLOR_PATH)"

image="$(cat $IMAGE_PATH)"

# prepares the next random backscreen in the background
$GET_IMG_EXE &

# Sets the lockscreen based on the colors we've collected
function set_lockscreen {
	swaylock -f \
		--image $image \
		--color 333333 \
		--scaling fill \
		--indicator-radius 64 \
		--indicator-thickness 13 \
		--indicator-y-position 750 \
		--ring-color "$accent0" \
		--inside-color "$accent0"33 \
		--bs-hl-color "$dominant1" \
		--key-hl-color "$dominant0" \
		--line-color 222222 \
		--ring-clear-color "$accent1" \
		--inside-clear-color "$accent1"33 \
		--line-clear-color 222222 \
		--text-clear-color "$text_color" \
		--ring-ver-color "$accent2" \
		--inside-ver-color "$accent2"33 \
		--line-ver-color 222222 \
		--text-ver-color "$text_color" \
		--ring-wrong-color "$accent3" \
		--inside-wrong-color "$accent3"33 \
		--line-wrong-color 222222 \
		--text-wrong-color "$text_color"
}

set_lockscreen || $GET_IMG_EXE; set_lockscreen

