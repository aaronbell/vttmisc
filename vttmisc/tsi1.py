import fontTools.ttLib
from fontTools.ttLib import TTFont
import argparse
from pathlib import Path

def clearSVCTA(data: str) -> None:
    lines = data.splitlines()

    newdata = ""

    for line in lines:
        if line == "SVTCA[X]":
            break
        newdata = newdata+"\n"+line 
        
    return newdata

def delete(font: TTFont, output: Path) -> None:
    for program in font["TSI1"].glyphPrograms:
        data = str.encode(font["TSI1"].glyphPrograms.get(program))
        data = str(data.decode())

        font["TSI1"].glyphPrograms[program] = clearSVCTA(data)
        font["TSI1"].glyphPrograms[program].encode()

    font.save(output)

def reWriteOFFSET(data: str, glyphOrder: list, glyphOrder_old: list) -> None:
    lines = data.splitlines()

    newdata = ""

    for line in lines:
        if "OFFSET" in line:
            splitLine = line.split(", ")
            try:
                name = glyphOrder_old[int(splitLine[1])]
                pos = "" 
                if name in glyphOrder:
                    pos = glyphOrder.index(name)
                    line = splitLine[0] + ", "+ str(pos)
                    i=2
                    while i < len(splitLine):
                        line = line+", "+splitLine[i]
                        i+=1
                else:
                    print (name+" not in new version. Please check " + lines[0])
            except:
                pass
        newdata = newdata+"\n"+line 

    return newdata

def fixOFFSET(newFont: TTFont, VTTSource: TTFont) -> None:

    glyphOrder = newFont.getGlyphOrder()
    glyphOrder_old = VTTSource.getGlyphOrder()

    for program in newFont["TSI1"].glyphPrograms:
        data = str.encode(newFont["TSI1"].glyphPrograms.get(program))
        data = str(data.decode())

        newFont["TSI1"].glyphPrograms[program] = reWriteOFFSET(data, glyphOrder, glyphOrder_old)
        newFont["TSI1"].glyphPrograms[program].encode()
    return newFont

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
        
        updatedFont = fixOFFSET(TTFont(inputPath), TTFont(vttPath))
        
        updatedFont.save(output)
    if vars(args).get("svtca") == True:
        if args.output:
            output = vars(args).get("output")
        else:
            newName = str(inputPath.name)[:-4]+"-stripped.ttf"
            output = inputPath.parent / newName
        delete(TTFont(inputPath),output)