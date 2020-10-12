from fontTools.ttLib import TTFont, newTable
import xml.etree.cElementTree as ET
from fontTools.ttLib.tables.TupleVariation import POINT_RUN_COUNT_MASK, TupleVariation

# fontTools needs an axis object that stores the relevant axis info with certain functions. Here's what I was able to figure out it wants:

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
    def get(self,axis, values):
        if len(self.header) > 1:
            for item in self.header:
                if item[0] == axis:
                    return item[1]
        else:
            return self.header[0][1]

def interpolate (normalCVT:int, loc:list, interpolationAxes:list, cvt:int) -> None: 
    # I assume this is badly optimized but it seems to work. So lalalalalalalala. 

    axisDifferences = []
    for i, point in enumerate(loc[1]):
        # Here's what we need to do. For each axis, determine the CVT value of A and B, to figure out the medial (OHGOD)
        # A ------ Point ------ B
        #defaults
        lowerPoint = [0.0, normalCVT]
        upperPoint = [0.0, normalCVT]
        medialPoint = [point[1][1], normalCVT]

        if medialPoint[0] < 0.0:
            lowerPoint[0] = -1.0
            upperPoint[0] = 0.0
        elif medialPoint[0] > 0.0:
            lowerPoint[0] = 0.0
            upperPoint[0] = 1.0

        axisMap = [[lowerPoint[0], lowerPoint[1]], [upperPoint[0], upperPoint[1]]]

        # First we parse through the points that are on the major axis and see if they are applicable for this range
        applicable = []
        reject = False
        for location in interpolationAxes:
            reject = False
            if location[0][i] == 0.0: # if at 0.0, then must be on another axis (as there is no (0.0, 0.0))
                reject = True
            elif location[0][i] > 0.0 and medialPoint[0] < 0.0: # if above 0.0 when point is below 0.0
                reject = True
            elif location[0][i] < 0.0 and medialPoint[0] > 0.0: # opposite
                reject = True

            for value in location[0]:
                if value == location[0][i]:
                    pass
                else:
                    if value != 0.0: # all other axis values must be 0.0 or it is not applicable
                        reject = True

            if cvt not in location[1]:
                reject = True          # also gotta make sure the correct Offset is present
            if reject == False:
                applicable.append(location)
        # now that we know which (if any) values from the above are applicable, we position them on the axis
        if len(applicable) > 0:
            for location in applicable:
                insertAbove = []
                for loc in axisMap:
                    if location[0][i] == loc[0]:
                        loc[1] = location[2][location[1].index(cvt)]
                    if location[0][i] > loc[0]:
                        insertAbove = loc
                    if location[0][i] < loc[0]:
                        break
                if len(insertAbove) > 0:
                    axisMap.insert(axisMap.index(insertAbove)+1, [location[0][i], location[2][location[1].index(cvt)]])
        
        
        # now we can start evaluating the medialPoint
        done = False
        lowerLimit = []
        upperLimit = []
        diff = 0

        for location in axisMap:            # if point is at the same location as an existing point, exit out
            if point[1][1] == location[0]:
                diff = normalCVT - location[1]
                done = True
                break
        if done == False:                   # if not, we have to figure out which points it is between
            for location in axisMap:        # so we set a lower and upper limit location
                if point[1][1] > location[0]:
                    lowerLimit = location
                else:
                    break
            for location in axisMap[::-1]:
                if point[1][1] < location[0]:
                    upperLimit = location
                else:
                    break
            #if these values are the same, diff is 0 (default), otherwise have to calculate ratio and determine what the expected value of the medial point would be. 
            if lowerLimit[1] != upperLimit[1]:
                ratio = abs(upperLimit[0] - point[1][1]) / abs(upperLimit[0] - lowerLimit[0])
                diff = round((upperLimit[1] - lowerLimit[1]) * ratio)
        axisDifferences.append(diff)

    # since we need to account for differences across multiple axis, we sum up these differences and diff it from the normalCVT from the cvt table to find the adjusted CVT value
    expectedVal = normalCVT - sum(axisDifferences)
    return expectedVal
    

def processMajor (majorLocations: list, locMap : list) -> None:
    for location in majorLocations:
        for x, l in enumerate(location[1]):
            map = list(locMap.values())[x]
            peak = float(l[1])
            posCount = 0
            negCount = 0
            negIntermed = False
            posIntermed = False

            for value in map:
                if peak > 0.0 and value > 0.0:
                    posCount += 1
                if value < 0.0 and value < 0.0:
                    negCount += 1
            if negCount > 1:
                negIntermed = True
            if posCount > 1:
                posIntermed = True
            minBound = 0.0
            maxBound = 0.0

            if peak > 0.0 and posIntermed == False:
                minBound = 0.0
                maxBound = peak
            elif peak < 0.0 and negIntermed == False:
                minBound = peak
                maxBound = 0.0
            elif peak > 0.0 and posIntermed == True:
                minBound = map[map.index(peak)-1]
                maxBound = peak
            elif peak < 0.0 and negIntermed == True:
                minBound = peak
                maxBound = map[map.index(peak)+1]
            elif peak == 0.0:
                minBound = 0.0
                maxBound = 0.0
            else:
                print ("Something weird happened here")
                print (map, l)

            l[1] = (minBound, peak, maxBound)
            l[0] = list(locMap.keys())[x]

def processMinor (minorLocations: list, locMap: list) -> None:
    for location in minorLocations:
        for x, l in enumerate(location[1]):
            map = list(locMap.values())[x]
            peak = float(l[1])
            minBound = 0.0
            maxBound = 0.0
            atMax = False
            if map[0] == peak or map[len(map)-1] == peak:
                atMax = True

            if peak > 0.0 and atMax == True:
                minBound = 0.0
                maxBound = peak
            elif peak < 0.0 and atMax == True:
                minBound = peak
                maxBound = 0.0
            elif peak < 0.0 and atMax == False:
                minBound = -1.0
                maxBound = 0.0
            elif peak < 0.0 and atMax == False:
                minBound = 1.0
                maxBound = 0.0
            elif peak == 0.0:
                minBound = 0.0
                maxBound = 0.0
            else:
                print ("Something weird happened here")
                print (map, l)

            l[1] = (minBound, peak, maxBound)
            l[0] = list(locMap.keys())[x]

def makeCVAR (varFont: TTFont, tree: ET.ElementTree) -> None:
    root = tree.getroot()
    TSIC = root.find("TSIC")

    # This used to be simple, then I discovered intermediate CVTs, and then more than one axis

    # Making sure that there are not axes in the TSIC table that aren't in the font (fvar).
    # Assuming a VTT-made TSIC table this shouldn't be the case, but better to check than not. 
    keyValues = []
    for axis in varFont["fvar"].axes:
        keyValues.append(axis.axisTag)

    # Here we assemble a axis-specific map of the interpolation space where CVTs are modified
    # As we sort through the RecordLocations, we will modify this map as necessary. 
    locMap = {}
    for axis in TSIC.findall("AxisArray"): 
        locMap.update({
            axis.get("value") : [0.0]
            })

    # Processing through the RecordLocations, we fill in the locMap above, as well as create a 
    # set of axisLocations that we'll use to generate the header file
    majorLocations = []
    minorLocations = []
    for i, loc in enumerate(TSIC.findall("RecordLocations")):
        axisLocation = []
        major = False
        for axis in loc.findall("Axis"):    # For the location map, we really only care about points on the major axes
            if axis.get("value") == "0.0" or axis.get("value") == "0" or len(keyValues) == 1:
                major = True
        
        # once we know a given record has a value of 0.0 (eg, on major axis), we add it to the locMap
        if major == True:          
            for axis in loc.findall("Axis"):
                if float(axis.get("value")) not in list(locMap.values())[int(axis.get("index"))]:
                        list(locMap.values())[int(axis.get("index"))].append(float(axis.get("value")))
                axisLocation.append([
                    int(axis.get("index")),
                    float(axis.get("value"))
                ])
            majorLocations.append([i,axisLocation])
            
        elif major == False:
            for axis in loc.findall("Axis"):
                axisLocation.append([
                    int(axis.get("index")),
                    float(axis.get("value"))
                ])
            minorLocations.append([i,axisLocation])

    #do a quick sort to make sure everything is in order. 
    for i, value in enumerate(list(locMap.values())):
        value.sort()
        list(locMap.values())[i] = value

    # Now that we've established the major axis locMap, we can create mappings for those positions
    processMajor(majorLocations, locMap)
    processMinor(minorLocations, locMap)

    # Now that we have the locMap and the locations, we can build the headers for the TupleVariation file

    # Just doing some assembly of the CVT values
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
    interpolationAxes = []
    # interpolationAxis = [[ [-1.0, 0.0], [0, 50], [100, 200] ]]
    # this says, [position, CVTs, CVT values]

    # NOW LET'S GET TUPLING

    for l in majorLocations:
        supportHeader = []
        recordIndex = l[0]
        coordinates = []
        for axis in l[1]:
            # Handily, we've already built the header file above
            supportHeader.append(([axis[0], axis[1]]))
            coordinates.append(axis[1][1]) #we need this for later
        interpolationAxes.append([coordinates, CVT_num[l[0]], CVT_val[l[0]]])

        # assemble the delta information for the second half of TupleVariation 
        delta = []
        for i in range(0, len(varFont["cvt "])-1):
            if i in CVT_num[recordIndex]:
                deltaVal = CVT_val[recordIndex][CVT_num[recordIndex].index(i)]
                normalCVT = varFont["cvt "].__getitem__(i)
                delta.append(deltaVal - normalCVT)
            else:
                delta.append(None)
        
        support = axisStorage(supportHeader,keyValues)
        var = TupleVariation(support, delta)
        variations.append(var)

    for l in minorLocations:
        supportHeader = []
        recordIndex = l[0]
        for axis in l[1]:
            # Handily, we've already built the header file above
            supportHeader.append(([axis[0], axis[1]]))
            
        # assemble the delta information for the second half of TupleVariation 
        delta = []
        for i in range(0, len(varFont["cvt "])-1):
            if i in CVT_num[recordIndex]:
                deltaVal = CVT_val[recordIndex][CVT_num[recordIndex].index(i)]
                normalCVT = varFont["cvt "].__getitem__(i)

                #the delta is actually not from the normalCVT, but the *expected* CVT, which is determined by the major axis and any modifications therein present. YIKES
                adjustedCVT = interpolate(normalCVT, l, interpolationAxes, i)

                delta.append(deltaVal - adjustedCVT)
            else:
                delta.append(None)
            
        support = axisStorage(supportHeader,keyValues)
        var = TupleVariation(support, delta)
        variations.append(var)

    varFont["cvar"] = newTable('cvar')
    varFont["cvar"].version = 1
    varFont["cvar"].variations = variations
    