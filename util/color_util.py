import numpy as np
from skimage import color

def makeNdistinctColors(n): #TODO improve performance via packing
	cielabSpacePoints = _makeCIELABSearchSpace()
	if n==0:
		return None
	colors = [(0,0,128)]
	if n==1:
		return tuple(colors)
	for i in range(2,n):
		colors.append(_findFurthestPointInSpaceFromGivenSet(colors, cielabSpacePoints))
	return colors

def findFurthestPointInCIELAB(setOfPoints):
	cielabSpacePoints = _makeCIELABSearchSpace()
	return _findFurthestPointInSpaceFromGivenSet(setOfPoints, cielabSpacePoints)

def _findFurthestPointInSpaceFromGivenSet(setOfPoints, searchSpacePoints):
	currDistance = 0
	furthestPoint=None
	for point in searchSpacePoints: #TODO vectorize further
		newDistance = _findMinDistance(setOfPoints, point)
		if newDistance > currDistance:
			currDistance=newDistance
			furthestPoint=point
	return tuple(furthestPoint)

def _tuplesToNumpy(setOfPoints):
	dt=np.dtype('float')
	xarr = np.array(setOfPoints,dtype=dt)
	return xarr

def _cielabToRGB(point):
	rgbV = color.lab2rgb([[point]])
	rgbV = rgbV[0][0]
	rgbV = tuple(x*255 for x in rgbV)
	return rgbV

def _RGBtoCIELAB(point):
	point = tuple(x/255 for x in point)
	point = [[point]]
	cielabPoint = color.rgb2lab(point)
	return cielabPoint[0][0]		

def _findMinDistance(setOfPoints, possiblePoint):
	matrix = np.subtract(setOfPoints, possiblePoint)
	oneNormVector = np.sum(np.abs(matrix)**2,axis=-1)**(1./2)
	minIndex = np.argmin(oneNormVector)
	minDistance = oneNormVector[minIndex]
	return minDistance

def _makeCIELABSearchSpace():
	cielabSpace = []
	#shrink search space
	LRange = range(0,101,2)
	abRange = range(-127,128,8)
	for x in LRange:
		for y in abRange:
			for z in abRange:
				cielabSpace.append((float(x),float(y), float(z)))
	return cielabSpace

# sampleListOfPoints=[(0,0,0), (98,-127,-127), (98,-127,121), (100,121,-127)]
# print(findFurthestPointInCIELAB(sampleListOfPoints))
# print(makeNdistinctColors(10))