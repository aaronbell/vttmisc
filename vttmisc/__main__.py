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
        "-o",
        type=str,
        dest="inputPath",
        help='path to input font',
        required=True,
    )
    parser.add_argument(
        "-s",
        type=str,
        dest="vttPath",
        help='path to old VTT source font',
        default=None,
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

    if vars(args).get("offset") == True:
        if args.output:
            output = vars(args).get("output")
        else:
            newName = str(inputPath.name)[:-4]+"-fixed.ttf"
            output = inputPath.parent / newName
        
        updatedFont = tsi1.fixOFFSET(TTFont(inputPath), TTFont(vttPath))
        
        updatedFont.save(output)
    if vars(args).get("svtca") == True:
        if args.output:
            output = vars(args).get("output")
        else:
            newName = str(inputPath.name)[:-4]+"-stripped.ttf"
            output = inputPath.parent / newName
        tsi1.delete(TTFont(inputPath),output)

    if vars(args).get("makeCVAR") == True:

        font = TTFont(inputPath)
        vttSource = TTFont(vttPath)

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