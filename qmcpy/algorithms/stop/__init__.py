''' Originally developed in MATLAB by Fred Hickernell. Translated to python by Sou-Cheng T. Choi and Aleksei Sorokin '''
from abc import ABC, abstractmethod

from .. import univ_repr

class DistributionCompatibilityError(Exception): pass

class stoppingCriterion(ABC):
    '''
    Decide when to stop
        Any sublcass of stoppingCriterion must include:
            Methods: stopYet(self,distribObj) 
            Properties: discDistAllowed  
    '''
    
    def __init__(self,distribObj,discDistAllowed,absTol,relTol,nInit,nMax): 
        if type(distribObj).__name__ not in discDistAllowed:
                raise DistributionCompatibilityError(type(self).__name__+' only accepts distributions:'+str(discDistAllowed))
        super().__init__()
        self.absTol = absTol if absTol else 1e-2 # absolute tolerance, Â§$\mcommentfont d$Â§
        self.relTol = relTol if relTol else 0 # relative tolerance, Â§$\mcommentfont d$Â§
        self.nInit = nInit if nInit else 1024 # initial sample size
        self.nMax = nMax if nMax else 1e8 # maximum number of samples allowed
        
    # Abstract Methods
    @abstractmethod
    def stopYet(self,distribObj): # distribObj = data or summary of data computed already
        pass
    
    # Magic Methods
    def __repr__(self): return univ_repr(self)