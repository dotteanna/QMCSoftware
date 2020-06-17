from ._true_measure import TrueMeasure
from ..util import TransformError,DimensionError
from ..discrete_distribution import Sobol
from numpy import array, sqrt, eye, dot, pi, exp,dot, tile, isscalar, diag
from numpy.linalg import cholesky, det, inv
from scipy.stats import norm


class Gaussian(TrueMeasure):
    """
    Normal Measure.
    
    >>> dd = Sobol(2,seed=7)
    >>> g = Gaussian(dd,mean=1,covariance=1./4)
    >>> g
    Gaussian (TrueMeasure Object)
        distrib_name    Sobol
        mean            1
        covariance      0.2500
    >>> g.gen_mimic_samples(n_min=4,n_max=8)
    array([[ 1.533,  0.676],
           [ 0.817,  1.351],
           [ 1.136,  1.011],
           [ 0.379, -0.194]])
    >>> g.set_dimension(4)
    >>> g.gen_mimic_samples(n_min=2,n_max=4)
    array([[ 1.309,  0.445,  1.128,  0.813],
           [ 0.634,  1.171,  0.362,  1.528]])
    >>> g2 = Gaussian(Sobol(2),mean=[1,2],covariance=[[1,.5],[.5,2]])
    >>> g2
    Gaussian (TrueMeasure Object)
        distrib_name    Sobol
        mean            [1 2]
        covariance      [[ 1.000  0.500]
                        [ 0.500  2.000]]
    >>> g2.pdf(array([0,0]))
    array([[ 0.027]])
    """

    parameters = ['mean', 'covariance']

    def __init__(self, distribution, mean=0, covariance=1):
        """
        Args:
            distribution (DiscreteDistribution): DiscreteDistribution instance
            mean (float): mu for Normal(mu,sigma^2)
            covariance (ndarray): sigma^2 for Normal(mu,sigma^2). 
                A float or d (dimension) vector input will be extended to covariance*eye(d)
        """
        self.distribution = distribution
        self.d = distribution.dimension
        self.mean = mean
        self.covariance = covariance
        if isscalar(mean):
            mean = tile(mean,self.d)
        if isscalar(covariance):
            covariance = covariance*eye(self.d)
        self.mu = array(mean)
        self.sigma2 = array(covariance)
        if self.sigma2.shape==(self.d,):
            self.sigma2 = diag(self.sigma2)
        if not (len(self.mu)==self.d and self.sigma2.shape==(self.d,self.d)):
            raise DimensionError("mean must have length dimension and "+\
                "covariance must be of shapre dimension x dimension")
        self.sigma = cholesky(self.sigma2)
        super().__init__()
    
    def pdf(self, x):
        """ See abstract method. """
        x = x.reshape(self.d,1)
        mu = self.mu.reshape(self.d,1)
        density = (2*pi)**(-self.d/2) * det(self.sigma)**(-1/2) * \
            exp(-1/2 *  dot( dot((x-mu).T,inv(self.sigma)), x-mu) )
        return density

    def _tf_to_mimic_samples(self, samples):
        """
        Transform samples to appear Gaussian
        
        Args:
            samples (ndarray): samples from a discrete distribution
        
        Return:
            ndarray: samples from the DiscreteDistribution transformed to mimic Gaussian.
        """
        if self.distribution.mimics == 'StdGaussian':
            # shift and stretch
            mimic_samples = self.mu + dot(samples,self.sigma)
        elif self.distribution.mimics == "StdUniform":
            # inverse CDF then shift and stretch
            mimic_samples = self.mu + dot(norm.ppf(samples),self.sigma)
        else:
            raise TransformError(\
                'Cannot transform samples mimicing %s to Gaussian'%self.distribution.mimics)
        return mimic_samples

    def transform_g_to_f(self, g):
        """ See abstract method. """
        def f(samples, *args, **kwargs):
            z = self._tf_to_mimic_samples(samples)
            y = g(z, *args, **kwargs)
            return y
        return f
    
    def gen_mimic_samples(self, *args, **kwargs):
        """ See abstract method. """
        samples = self.distribution.gen_samples(*args,**kwargs)
        mimic_samples = self._tf_to_mimic_samples(samples)
        return mimic_samples

    def set_dimension(self, dimension):
        """ See abstract method. """
        m = self.mu[0]
        c = self.sigma2[0,0]
        expected_cov = c*eye(self.d)
        if not (all(self.mu==m) and (self.sigma2==expected_cov).all()):
            raise DimensionError('In order to change dimension of Gaussian measure '+\
                'mean (mu) must be all the same and covariance must be a scaler times I')
        self.distribution.set_dimension(dimension)
        self.d = dimension
        self.mu = tile(m,self.d)
        self.sigma2 = c*eye(self.d)
        self.sigma = cholesky(self.sigma2)