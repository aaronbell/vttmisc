from fontTools.ttLib import TTFont
import argparse
from vttmisc import tsi1, tsic
from pathlib import Path
import xml.etree.cElementTree as ET
import tempfile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="misc font work")

    parser.add_argument( 
        "--fix-offset", 
        default=False,
        action="store_true",
        dest="offset",
        help="Fix the offset of the VTT source based on old version of font",
        )
    parser.add_argument(
        "--clear-svtca", 
        default=False,
        action="store_true",
        dest="svtca",
        help="Remove all SVTCA[X] code from the VTT source",
        )
    parser.add_argument(
        "--makeCVAR", 
        default=False,
        action="store_true",
        dest="makeCVAR",
        help="Create CVAR table from TSIC",
        )
    parser.add_argument(
        "-i",
        type=str,
        dest="inputPath",
        help='path to input font',
        default=None,
        required=True,
    )
    parser.add_argument(
        "-s",
        type=str,
        dest="vttPath",
        help='path to old VTT source font',
    )
    parser.add_argument(
        "-d",
        type=str,
        dest="output",
        help='path for output',
    )

    args = parser.parse_args()

    inputPath = Path(vars(args).get("inputPath"))
    if vars(args).get("vttPath"):
        vttPath = Path(vars(args).get("vttPath"))
    else:
        vttPath = None

# Fix offsets
    if vars(args).get("offset") == True:
        newFont = TTFont(inputPath)
        vttSource = TTFont(vttPath)
            
        if args.output:
            output = vars(args).get("output")
        else:
            newName = str(inputPath.name)[:-4]+"-fixed.ttf"
            output = inputPath.parent / newName

        if vttPath is not None:
            if "TSI1" in newFont and "TSI1" in vttSource:
                if "post" not in vttSource or vttSource["post"].formatType == 3.0 or "post" not in newFont or newFont["post"].formatType == 3.0:
                        print ("*Warning* Input font / source font lack post table v3, not all components may be converted")
                updatedFont = tsi1.fixOFFSET(newFont, vttSource)
                
                updatedFont.save(output)
            else:
                print ("*FAIL* Input font / source font lack TSI1 table.")
        else:
            print ("*FAIL* Source font not found")

# Remove SVTCA
    if vars(args).get("svtca") == True:
        font = TTFont(inputPath)
        if args.output:
            output = vars(args).get("output")
        else:
            newName = str(inputPath.name)[:-4]+"-stripped.ttf"
            output = inputPath.parent / newName
        
        if "TSI1" in font:
            tsi1.delete(font,output)
        else:
            print ("*Fail* Font lacking TSI1 table. ")


# makeCVAR 
    if vars(args).get("makeCVAR") == True and vars(args).get("vttPath") is not None:

        font = TTFont(inputPath)
        vttSource = TTFont(vttPath)

        if "TSIC" in vttSource:
        
            tree = ET.ElementTree()
            TSICfile = tempfile.NamedTemporaryFile()
            vttSource.saveXML(TSICfile.name, tables=["TSIC"])
            tree = ET.parse(TSICfile.name)

            tsic.makeCVAR(font, tree)

            if args.output:
                output = vars(args).get("output")
            else:
                newName = str(inputPath.name)[:-4]+"-cvar.ttf"
                output = inputPath.parent / newName

            font.save(output)
        else:
            print ("*FAIL* Source file missing TSIC table")
    elif vars(args).get("makeCVAR") == True and vars(args).get("vttPath") == None:
        print ("*FAIL* Source VTT file required.")

    if vars(args).get("offset") == False and vars(args).get("svtca") == False and vars(args).get("makeCVAR") == False:
        print ("No script selected.")