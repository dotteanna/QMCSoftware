from ._true_measure import TrueMeasure
from ..discrete_distribution import Sobol
from ..util import TransformError, ParameterError
from numpy import linspace, cumsum, sqrt, log2, ceil, \
    array, exp, array, dot, diff, argsort, diag, hstack
from scipy.stats import norm
from scipy.linalg import eigh
import warnings


class BrownianMotion(TrueMeasure):
    """
    Geometric Brownian Motion.
    
    >>> dd = Sobol(2,seed=7)
    >>> bm = BrownianMotion(dd,drift=1)
    >>> bm
    BrownianMotion (TrueMeasure Object)
        time_vector     [0.5 1. ]
        drift           1
        assembly_type   pca
    >>> bm.gen_samples(n_min=4,n_max=8)
    array([[ 1.383,  1.889],
           [ 0.019,  0.804],
           [ 0.655,  1.269],
           [ 0.64 , -0.758]])
    >>> bm.set_dimension(4)
    >>> bm
    BrownianMotion (TrueMeasure Object)
        time_vector     [0.25 0.5  0.75 1.  ]
        drift           1
        assembly_type   pca
    >>> bm.gen_samples(n_min=2,n_max=4)
    array([[-0.261, -0.156,  0.13 ,  0.794],
           [ 0.436,  0.961,  1.761,  1.351]])
    """

    parameters = ['time_vector','drift','assembly_type']

    def __init__(self, distribution, assembly_type='PCA', drift=0.):
        """
        Args:
            distribution (DiscreteDistribution): DiscreteDistribution instance
            assembly_type (str): assembly type type either 
                "Diff" for time differencing, 
                "PCA" for principal component analysis, or
                "Bridge" for Brownian Bridge.
            drift (float): mean shift for importance sampling. 
        """
        self.distribution = distribution
        self.assembly_type = assembly_type.lower()
        if self.assembly_type not in ['diff','pca','bridge']:
            raise ParameterError('Brownian Motion assembly_type parameter must be either "Diff", "PCA", or "Bridge"')
        self.drift = float(drift)
        self.d = self.distribution.dimension
        self._assemble()
        self.t = 1. # exercise time
        super(BrownianMotion,self).__init__()
    
    def _assemble(self):
        """ Set parameters dependent on the dimension. """
        self.time_vector = linspace(1./self.d,1,self.d) # evenly spaced
        self.ms_vec = self.drift * self.time_vector
        if self.assembly_type == 'diff':
            self.time_diff = diff(hstack((0,self.time_vector)))
        elif self.assembly_type == 'pca':
            sigma = array([[min(self.time_vector[i],self.time_vector[j])
                        for i in range(self.d)]
                        for j in range(self.d)])
            evals,evecs = eigh(sigma) # get eigenvectors and eigenvalues for
            order = argsort(-evals)
            self.a = dot(evecs[:,order],diag(sqrt(evals[order])))
        elif self.assembly_type == 'bridge':
            n_pow2 = 2**ceil(log2(self.d))
            self.time_diff = diff(hstack((0,self.time_vector)))
            sobol = Sobol(dimension=1, randomize=False, graycode=False)
            seq = sobol.gen_samples(n=n_pow2).squeeze()[:self.d]
            self.order = argsort(seq)

    def _tf_to_mimic_samples(self, samples):
        """
        Transform samples to appear BrownianMotion.
        
        Args:
            samples (ndarray): samples from a discrete distribution
        
        Return:
            ndarray: samples from the DiscreteDistribution transformed to mimic the Brownain Motion.
        """
        # transform samples to appear standard Gaussian
        if self.distribution.mimics == 'StdGaussian':
            std_gaussian_samples = samples
        elif self.distribution.mimics == "StdUniform":
            std_gaussian_samples = norm.ppf(samples)
        else:
            raise TransformError(\
                'Cannot transform samples mimicing %s to Brownian Motion'%self.distribution.mimics)
        # generate Brownian Motion paths
        if self.assembly_type == 'diff':
            paths = cumsum(sqrt(self.time_diff)*std_gaussian_samples,1)
        elif self.assembly_type == 'pca':
            paths = dot(std_gaussian_samples,self.a.T)
        elif self.assembly_type == 'bridge':
            paths = cumsum(sqrt(self.time_diff)*std_gaussian_samples[:,self.order],1)
        is_paths = paths + self.ms_vec # add drift shift for importance sampling
        return is_paths

    def transform_g_to_f(self, g):
        """ See abstract method. """
        def f(samples, *args, **kwargs):
            z = self._tf_to_mimic_samples(samples)
            y = g(z,*args,**kwargs) * exp( (self.drift*self.t/2. - z[:,-1]) * self.drift)
            return y
        return f
    
    def gen_samples(self, *args, **kwargs):
        """ See abstract method. """
        samples = self.distribution.gen_samples(*args,**kwargs)
        mimic_samples = self._tf_to_mimic_samples(samples)
        return mimic_samples
    
    def set_dimension(self, dimension):
        """
        See abstract method. 
        
        Note:
            Monitoring times are evenly spaced as linspace(1/dimension,1,dimension)
        """
        self.distribution.set_dimension(dimension)
        self.d = dimension
        self._assemble()
