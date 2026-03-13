# Random Lockscreen Setter

### Overview 

This project takes a directory full of image files and will select one at random and will use it
as the image for a lockscreen.

When the image is selected, the python engine will perform color calculations and will extract
the primary and accent colors used in this image and will save them to a cache.

The script than can read the selected image and extracted colors and can use it to create a color
palatte for the lockscreen, allowing for dynamic color configurations that match the background 
image.

It is currently configured to use `swaylock` or `i3lock` but will be able to be configured for
an arbitrary lock command, if you know the CLI command.

### Usage

To use this script, you must first edit the configuration file `lockscreen.conf` and set the following parameters:
- APP_PATH: This is the file path of the directory of where the application will be running from.
    - e.g. `APP_PATH=~/Applications/randomLockscreen/`
- WALLPAPER_DIR: This is the file path of the directory of where you are storing your images to pull from
    - e.g. `WALLPAPER_DIR=~/Pictures/Wallpapers"
- ACCENT_NUM: This is the number of accent colors you wish to extract from the image. The default is 4.
    - e.g. `ACCENT_NUM=3`
- DOM_NUM: This is the number of dominant colors you wish to extract from the image. The default is 2.
    - e.g `DOM_NUM=1`

After that, you can run the `set_random_lockscreen.sh` file located in the `app` directory of the root project folder. The first time it will take a significant amount of time as it needs to create a python venv and perform all of the necessary calculations (which takes some time). After this, however, the next random lockscreen and color codes will be cached in the `data` directory, allowing for instant locking.  

### File Structure

The application is comprised of two folders `app` and `data`. These two folders will be stored within whichever directory you choose to place the application. You can even change the location of the `data` folder by modifying the script's `DATA_PATH` variable in `lockscreen.conf`.

It is a somewhat rudimentary way of storing a program, but it works.
