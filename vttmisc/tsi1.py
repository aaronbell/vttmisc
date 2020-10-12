from fontTools.ttLib import TTFont
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