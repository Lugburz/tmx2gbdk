from PIL import Image
import os
import sys
import getopt

# for simplicity, consider a pixel :
# White if mean is purely 3
# Black if mean is purely 0
# Dark Gray if mean is above 2
# Light Gray otherwise
def get_pixel_color_index(rgb_im, x, y):
    r, g, b = rgb_im.getpixel((x, y))
    mean = (r + g + b) / 255
    if(mean == 3.0):
        return 0
    if(mean == 0.0):
        return 3
        return 0
    if(mean >= 2.0):
        return 2
    return 1

def binary2hexa(binary_string):
    decimal_representation = int(binary_string, 2)
    return "0x{:02X}".format(decimal_representation)

# input : 
#   rgb_img, an RGB converted image from Pillow
#   c, the tile's column
#   r, the tile's row
def convert_one_tile(rgb_im,c,r):
    # GBDK format uses two bytes per row of 8 pixels
    # in binary, palette positions are :
    # 0 => 000000000 (white)
    # 1 => 000000001 (light gray)
    # 2 => 000000010 (dark gray)
    # 3 => 000000011 (black)
    # if first bit is 1, we add a one to our first byte
    # if second bit is 1, we add a one to our second byte
    # otherwise corresponding byte gets a 0
    #
    # so a full LIGHT GRAY  line would be  0xFF,0x00 (11111111, 00000000)
    #    a full  DARK GRAY                 0x00,0xFF (00000000, 11111111)
    #    a full       BLACK                0xFF,0xFF (11111111, 11111111)
    #    a full       WHITE                0x00,0x00 (00000000, 00000000)
    #
    # a mix of white and black as WBWBWBWB gives 0x55,0x55 (01010101 01010101)
    # a mix of black and white as BWBWBWBW gives 0xAA,0xAA (10101010 10101010)
    # BLLLLLLL => 0xFF,0x80 (11111111,10000000)
    # NB : the byte position decreases when going right on the tile

    # xxx it would probably be smarter to think in terms of actual binary 
    # xxx but string logic works too and we don't have such constraints for once
    full_tile = []
    for y in range(8):
        row_binary_1 = ''
        row_binary_2 = ''
        for x in range(8):
            colori = get_pixel_color_index(rgb_im, c*8 + x, r*8 + y)
            if(colori == 0 or colori == 1):
                row_binary_1 += '0'
            else:
                row_binary_1 += '1'
            if(colori == 0 or colori == 2):
                row_binary_2 += '0'
            else:
                row_binary_2 += '1'
        full_tile.append( binary2hexa(row_binary_1) )
        full_tile.append( binary2hexa(row_binary_2) )

    return full_tile;


def get_file_content_c(tiles, fname, metadata):
    
    full_str = """
/*
    {name}.c
    
    Tile Source File.
    File generated with tileset2gbdk v0.1
*/ 

#define {name}BytesCount {length}
#define {name}TilesCount {tilesc}

const unsigned char {name}[] = 
{{
  {content}
}};

{metadata}
"""
    size = len(tiles)
    content = ''
    i = 0
    for byte in tiles:
        i+=1
        content += byte
        if(i < len(tiles)):
            content += ','
        if( i % 8 == 0 and i < len(tiles)):
            content += "\n  "

    metadata_str = ''
    if(metadata is not None):
        for key in metadata:
            metadata_str += "#define {name}{key}Length {size}\n".format(name=fname, key=key.capitalize(), size=len(metadata[key]))
            metadata_str += "const unsigned char {name}{key}[] =".format(name=fname, key=key.capitalize())
            metadata_str += "\n{\n  "

            meta_str = map(str, metadata[key])  
            metadata_str += ','.join(meta_str)
            metadata_str += "\n};\n"

    return full_str.format(name=fname, content=content, length=size, tilesc=int(size/2/8), metadata=metadata_str)

def get_file_content_h(tiles, fname):
    str = """
/*
    {name}.h

    Tile Include File.
    File generated with tileset2gbdk v0.1
*/ 
#ifndef __{name}_h_INCLUDE
#define __{name}_h_INCLUDE

#define {name}BytesCount {length}
#define {name}TilesCount {tilesc}

/* Bank of tiles. */
#define {name}Bank 0
/* Start of tile array. */
extern const unsigned char {name}[];

#endif
"""
    size = len(tiles)
    return str.format(name=fname, length=size, tilesc=int(size/2/8)) 



# CORE
# Convert image to byte array and save .c and .h files
def convert_tileset(img_path, verbose, metadata):

    img_basename = os.path.splitext(os.path.basename(img_path))[0]

    if(verbose):
        print("Opening", img_path)
    im = Image.open(img_path)
    rgb_im = im.convert('RGB')

    if(im.size[0] % 8 != 0 or im.size[1] % 8 != 0):
        print("Your image is not proper GB tileset, its size should be multiple of 8 (eg 48px by 56px)")
        exit(1)

    columns = int(im.size[0] / 8)
    rows = int(im.size[1] / 8)

    d_colors = ['WHITE', 'LGRAY', 'DGRAY', 'BLACK']

    tiles = []

    for r in range(rows):
        for c in range(columns):
            tile = convert_one_tile(rgb_im, c, r)
            tiles = tiles + tile

    # time to write our files
    content = get_file_content_c(tiles, img_basename, metadata)

    files_noext = os.path.splitext(img_path)[0]
    file_c = open(files_noext + ".c","w")
    file_c.write(content)
    file_c.close()

    if(verbose):
        print(files_noext + ".c saved")


    content = get_file_content_h(tiles, img_basename)
    file_c = open(files_noext + ".h","w")
    file_c.write(content)
    file_c.close()

    if(verbose):
        print(files_noext + ".h saved")


def help():
    h ="""
tileset2gbdk v0.1
Use this script to convert a tileset image (png, bitmap, any basic format handled by Pillow) 
to a format similar to the Gameboy Tile Designer (GBTD) GBDK C files output.
The purpose of this script is to be used with tmx2gbdk, alone it is pretty uneventful.

Usage
python tileset2gbdk.py (-i|--input)=path_to_image_file [(-o|--ouput)=path_to_file] [-h|--help] [-v]
Example
python .\tileset2gbdk.py -i '../map_forest_tiled.png' -v

help:   will display this help message
input:  mandatory, relative or absolute path to the image you want to convert
output: optional, which name to give your .h and .c files
        by default it will use the basename of your input file and put it the same folder
v:      verbose mode, will confirm the saved files names"""
    print(h)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:vi:v", ["help", "output=", 'input='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        help()
        sys.exit(2)

    minput = None
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            help()
            sys.exit()
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-i", "--input"):
            minput = a
        else:
            assert False, "unhandled option"

    if(minput is None):
        print("Input required")
        help()
        sys.exit()
	# executed as script
    convert_tileset(minput, verbose)