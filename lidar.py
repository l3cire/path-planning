import random

import numpy as np
from math import *
import scipy as sc
import scipy.optimize as opt
from sklearn.linear_model import LinearRegression

lidarGeneratedData = []


#lidarinput keeps distance to each point at each degree with step of 1 degree

def generateLine():
    print('generated random line')
    x0 = np.random.uniform(-5.0,5.0)
    y0 = np.random.uniform(-5.0,5.0)
    x1 = x0 + np.random.uniform(-10.0,10.0)
    y1 = y0 + np.random.uniform(-10.0, 10.0)
    xLowerLimit = np.random.uniform(-1.0,1.0)
    xUpperLimit = np.random.uniform(xLowerLimit, xLowerLimit+np.random.uniform(0, 50.0))
    twoPoints = [x0,y0,x1,y1,xLowerLimit,xUpperLimit] #x0,y0,x1,y1
    slope = (y1-y0)/(x1-x0)
    const = ((0 - x0) / (x1 - x0)) * (y1 - y0) + y0
    print(f'slope is {slope}')
    print(f'const is {const}')
    twoPoints.append(slope)
    twoPoints.append(const)
    #print(f"Generated points: {twoPoints}")
    #print(f"Func eq is: {slope}x + {const}")
    #print('')
    return twoPoints

twoPoints = generateLine()
print(f'twoPoints is {twoPoints}')
print(f'limits are {twoPoints[5], twoPoints[6]}')
#print(twoPoints)

#def randFunc(x):
#    print(twoPoints[4] , x[0] , twoPoints[5])
#    if twoPoints[4]<x[0]<twoPoints[5]:
#        x0 = twoPoints[0]
#        y0 = twoPoints[1]
#        x1 = twoPoints[2]
#        y1 = twoPoints[3]
#        func = ((x[0] - x0) / (x1 - x0)) * (y1 - y0) + y0
#        return func
#    else:
#        return "out of bounds"
#
#
#def angleFunc(alpha, x):
#    y = -alpha[0] + 90
#    func  = np.tan(y)*x
#    return (func)
#
#def difFunc(alpha, x):
#    func =  randFunc(x[0])-angleFunc(alpha, x[0])
#    return func
#
#def sqDifFunc(alpha, x):
#    func = difFunc(alpha, x[0])**2
#    return func
#
#xIntersection = opt.minimize(sqDifFunc, [0], options={'eps': 0.1})
#print(xIntersection)

def findIntersections():
    intersectionsX = []
    b = twoPoints[7]
    k = twoPoints[6]
    print(f'b is {b}')
    print(f'k is {k}')
    for i in range (360):
        j = -i + 90 #angle in normal coords
        if -90<=j<=90:
            j = radians(j)
            if (tan(j) != k):
                xIntersect = b / (tan(j) - k)
                if twoPoints[4] < xIntersect < twoPoints[5] and xIntersect>=0:
                    xIntersect = xIntersect
                    # intersectionsX.append([i,xIntersect])
                    intersectionsX.append([i, xIntersect])
                else:
                    intersectionsX.append([i, None])
                    # intersectionsX.append([i,'none'])
        if j< -90:
            j = radians(j)
            if (tan(j) != k):
                xIntersect = b / (tan(j) - k)
                if twoPoints[4] < xIntersect < twoPoints[5] and xIntersect < 0:
                    xIntersect = xIntersect
                    # intersectionsX.append([i,xIntersect])
                    intersectionsX.append([i, xIntersect])
                else:
                    intersectionsX.append([i, None])
                    # intersectionsX.append([i,'none'])
    return intersectionsX

intersectionsX = findIntersections()

#pointx = [3]
#print(f"Func value in point {pointx} is: {randFunc(pointx)}")
print('')
print(f'Intersection points of lidar with obstacles are: {intersectionsX}')
print(len(intersectionsX))

for unit in intersectionsX:
    alpha = unit[0]
    lengthX = unit[1]
    if lengthX is not None and sin(radians(alpha))!=0:
        lengthR = lengthX/sin(radians(alpha))
        lidarGeneratedData.append(round(lengthR,2))
    else:
        lidarGeneratedData.append(None)

print('')

def generateNoise(lidarGeneratedData):
    noisedData = np.array([])
    for datum in lidarGeneratedData:
        if datum is None:
            if np.random.uniform(0,100)<2:
                datum = np.random.uniform(0,100)
        else:
            datum += np.random.uniform(0,0.2)
        noisedData = np.append(noisedData, datum)

    #print(noisedData)

    return noisedData

noisedData  = generateNoise(lidarGeneratedData)


"""
THIS WAS THE INFORMATION GENERATION PART



FROM NOW ON, DATA ANALYSIS IS BEING IMPLEMENTED
"""
def data2coords(dist):
    overall = []
    xS = np.array([])
    yS = np.array([])
    c = 0

    for i in range (len(dist)):
        if dist[i] is not None:
            xCoordinate = dist[i]*sin(radians(i))
            xS = np.append(xS, xCoordinate)
            yCoordinate = dist[i]*cos(radians(i))
            yS = np.append(yS, yCoordinate)
    return  xS, yS


def LinesSplit(inputData):
    lines = []
    lineNum = 0
    inputData = np.append(inputData, inputData[0])
    inputData = np.insert(inputData,0, inputData[-2])
    flag = 1
    for i in range(1, len(inputData)-1):
        if inputData[i] is not None:
            if inputData[i+1] is not None or inputData[i-1] is not None:
                if flag == 1:
                    lines.append([])
                    flag = 0
                lines[-1].append([inputData[i],i - 1])
            else:
                lineNum +=1
                flag = 1
    if lines[0][0][1] == 0 and lines[-1][-1][1] == 359:
        for k in range(len(lines[0])):
            lines[-1].append(lines[0][k])
        lines.pop(0)

    return lines




def process_data(data):   #data is an array of length with each degree
    lines = LinesSplit(data)

    outData = []


    for line in lines:
        modelIntercepts = []
        modelCoefs = []
        xS = np.array([])
        yS = np.array([])
        lineNP = np.array(line)
        xS = np.append(xS, data2coords(lineNP)[0])
        yS = np.append(yS, data2coords(lineNP)[1])

        xS = np.array(xS).reshape(-1, 1)

        model = LinearRegression().fit(xS, yS)

        print(f'intercept: {model.intercept_}')
        modelIntercepts.append(model.intercept_)
        print(f'slope: {model.coef_}')
        modelCoefs.append(model.coef_[0])

        xLowerLimit = xS[0][0]
        xHigherLimit = xS[-1][0]

        outData.append([modelIntercepts,modelCoefs, xLowerLimit, xHigherLimit])

    print (f'modelIntercepts are {modelIntercepts}, modelCoefs are {modelCoefs}')
    print('')
    print(f'outData is {outData}')
    return outData

process_data(noisedData)