from discreteDistribution import discreteDistribution
import numpy as np
import sys
import randomstate.prng.mrg32k3a as rnd

# Specifies and generates the components of $\frac 1n \sum_{i=1}^n \delta_{\vx_i}(\cdot)$
# where the $\vx_i$ are IID uniform on $[0,1]^d$ or IID standard Gaussian
class IIDDistribution(discreteDistribution):

    def __init__(self):
        self.distribData
        super().__init__()

    @property
    def distribData(self):
        return []

    @property
    def state(self):
        return []

    @property
    def nStreams(self):
        return 1

    def initStreams(self, nStreams = 1):
        self.distribDataStream = list(range(nStreams))
        for x in range(nStreams):
            self.distribDataStream[x] = rnd.RandomState()

        #self.distribData.stream = RandStream.create('mrg32k3a', 'NumStreams', nStreams, 'CellOutput', True)
        return self

    def genDistrib(self, nStart, nEnd, n, coordIndex, streamIndex=0):
        nPts = nEnd - nStart + 1  # how many points to be generated

        if self.trueDistribution == 'uniform': # generate uniform points
            x = self.distribDataStream[streamIndex].rand(int(nPts), len(coordIndex))  # nodes
        else:  # standard normal points
            x = self.distribDataStream[streamIndex].randn(int(nPts), len(coordIndex))  # nodes

        # Code without streams

        w = 1
        a = 1 / n

        return x, w, a

if __name__ == "__main__":
    import doctest
    x = doctest.testfile("dt_IIDDistribution.py")
    print("\n"+str(x))
    
