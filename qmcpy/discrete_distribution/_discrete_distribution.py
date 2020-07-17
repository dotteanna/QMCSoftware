from ..util import ParameterError, MethodImplementationError, _univ_repr, DimensionError
from numpy import array


class DiscreteDistribution(object):
    """ Discrete Distribution abstract class. DO NOT INSTANTIATE. """

    def __init__(self):
        prefix = 'A concrete implementation of DiscreteDistribution must have '
        if not hasattr(self, 'mimics'):
            raise ParameterError(prefix + 'self.mimcs (measure mimiced by the distribution)')
        if not hasattr(self, 'dimension'):
            raise ParameterError(prefix + 'self.dimension')
        if not hasattr(self,'parameters'):
            self.parameters = []

    def gen_samples(self, *args):
        """
        ABSTRACT METHOD Generate samples from discrete distribution. 
        
        Args:
            args (tuple): tuple of positional argument. See implementations for details
        Returns:
            ndarray: n x d array of samples
        """
        raise MethodImplementationError(self, 'gen_samples')

    def set_dimension(self, dimension):
        """
        ABSTRACT METHOD to reset the dimension of the problem.
        
        Args:
            dimension (int): new dimension to reset to
        
        Note:
            May not be applicable to every discrete distribution (ex: CustomIIDDistribution). 
        """
        raise DimensionError("Cannot reset dimension of %s object"%str(type(self).__name__))
    
    def set_seed(self, seed):
        """ 
        ABSTRACT METHOD to reset the seed of the problem.

        Args: 
            seed (int): new seed for generator
        
        Note:
            May not be applicable to every discrete distribution (ex: InverseCDFSampling)
        """
        raise MethodImplementationError(self, 'set_seed')

    def __repr__(self):
        return _univ_repr(self, "DiscreteDistribution", self.parameters)
