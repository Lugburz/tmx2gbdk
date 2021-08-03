# tmx2gbdk
A python script to convert Tiled's .tmx files and their tileset images to GBDK compatible .c and .h

GBTD and GBMD are great beginner tools but have their limitations so I wanted to design my maps directly in Tiled.

# Usage
For a specific file:

`python ./tmx2gbdk.py --input your_file.tmx`

If you just want to let it run in the background and recreate your files in real time:

`python ./t2gwatcher.py [folder_to_watch, by default './']`

# Example
I included a little map and its tileset so you can see how I configured it for now.

`python ./tmx2gbdk.py -i ./maps/example_map.tmx` will generate the .c and .h of both the tileset and the map. 

`python ./t2gwatcher.py` will continuously regenerate these files as you work on them.

You can see them changing in real time by editing `maps/example_map.tmx` in Tiled or editing `tilesets/tileset.png` in any image editor.

# Requirements
- [Tiled](https://www.mapeditor.org/) obviously
- python 3 (originally made with python 3.9.6)
- Pillow for tileset conversion ( `pip install Pillow` )

# Limitations
For now the project is very minimal as I made it for my own needs. Here are the limitation, sorted by likeliness that I solve the issue soon or not.

- rather than a "watcher" this script just sleeps 5 seconds then processes the whole folder again, even if there is not a single change in your files. I guess I could at least compare file modification date with the last time the script ended its process.
- the tileset has to be embedded in the .tmx file (in Tiled, that's the button right to "New Tileset" in the tilesets viewer). It's just a matter of opening another XML file though.
- only one layer and one tileset should be used, otherwise it might act funny.
- no support for GBC palettes, I only work with original GB for now but I may look into it later on.
- no support for banks yet, it always sets them to 0, not sure how that works yet.
- unlike GBTD and GBMD it only has ouput for GBDK C format.


# Todo
Beside the current limitations, I would like to include support for the following:

- map custom properties to be added as preprocessor statements
`#define {map_name}{map_property} {map_property_value}`
- tileset custom properties, to specify which tiles are solid for example
- allow for one object layer, which could help placing entities on your map
- make it a javascript extension for Tiled

# Licence
Example tileset created by [Dennis Payne](https://opengameart.org/users/dulsi).
