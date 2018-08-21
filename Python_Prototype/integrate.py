from time import time

def integrate(funObj, distribObj, stopCritObj, datObj=[]):
    """  Specify and generate values $f(\vx)$ for $\vx \in \cx$Â§
     funObj = an object from class fun
     distribObj = an object from class discrete_distribution
     stopcritObj = an object from class stopping_criterion
    """
    # Initialize the accumData object and other crucial objects
    [datObj, distribObj] = stopCritObj.stopYet(datObj, funObj, distribObj)
    while not datObj.stage == 'done': # the datObj.stage property tells us where we are in the process
        datObj.updateData(distribObj, funObj)  # compute additional data
        [datObj, distribObj] = stopCritObj.stopYet(datObj, funObj, distribObj)  # update the status of the computation
    solution = datObj.solution  # assign outputs
    datObj.timeUsed = time() - datObj.__timeStart__
    return solution, datObj


def print_dict(dict):
    for key, value in dict.items():
        print("%s: %s" % (key, value))

import addpath
addpath
from Keister import Keister as Keister
from IID import IID as IID
from CLT import CLT as CLT

trueVal = 0.425184685650728
funObj = Keister()
distribObj = IID()
stopObj = CLT()
[solution, datObj] = integrate(funObj, distribObj, stopObj)
print(solution)
print_dict(datObj.__dict__)
error = abs(solution-trueVal)
print("Error = %f, error < stop.absTol? %s\n" % (error, str(error < stopObj.absTol)))

stopObj.absTol = 1e-3
[solution, datObj] = integrate(funObj, distribObj, stopObj)
print(solution)
print_dict(datObj.__dict__)
error = abs(solution-trueVal)
print("Error = %f, error < stop.absTol? %s\n" % (error, str(error < stopObj.absTol)))


stopObj.absTol = 0
stopObj.nMax = 1e6
[solution, datObj] = integrate(funObj, distribObj, stopObj)
print(solution)
print_dict(datObj.__dict__)
error = abs(solution-trueVal)
print("Error = %f, datObj.nSamplesUsed <= stopObj.nMax? %s\n" % (error, str(datObj.nSamplesUsed <= stopObj.nMax)))