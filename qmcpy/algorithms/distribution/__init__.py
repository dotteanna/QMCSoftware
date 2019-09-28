''' Originally developed in MATLAB by Fred Hickernell. Translated to python by Sou-Cheng T. Choi and Aleksei Sorokin '''
from abc import ABC, abstractmethod
from numpy import array, arange

from .. import univ_repr

class MeasureCompatibilityError(Exception): pass

class discreteDistribution(ABC):
    '''
    Specifies and generates the components of §$\mcommentfont a_n \sum_{i=1}^n w_i \delta_{\vx_i}(\cdot)$
        Any sublcass of discreteDistribution must include:
            Methods: genDistrib(self,nStart,nEnd,n,coordIndex)
            Properties: distribData,trueD
    '''
    def __init__(self,accepted_measures,trueD=None,distribData=None):
        super().__init__()
        # Abstract Properties
        self.distribData = distribData
        self.trueD = trueD   
        self.distrib_list = [self]
        
        # Create self.distrib_list (self) and distribute attributes
        if trueD:
            if trueD.measureName not in accepted_measures:
                raise MeasureCompatibilityError(type(self).__name__+' only accepts measures:'+str(accepted_measures))
            self.distrib_list = [type(self)() for i in range(len(trueD))]
            for i in range(len(self)):    
                self[i].trueD = self.trueD[i]
                self[i].distribData = self.distribData[i] if self.distribData else None          

    # Abstract Methods
    @abstractmethod
    def genDistrib(self,n,m,j):
        """
         nStart = starting value of §$\mcommentfont i$§
         nEnd = ending value of §$\mcommentfont i$§
         n = value of §$\mcommentfont n$§ used to determine §$\mcommentfont a_n$§
         coordIndex = which coordinates in sequence are needed
        """
        pass
    
    # Magic Methods. Makes self[i]==self.distrib_list[i]
    def __len__(self): return len(self.distrib_list)
    def __iter__(self):
        for distribObj in self.distrib_list:
            yield distribObj
    def __getitem__(self,i): return self.distrib_list[i]
    def __setitem__(self,i,val): self.distrib_list[i]=val
    def __repr__(self): return univ_repr(self,'distrib_list')


class measure():
    '''
    Specifies the components of a general measure used to define an
    integration problem or a sampling method
    '''
    
    def __init__(self,domainShape='',domainCoord=None,measureData=None):  
        # Argument Parsing
        #    Shape of the domain
        if domainShape in ['','box','cube','unitCube']: self.domainShape = domainShape
        else: raise Exception("measure.domainShape must be one of: ['','box','cube','unitCube']")
        #   TypeCast to numpy ndarray's
        self.domainCoord = array(domainCoord) if domainCoord else array([])
        self.measureData = measureData if measureData else {}
        self.measure_list = []

    ''' Methods to construct list of measures ''' 
    def stdUniform(self,dimension=array([2])):
        ''' create standard uniform measure '''
        self.measureName = 'stdUniform'
        #    Dimension of the domain, Â§$\mcommentfont d$Â§
        if type(dimension)==int: self.dimension = array([dimension])
        elif all(item>0 for item in dimension): self.dimension = array(dimension)
        else: raise Exception("measure.dimension must be a list of positive integers")
        #    Construct list of measures
        self.measure_list = list(range(len(dimension)))
        for i in range(len(self.measure_list)):
            self.measure_list[i] = measure()
            self.measure_list[i].dimension = self.dimension[i]
            self.measure_list[i].measureName = 'stdUniform'
        return self

    def stdGaussian(self,dimension=array([2])):
        ''' create standard Gaussian measure '''
        self.measureName = 'stdGaussian'
        #    Dimension of the domain, Â§$\mcommentfont d$Â§
        if type(dimension)==int: self.dimension = array([dimension])
        elif all(item>0 for item in dimension): self.dimension = array(dimension)
        else: raise Exception("measure.dimension be a list of positive integers")
        #    Construct list of measures
        self.measure_list = list(range(len(dimension)))
        for i in range(len(self.measure_list)):
            self.measure_list[i] = measure()
            self.measure_list[i].dimension = self.dimension[i]
            self.measure_list[i].measureName = 'stdGaussian'
        return self

    def IIDZMeanGaussian(self,dimension=array([2]),variance=array([1])):
        ''' create standard Gaussian measure '''
        self.measureName = 'IIDZMeanGaussian'
         #    Dimension of the domain, Â§$\mcommentfont d$Â§
        if type(dimension)==int: self.dimension = array([dimension])
        elif all(item>0 for item in dimension): self.dimension = array(dimension)
        else: raise Exception("measure.dimension be a list of positive integers")
        #    Variance of Gaussian Measures
        if type(variance)==int: variance = array([variance])
        elif all(item>0 for item in variance): variance = array(variance)
        else: raise Exception("measure.variance be a list of positive integers")
        #    Construct list of measures
        self.measure_list = list(range(len(dimension)))
        for i in range(len(self.measure_list)):
            self.measure_list[i] = measure()
            self.measure_list[i].dimension = self.dimension[i]
            self.measure_list[i].measureData['variance'] = variance[i]
            self.measure_list[i].measureName = 'IIDZMeanGaussian'
        return self

    def BrownianMotion(self,timeVector=arange(1/4,5/4,1/4)):
        ''' create a discretized Brownian Motion measure '''
        self.measureName = 'BrownianMotion'
        #    Dimension of domain, Â§$\mcommentfont d$Â§
        self.dimension = array([len(tV) for tV in timeVector])
        #    Construct list of measures
        self.measure_list = list(range(len(timeVector)))
        for i in range(len(self.measure_list)): 
            self.measure_list[i] = measure()
            self.measure_list[i].measureData['timeVector'] = array(timeVector[i])
            self.measure_list[i].dimension = self.dimension[i]
            self.measure_list[i].measureName = 'BrownianMotion'
        return self
    
    def lattice(self,dimension=array([2])):
        ''' low descrepancy lattice '''
        self.measureName = 'lattice'
        #    Dimension of the domain, Â§$\mcommentfont d$Â§
        if type(dimension)==int: self.dimension = array([dimension])
        elif all(item>0 for item in dimension): self.dimension = array(dimension)
        else: raise Exception("measure.dimension be a list of positive integers")
        #    Construct list of measures
        self.measure_list = list(range(len(dimension)))
        for i in range(len(self.measure_list)):
            self.measure_list[i] = measure()
            self.measure_list[i].measureData['lds_type'] = 'lattice'
            self.measure_list[i].dimension = self.dimension[i]
            self.measure_list[i].measureName = 'stdUniform'
        return self

    def Sobol(self,dimension=array([2])):
        ''' low descrepancy Sobol '''
        self.measureName = 'Sobol'
        #    Dimension of the domain, Â§$\mcommentfont d$Â§
        if type(dimension)==int: self.dimension = array([dimension])
        elif all(item>0 for item in dimension): self.dimension = array(dimension)
        else: raise Exception("measure.dimension be a list of positive integers")
        #    Construct list of measures
        self.measure_list = list(range(len(dimension)))
        for i in range(len(self.measure_list)):
            self.measure_list[i] = measure()
            self.measure_list[i].measureData['lds_type'] = 'Sobol'
            self.measure_list[i].dimension = self.dimension[i]
            self.measure_list[i].measureName = 'stdUniform'
        return self

    # Magic Methods. Makes self[i]==self.measure_list[i]
    def __len__(self): return len(self.measure_list)
    def __iter__(self):
        for measureObj in self.measure_list:
            yield measureObj
    def __getitem__(self,i): return self.measure_list[i]
    def __setitem__(self,i,val): self.measure_list[i] = val
    def __repr__(self): return univ_repr(self,'measure_list')
