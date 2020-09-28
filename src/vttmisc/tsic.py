import fontTools.ttLib
import xml.etree.cElementTree as ET
from fontTools.ttLib.tables.TupleVariation import TupleVariation

class axisStorage(object):
    def __init__(self, header, axisTags):
        self.header = header
        self.axisTags = axisTags
    def copy(self):
        return self
    def items(self):
        return self.header
    def keys(self):
        return self.axisTags
    def get(self,axis,values):
        peak = "0"
        for item in self.header:
            if item[0] == axis:
                peak = item[1]

        if int(float(peak)) == -1:
            return (peak, peak, 0)
        elif int(float(peak)) == 1:
            return (0, peak, peak)

def generate (varFont: fontTools.ttLib.TTFont, tree: ET.ElementTree) -> None:
    root = tree.getroot()
    TSIC = root.find("TSIC")

    axisSet = []
    for axis in TSIC.findall("AxisArray"):
        axisSet.append(axis.get("value"))

    locations = []
    for loc in TSIC.findall("RecordLocations"):
        axisLoc = []
        for axis in loc.findall("Axis"):
            axisLoc.append([axis.get("index"),axis.get("value")])
        locations.append(axisLoc)
    CVT_num = []
    CVT_val = []
    for rec in TSIC.findall("Record"):
        RecNum = []
        RecVal = []
        for num in rec.findall("CVTArray"):
            RecNum.append(int(num.get("value")))
        for pos in rec.findall("CVTValueArray"):
            RecVal.append(int(pos.get("value")))
        CVT_num.append(RecNum)
        CVT_val.append(RecVal)

    variations = []

    supportAxisTags = []
    for tag in axisSet:
        supportAxisTags.append(tag)

    # Now let's play the game of making TupleVariation happy, somehow. 
    for x, l in enumerate(locations):
        for loc in l:
            #supportLoc = [[0, ["wght","-1.0"]],[1, ["wght","1.0"]]]
            supportLoc = [0, ["wght",("-1.0", "-.333", 0)]]
            supportHeader = []
            
            axisChoice = int(float(loc[0]))
            if float(loc[1]) < 0:
                supportHeader.append([axisSet[axisChoice],float(loc[1])])
            elif float(loc[1]) > 0:
                supportHeader.append([axisSet[axisChoice],float(loc[1])])

        #    if n-1 > 0:
        #        support = support+", "
        #    axisChoice = int(float(loc[0]))
        #    if float(loc[1]) < 0:
        #        support = axisSet[axisChoice]+"=("+loc[1]+", "+loc[1]+", 0)"
        #    elif float(loc[1]) > 0:
        #        support = axisSet[axisChoice]+"=(0, "+loc[1]+", "+loc[1]+")"

            delta = []
            for i in range(0, len(varFont["cvt "])-1):
                if i in CVT_num[x]:
                    deltaVal = CVT_val[x][CVT_num[x].index(i)]
                    delta.append(deltaVal)
                else:
                    delta.append(None)
            
            support = axisStorage(supportHeader,supportAxisTags, supportLoc)
            var = TupleVariation(support, delta)
            print (var)
            variations.append(var)

    varFont["cvar"] = fontTools.ttLib.newTable('cvar')
    varFont["cvar"].version = 1
    #varFont["cvar"].variations = variations