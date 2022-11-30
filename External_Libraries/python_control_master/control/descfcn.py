# descfcn.py - describing function analysis
#
# RMM, 23 Jan 2021
#
# This module adds functions for carrying out analysis of systems with
# memoryless nonlinear feedback functions using describing functions.
#

"""The :mod:~control.descfcn` module contains function for performing
closed loop analysis of systems with memoryless nonlinearities using
describing function analysis.

"""

import math
import numpy as np
import matplotlib.pyplot as plt
import scipy
from warnings import warn

from .freqplot import nyquist_plot

__all__ = ['describing_function', 'describing_function_plot',
           'DescribingFunctionNonlinearity', 'friction_backlash_nonlinearity',
           'relay_hysteresis_nonlinearity', 'saturation_nonlinearity']

# Class for nonlinearities with a built-in describing function
class DescribingFunctionNonlinearity():
    """Base class for nonlinear systems with a describing function.

    This class is intended to be used as a base class for nonlinear functions
    that have an analytically defined describing function.  Subclasses should
    override the `__call__` and `describing_function` methods and (optionally)
    the `_isstatic` method (should be `False` if `__call__` updates the
    instance state).

    """
    def __init__(self):
        """Initailize a describing function nonlinearity (optional)."""
        pass

    def __call__(self, A):
        """Evaluate the nonlinearity at a (scalar) input value."""
        raise NotImplementedError(
            "__call__() not implemented for this function (internal error)")

    def describing_function(self, A):
        """Return the describing function for a nonlinearity.

        This method is used to allow analytical representations of the
        describing function for a nonlinearity.  It turns the (complex) value
        of the describing function for sinusoidal input of amplitude `A`.

        """
        raise NotImplementedError(
            "describing function not implemented for this function")

    def _isstatic(self):
        """Return True if the function has no internal state (memoryless).

        This internal function is used to optimize numerical computation of
        the describing function.  It can be set to `True` if the instance
        maintains no internal memory of the instance state.  Assumed False by
        default.

        """
        return False

    # Utility function used to compute common describing functions
    def _f(self, x):
        return math.copysign(1, x) if abs(x) > 1 else \
            (math.asin(x) + x * math.sqrt(1 - x**2)) * 2 / math.pi


def describing_function(
        F, A, num_points=100, zero_check=True, try_method=True):
    """Numerical compute the describing function of a nonlinear function

    The describing function of a nonlinearity is given by magnitude and phase
    of the first harmonic of the function when evaluated along a sinusoidal
    input :math:`A \\sin \\omega t`.  This function returns the magnitude and
    phase of the describing function at amplitude :math:`A`.

    Parameters
    ----------
    F : callable
        The function F() should accept a scalar number as an argument and
        return a scalar number.  For compatibility with (static) nonlinear
        input/output systems, the output can also return a 1D array with a
        single element.

        If the function is an object with a method `describing_function`
        then this method will be used to computing the describing function
        instead of a nonlinear computation.  Some common nonlinearities
        use the :class:`~control.DescribingFunctionNonlinearity` class,
        which provides this functionality.

    A : array_like
        The amplitude(s) at which the describing function should be calculated.

    zero_check : bool, optional
        If `True` (default) then `A` is zero, the function will be evaluated
        and checked to make sure it is zero.  If not, a `TypeError` exception
        is raised.  If zero_check is `False`, no check is made on the value of
        the function at zero.

    try_method : bool, optional
        If `True` (default), check the `F` argument to see if it is an object
        with a `describing_function` method and use this to compute the
        describing function.  More information in the `describing_function`
        method for the :class:`~control.DescribingFunctionNonlinearity` class.

    Returns
    -------
    df : array of complex
        The (complex) value of the describing function at the given amplitudes.

    Raises
    ------
    TypeError
        If A[i] < 0 or if A[i] = 0 and the function F(0) is non-zero.

    """
    # If there is an analytical solution, trying using that first
    if try_method and hasattr(F, 'describing_function'):
        try:
            return np.vectorize(F.describing_function, otypes=[complex])(A)
        except NotImplementedError:
            # Drop through and do the numerical computation
            pass

    #
    # The describing function of a nonlinear function F() can be computed by
    # evaluating the nonlinearity over a sinusoid.  The Fourier series for a
    # static nonlinear function evaluated on a sinusoid can be written as
    #
    # F(A\sin\omega t) = \sum_{k=1}^\infty M_k(A) \sin(k\omega t + \phi_k(A))
    #
    # The describing function is given by the complex number
    #
    #    N(A) = M_1(A) e^{j \phi_1(A)} / A
    #
    # To compute this, we compute F(A \sin\theta) for \theta between 0 and 2
    # \pi, use the identities
    #
    #   \sin(\theta + \phi) = \sin\theta \cos\phi + \cos\theta \sin\phi
    #   \int_0^{2\pi} \sin^2 \theta d\theta = \pi
    #   \int_0^{2\pi} \cos^2 \theta d\theta = \pi
    #
    # and then integrate the product against \sin\theta and \cos\theta to obtain
    #
    #   \int_0^{2\pi} F(A\sin\theta) \sin\theta d\theta = M_1 \pi \cos\phi
    #   \int_0^{2\pi} F(A\sin\theta) \cos\theta d\theta = M_1 \pi \sin\phi
    #
    # From these we can compute M1 and \phi.
    #

    # Evaluate over a full range of angles (leave off endpoint a la DFT)
    theta, dtheta = np.linspace(
        0, 2*np.pi, num_points, endpoint=False, retstep=True)
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    # See if this is a static nonlinearity (assume not, just in case)
    if not hasattr(F, '_isstatic') or not F._isstatic():
        # Initialize any internal state by going through an initial cycle
        for x in np.atleast_1d(A).min() * sin_theta:
            F(x)                # ignore the result

    # Go through all of the amplitudes we were given
    retdf = np.empty(np.shape(A), dtype=complex)
    df = retdf                  # Access to the return array
    df.shape = (-1, )           # as a 1D array
    for i, a in enumerate(np.atleast_1d(A)):
        # Make sure we got a valid argument
        if a == 0:
            # Check to make sure the function has zero output with zero input
            if zero_check and np.squeeze(F(0.)) != 0:
                raise ValueError("function must evaluate to zero at zero")
            df[i] = 1.
            continue
        elif a < 0:
            raise ValueError("cannot evaluate describing function for A < 0")

        # Save the scaling factor to make the formulas simpler
        scale = dtheta / np.pi / a

        # Evaluate the function along a sinusoid
        F_eval = np.array([F(x) for x in a*sin_theta]).squeeze()

        # Compute the prjections onto sine and cosine
        df_real = (F_eval @ sin_theta) * scale     # = M_1 \cos\phi / a
        df_imag = (F_eval @ cos_theta) * scale     # = M_1 \sin\phi / a

        df[i] = df_real + 1j * df_imag

    # Return the values in the same shape as they were requested
    return retdf


def describing_function_plot(
        H, F, A, omega=None, refine=True, label="%5.2g @ %-5.2g",
        warn=None, **kwargs):
    """Plot a Nyquist plot with a describing function for a nonlinear system.

    This function generates a Nyquist plot for a closed loop system consisting
    of a linear system with a static nonlinear function in the feedback path.

    Parameters
    ----------
    H : LTI system
        Linear time-invariant (LTI) system (state space, transfer function, or
        FRD)
    F : static nonlinear function
        A static nonlinearity, either a scalar function or a single-input,
        single-output, static input/output system.
    A : list
        List of amplitudes to be used for the describing function plot.
    omega : list, optional
        List of frequencies to be used for the linear system Nyquist curve.
    label : str, optional
        Formatting string used to label intersection points on the Nyquist
        plot.  Defaults to "%5.2g @ %-5.2g".  Set to `None` to omit labels.
    warn : bool, optional
        Set to True to turn on warnings generated by `nyquist_plot` or False
        to turn off warnings.  If not set (or set to None), warnings are
        turned off if omega is specified, otherwise they are turned on.

    Returns
    -------
    intersections : 1D array of 2-tuples or None
        A list of all amplitudes and frequencies in which :math:`H(j\\omega)
        N(a) = -1`, where :math:`N(a)` is the describing function associated
        with `F`, or `None` if there are no such points.  Each pair represents
        a potential limit cycle for the closed loop system with amplitude
        given by the first value of the tuple and frequency given by the
        second value.

    Example
    -------
    >>> H_simple = ct.tf([8], [1, 2, 2, 1])
    >>> F_saturation = ct.descfcn.saturation_nonlinearity(1)
    >>> amp = np.linspace(1, 4, 10)
    >>> ct.describing_function_plot(H_simple, F_saturation, amp)
    [(3.344008947853124, 1.414213099755523)]

    """
    # Decide whether to turn on warnings or not
    if warn is None:
        # Turn warnings on unless omega was specified
        warn = omega is None

    # Start by drawing a Nyquist curve
    count, contour = nyquist_plot(
        H, omega, plot=True, return_contour=True,
        warn_encirclements=warn, warn_nyquist=warn, **kwargs)
    H_omega, H_vals = contour.imag, H(contour)

    # Compute the describing function
    df = describing_function(F, A)
    N_vals = -1/df

    # Now add the describing function curve to the plot
    plt.plot(N_vals.real, N_vals.imag)

    # Look for intersection points
    intersections = []
    for i in range(N_vals.size - 1):
        for j in range(H_vals.size - 1):
            intersect = _find_intersection(
                N_vals[i], N_vals[i+1], H_vals[j], H_vals[j+1])
            if intersect == None:
                continue

            # Found an intersection, compute a and omega
            s_amp, s_omega = intersect
            a_guess = (1 - s_amp) * A[i] + s_amp * A[i+1]
            omega_guess = (1 - s_omega) * H_omega[j] + s_omega * H_omega[j+1]

            # Refine the coarse estimate to get better intersection point
            a_final, omega_final = a_guess, omega_guess
            if refine:
                # Refine the answer to get more accuracy
                def _cost(x):
                    # If arguments are invalid, return a "large" value
                    # Note: imposing bounds messed up the optimization (?)
                    if x[0] < 0 or x[1] < 0:
                        return 1
                    return abs(1 + H(1j * x[1]) *
                               describing_function(F, x[0]))**2
                res = scipy.optimize.minimize(
                    _cost, [a_guess, omega_guess])
                # bounds=[(A[i], A[i+1]), (H_omega[j], H_omega[j+1])])

                if not res.success:
                    warn("not able to refine result; returning estimate")
                else:
                    a_final, omega_final = res.x[0], res.x[1]

            # Add labels to the intersection points
            if isinstance(label, str):
                pos = H(1j * omega_final)
                plt.text(pos.real, pos.imag, label % (a_final, omega_final))
            elif label is not None or label is not False:
                raise ValueError("label must be formatting string or None")

            # Save the final estimate
            intersections.append((a_final, omega_final))

    return intersections


# Utility function to figure out whether two line segments intersection
def _find_intersection(L1a, L1b, L2a, L2b):
    # Compute the tangents for the segments
    L1t = L1b - L1a
    L2t = L2b - L2a

    # Set up components of the solution: b = M s
    b = L1a - L2a
    detM = L1t.imag * L2t.real - L1t.real * L2t.imag
    if abs(detM) < 1e-8:        # TODO: fix magic number
        return None

    # Solve for the intersection points on each line segment
    s1 = (L2t.imag * b.real - L2t.real * b.imag) / detM
    if s1 < 0 or s1 > 1:
        return None

    s2 = (L1t.imag * b.real - L1t.real * b.imag) / detM
    if s2 < 0 or s2 > 1:
        return None

    # Debugging test
    # np.testing.assert_almost_equal(L1a + s1 * L1t, L2a + s2 * L2t)

    # Intersection is within segments; return proportional distance
    return (s1, s2)


# Saturation nonlinearity
class saturation_nonlinearity(DescribingFunctionNonlinearity):
    """Create saturation nonlinearity for use in describing function analysis.

    This class creates a nonlinear function representing a saturation with
    given upper and lower bounds, including the describing function for the
    nonlinearity.  The following call creates a nonlinear function suitable
    for describing function analysis:

        F = saturation_nonlinearity(ub[, lb])

    By default, the lower bound is set to the negative of the upper bound.
    Asymmetric saturation functions can be created, but note that these
    functions will not have zero bias and hence care must be taken in using
    the nonlinearity for analysis.

    """
    def __init__(self, ub=1, lb=None):
        # Create the describing function nonlinearity object
        super(saturation_nonlinearity, self).__init__()

        # Process arguments
        if lb == None:
            # Only received one argument; assume symmetric around zero
            lb, ub = -abs(ub), abs(ub)

        # Make sure the bounds are sensible
        if lb > 0 or ub < 0 or lb + ub != 0:
            warn("asymmetric saturation; ignoring non-zero bias term")

        self.lb = lb
        self.ub = ub

    def __call__(self, x):
        return np.clip(x, self.lb, self.ub)

    def _isstatic(self):
        return True

    def describing_function(self, A):
        # Check to make sure the amplitude is positive
        if A < 0:
            raise ValueError("cannot evaluate describing function for A < 0")

        if self.lb <= A and A <= self.ub:
            return 1.
        else:
            alpha, beta = math.asin(self.ub/A), math.asin(-self.lb/A)
            return (math.sin(alpha + beta) * math.cos(alpha - beta) +
                    (alpha + beta)) / math.pi


# Relay with hysteresis (FBS2e, Example 10.12)
class relay_hysteresis_nonlinearity(DescribingFunctionNonlinearity):
    """Relay w/ hysteresis nonlinearity for describing function analysis.

    This class creates a nonlinear function representing a a relay with
    symmetric upper and lower bounds of magnitude `b` and a hysteretic region
    of width `c` (using the notation from [FBS2e](https://fbsbook.org),
    Example 10.12, including the describing function for the nonlinearity.
    The following call creates a nonlinear function suitable for describing
    function analysis:

        F = relay_hysteresis_nonlinearity(b, c)

    The output of this function is `b` if `x > c` and `-b` if `x < -c`.  For
    `-c <= x <= c`, the value depends on the branch of the hysteresis loop (as
    illustrated in Figure 10.20 of FBS2e).

    """
    def __init__(self, b, c):
        # Create the describing function nonlinearity object
        super(relay_hysteresis_nonlinearity, self).__init__()

        # Initialize the state to bottom branch
        self.branch = -1        # lower branch
        self.b = b              # relay output value
        self.c = c              # size of hysteresis region

    def __call__(self, x):
        if x > self.c:
            y = self.b
            self.branch = 1
        elif x < -self.c:
            y = -self.b
            self.branch = -1
        elif self.branch == -1:
            y = -self.b
        elif self.branch == 1:
            y = self.b
        return y

    def _isstatic(self):
        return False

    def describing_function(self, A):
        # Check to make sure the amplitude is positive
        if A < 0:
            raise ValueError("cannot evaluate describing function for A < 0")

        if A < self.c:
            return np.nan

        df_real = 4 * self.b * math.sqrt(1 - (self.c/A)**2) / (A * math.pi)
        df_imag = -4 * self.b * self.c / (math.pi * A**2)
        return df_real + 1j * df_imag


# Friction-dominated backlash nonlinearity (#48 in Gelb and Vander Velde, 1968)
class friction_backlash_nonlinearity(DescribingFunctionNonlinearity):
    """Backlash nonlinearity for describing function analysis.

    This class creates a nonlinear function representing a friction-dominated
    backlash nonlinearity ,including the describing function for the
    nonlinearity.  The following call creates a nonlinear function suitable
    for describing function analysis:

        F = friction_backlash_nonlinearity(b)

    This function maintains an internal state representing the 'center' of a
    mechanism with backlash.  If the new input is within `b/2` of the current
    center, the output is unchanged.  Otherwise, the output is given by the
    input shifted by `b/2`.

    """

    def __init__(self, b):
        # Create the describing function nonlinearity object
        super(friction_backlash_nonlinearity, self).__init__()

        self.b = b              # backlash distance
        self.center = 0         # current center position

    def __call__(self, x):
        # If we are outside the backlash, move and shift the center
        if x - self.center > self.b/2:
            self.center = x - self.b/2
        elif x - self.center < -self.b/2:
            self.center = x + self.b/2
        return self.center

    def _isstatic(self):
        return False

    def describing_function(self, A):
        # Check to make sure the amplitude is positive
        if A < 0:
            raise ValueError("cannot evaluate describing function for A < 0")

        if A <= self.b/2:
            return 0

        df_real = (1 + self._f(1 - self.b/A)) / 2
        df_imag = -(2 * self.b/A - (self.b/A)**2) / math.pi
        return df_real + 1j * df_imag
