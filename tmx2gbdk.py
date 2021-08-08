import xml.etree.ElementTree as ET
import sys, os, getopt
import tileset2gbdk

def int2hexa(decimal_representation):
    return "0x{:02X}".format(decimal_representation)

def get_file_content_c(main_map, w, h, fname):
    str="""/*
    {name}.c
    
    Map Source File.
    File generated with tmx2gbdk v0.1
*/

#define {name}Width {width}
#define {name}Height {height}
#define {name}Bank 0

const unsigned char {name}[] = 
{{
  {content}
}};
"""
    content = ''
    i = 0
    for tilei in main_map:
        i+=1
        content += tilei
        if(i < len(main_map)):
            content += ','
        if( i % w == 0 and i < len(main_map)):
            content += "\n  "

    return str.format(name=fname, content=content, width=w, height=h)

def get_file_content_h(main_map, w, h, fname):
    str="""/*
    {name}.h
    
    Map Include File.
    File generated with tmx2gbdk v0.1
*/
#ifndef __{name}_h_INCLUDE
#define __{name}_h_INCLUDE

#define {name}Width {width}
#define {name}Height {height}
#define {name}Bank 0

extern const unsigned char {name}[];

#endif
"""
    return str.format(name=fname, width=w, height=h)

# extract metadata from a tileset
# each node can have custom properties, 
# we will compile them here to be sent
# to tileset2gbdk, which will incorporate
# said data to its output files
# Input: 
#   tileset node, we will ignore the "image" subnode
# Output:
#   dictionary of "property_name" : [indexes of tiles] 
def extract_metadata_tiles(node):
    metadata = {}
    for child in node:
        if(child.tag == 'tile'):
            current_id = child.attrib['id']
            # should only contain "properties" node at index 0
            for prop in child[0]:
                key = prop.attrib['name']
                val = prop.attrib['value']
                # xxx for now we only manage booleans
                if(val == "1" or val == "true"):
                    if key not in metadata:
                        metadata[key] = []
                    metadata[key].append(int(current_id))
    return metadata

def read_tileset_node(node, path, verbose):

    if(verbose):
        print("Found tileset, converting it too")

    node_metadata = None
    img_path = None

    # if it's an external tileset (tsx)
    if('source' in node.attrib):
        absdir = os.path.abspath(os.path.dirname(path))
        adaptative_path=os.path.join(absdir, node.attrib['source'])
        tree = ET.parse(adaptative_path)
        root = tree.getroot()
        img_path = os.path.join(os.path.dirname(node.attrib['source']), root[0].attrib['source'])
        node_metadata = root
    else:
        # embedded tileset, direct access
        img_path = node[0].attrib['source']
        node_metadata = node

    metadata = extract_metadata_tiles(node_metadata)

    absdir = os.path.abspath(os.path.dirname(path))
    adaptative_path=os.path.join(absdir, img_path)

    tileset2gbdk.convert_tileset(adaptative_path, verbose, metadata)


def convert_tmx(path, verbose):
    tree = ET.parse(path)
    root = tree.getroot()

    map_height=int( root.attrib['height'] )
    map_width =int( root.attrib['width']  )

    main_map = []

    for child in root:
        if(child.tag == 'tileset'):
            read_tileset_node(child, path, verbose)
        elif(child.tag == 'layer'):
            # in layer we want to find our csv background layer
            for subchild in child:
                if(subchild.tag == 'data'):
                    if(subchild.attrib['encoding'] != 'csv'):
                        print("Error: layer encoding should be configured to CSV")
                        sys.exit(1)
                    for tilei in subchild.text.split(','):
                        # convert "empty" (0) to first tile
                        if(int(tilei) <= 1):
                            tilei = 1
                        main_map.append( int2hexa( int(tilei) - 1 ))


    files_noext = os.path.splitext(path)[0]

    content = get_file_content_c(main_map, map_width, map_height, os.path.splitext(os.path.basename(path))[0])
    file_c = open(files_noext + ".c","w")
    file_c.write(content)
    file_c.close()

    if(verbose):
        print(files_noext + ".c saved")

    content = get_file_content_h(main_map, map_width, map_height, os.path.splitext(os.path.basename(path))[0])
    file_c = open(files_noext + ".h","w")
    file_c.write(content)
    file_c.close()

    if(verbose):
        print(files_noext + ".h saved")


def help():
    h ="""
tmx2gbdk v0.1

help:   will display this help message
input:  mandatory, relative or absolute path to the .tmx you want to convert"""
    print(h)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:v", ["help", 'input='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        help()
        sys.exit(2)

    input = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            help()
            sys.exit()
        elif o in ("-i", "--input"):
            input = a
        else:
            assert False, "unhandled option"

    if(input is None):
        print("Input required")
        help()
        sys.exit()
	# executed as script
    convert_tmx(input, verbose)




