"""statesp_test.py - test state space class

RMM, 30 Mar 2011 based on TestStateSp from v0.4a)
RMM, 14 Jun 2019 statesp_array_test.py coverted from statesp_test.py to test
                 with use_numpy_matrix(False)
BG,  26 Jul 2020 merge statesp_array_test.py differences into statesp_test.py
                 convert to pytest
"""

import numpy as np
from numpy.testing import assert_array_almost_equal
import pytest
import operator
from numpy.linalg import solve
from scipy.linalg import block_diag, eigvals

import control as ct
from control.config import defaults
from control.dtime import sample_system
from control.lti import evalfr
from control.statesp import StateSpace, _convert_to_statespace, tf2ss, \
    _statesp_defaults, _rss_generate, linfnorm
from control.iosys import ss, rss, drss
from control.tests.conftest import ismatarrayout, slycotonly
from control.xferfcn import TransferFunction, ss2tf


from .conftest import editsdefaults


class TestStateSpace:
    """Tests for the StateSpace class."""

    @pytest.fixture
    def sys322ABCD(self):
        """Matrices for sys322"""
        A322 = [[-3., 4., 2.],
                [-1., -3., 0.],
                [2., 5., 3.]]
        B322 = [[1., 4.],
                [-3., -3.],
                [-2., 1.]]
        C322 = [[4., 2., -3.],
                [1., 4., 3.]]
        D322 = [[-2., 4.],
                [0., 1.]]
        return (A322, B322, C322, D322)

    @pytest.fixture
    def sys322(self, sys322ABCD):
        """3-states square system (2 inputs x 2 outputs)"""
        return StateSpace(*sys322ABCD)

    @pytest.fixture
    def sys121(self):
        """2 state, 1 input, 1 output (siso)  system"""
        A121 = [[4., 1.],
                [2., -3]]
        B121 = [[5.],
                [-3.]]
        C121 = [[2., -4]]
        D121 = [[3.]]
        return StateSpace(A121, B121, C121, D121)

    @pytest.fixture
    def sys222(self):
        """2-states square system (2 inputs x 2 outputs)"""
        A222 = [[4., 1.],
                [2., -3]]
        B222 = [[5., 2.],
                [-3., -3.]]
        C222 = [[2., -4],
                [0., 1.]]
        D222 = [[3., 2.],
                [1., -1.]]
        return StateSpace(A222, B222, C222, D222)

    @pytest.fixture
    def sys623(self):
        """sys3: 6 states non square system (2 inputs x 3 outputs)"""
        A623 = np.array([[1, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, 0, 0],
                         [0, 0, 3, 0, 0, 0],
                         [0, 0, 0, -4, 0, 0],
                         [0, 0, 0, 0, -1, 0],
                         [0, 0, 0, 0, 0, 3]])
        B623 = np.array([[0, -1],
                        [-1, 0],
                        [1, -1],
                        [0, 0],
                        [0, 1],
                        [-1, -1]])
        C623 = np.array([[1, 0, 0, 1, 0, 0],
                         [0, 1, 0, 1, 0, 1],
                         [0, 0, 1, 0, 0, 1]])
        D623 = np.zeros((3, 2))
        return StateSpace(A623, B623, C623, D623)

    @pytest.mark.parametrize(
        "dt",
        [(), (None, ), (0, ), (1, ), (0.1, ), (True, )],
        ids=lambda i: "dt " + ("unspec" if len(i) == 0 else str(i[0])))
    @pytest.mark.parametrize(
        "argfun",
        [pytest.param(
            lambda ABCDdt: (ABCDdt, {}),
            id="A, B, C, D[, dt]"),
         pytest.param(
            lambda ABCDdt: (ABCDdt[:4], {'dt': dt_ for dt_ in ABCDdt[4:]}),
            id="A, B, C, D[, dt=dt]"),
         pytest.param(
             lambda ABCDdt: ((StateSpace(*ABCDdt), ), {}),
             id="sys")
         ])
    def test_constructor(self, sys322ABCD, dt, argfun):
        """Test different ways to call the StateSpace() constructor"""
        args, kwargs = argfun(sys322ABCD + dt)
        sys = StateSpace(*args, **kwargs)

        dtref = defaults['control.default_dt'] if len(dt) == 0 else dt[0]
        np.testing.assert_almost_equal(sys.A, sys322ABCD[0])
        np.testing.assert_almost_equal(sys.B, sys322ABCD[1])
        np.testing.assert_almost_equal(sys.C, sys322ABCD[2])
        np.testing.assert_almost_equal(sys.D, sys322ABCD[3])
        assert sys.dt == dtref

    @pytest.mark.parametrize("args, exc, errmsg",
                             [((True, ), TypeError,
                               "(can only take in|sys must be) a StateSpace"),
                              ((1, 2), TypeError, "1, 4, or 5 arguments"),
                              ((np.ones((3, 2)), np.ones((3, 2)),
                                np.ones((2, 2)), np.ones((2, 2))),
                               ValueError, "A must be square"),
                              ((np.ones((3, 3)), np.ones((2, 2)),
                                np.ones((2, 3)), np.ones((2, 2))),
                               ValueError, "A and B"),
                              ((np.ones((3, 3)), np.ones((3, 2)),
                                np.ones((2, 2)), np.ones((2, 2))),
                               ValueError, "A and C"),
                              ((np.ones((3, 3)), np.ones((3, 2)),
                                np.ones((2, 3)), np.ones((2, 3))),
                               ValueError, "B and D"),
                              ((np.ones((3, 3)), np.ones((3, 2)),
                                np.ones((2, 3)), np.ones((3, 2))),
                               ValueError, "C and D"),
                              ])
    def test_constructor_invalid(self, args, exc, errmsg):
        """Test invalid input to StateSpace() constructor"""
        with pytest.raises(exc, match=errmsg):
            StateSpace(*args)
        with pytest.raises(exc, match=errmsg):
            ss(*args)

    def test_constructor_warns(self, sys322ABCD):
        """Test ambiguos input to StateSpace() constructor"""
        with pytest.warns(UserWarning, match="received multiple dt"):
            sys = StateSpace(*(sys322ABCD + (0.1, )), dt=0.2)
            np.testing.assert_almost_equal(sys.A, sys322ABCD[0])
        np.testing.assert_almost_equal(sys.B, sys322ABCD[1])
        np.testing.assert_almost_equal(sys.C, sys322ABCD[2])
        np.testing.assert_almost_equal(sys.D, sys322ABCD[3])
        assert sys.dt == 0.1

    def test_copy_constructor(self):
        """Test the copy constructor"""
        # Create a set of matrices for a simple linear system
        A = np.array([[-1]])
        B = np.array([[1]])
        C = np.array([[1]])
        D = np.array([[0]])

        # Create the first linear system and a copy
        linsys = StateSpace(A, B, C, D)
        cpysys = StateSpace(linsys)

        # Change the original A matrix
        A[0, 0] = -2
        np.testing.assert_allclose(linsys.A, [[-1]])  # original value
        np.testing.assert_allclose(cpysys.A, [[-1]])  # original value

        # Change the A matrix for the original system
        linsys.A[0, 0] = -3
        np.testing.assert_allclose(cpysys.A, [[-1]])  # original value

    @pytest.mark.skip("obsolete test")
    def test_copy_constructor_nodt(self, sys322):
        """Test the copy constructor when an object without dt is passed"""
        sysin = sample_system(sys322, 1.)
        del sysin.dt            # this is a nonsensical thing to do
        sys = StateSpace(sysin)
        assert sys.dt == defaults['control.default_dt']

        # test for static gain
        sysin = StateSpace([], [], [], [[1, 2], [3, 4]], 1.)
        del sysin.dt            # this is a nonsensical thing to do
        sys = StateSpace(sysin)
        assert sys.dt is None

    def test_matlab_style_constructor(self):
        """Use (deprecated) matrix-style construction string"""
        with pytest.deprecated_call():
            sys = StateSpace("-1 1; 0 2", "0; 1", "1, 0", "0")
        assert sys.A.shape == (2, 2)
        assert sys.B.shape == (2, 1)
        assert sys.C.shape == (1, 2)
        assert sys.D.shape == (1, 1)
        for X in [sys.A, sys.B, sys.C, sys.D]:
            assert ismatarrayout(X)

    def test_D_broadcast(self, sys623):
        """Test broadcast of D=0 to the right shape"""
        # Giving D as a scalar 0 should broadcast to the right shape
        sys = StateSpace(sys623.A, sys623.B, sys623.C, 0)
        np.testing.assert_allclose(sys623.D, sys.D)

        # Giving D as a matrix of the wrong size should generate an error
        with pytest.raises(ValueError):
            sys = StateSpace(sys.A, sys.B, sys.C, np.array([[0]]))

        # Make sure that empty systems still work
        sys = StateSpace([], [], [], 1)
        np.testing.assert_allclose(sys.D, [[1]])

        sys = StateSpace([], [], [], [[0]])
        np.testing.assert_allclose(sys.D, [[0]])

        sys = StateSpace([], [], [], [0])
        np.testing.assert_allclose(sys.D, [[0]])

        sys = StateSpace([], [], [], 0)
        np.testing.assert_allclose(sys.D, [[0]])

    def test_pole(self, sys322):
        """Evaluate the poles of a MIMO system."""

        p = np.sort(sys322.poles())
        true_p = np.sort([3.34747678408874,
                          -3.17373839204437 + 1.47492908003839j,
                          -3.17373839204437 - 1.47492908003839j])

        np.testing.assert_array_almost_equal(p, true_p)

    def test_zero_empty(self):
        """Test to make sure zero() works with no zeros in system."""
        sys = _convert_to_statespace(TransferFunction([1], [1, 2, 1]))
        np.testing.assert_array_equal(sys.zeros(), np.array([]))

    @slycotonly
    def test_zero_siso(self, sys222):
        """Evaluate the zeros of a SISO system."""
        # extract only first input / first output system of sys222. This system is denoted sys111
        #  or tf111
        tf111 = ss2tf(sys222)
        sys111 = tf2ss(tf111[0, 0])

        # compute zeros as root of the characteristic polynomial at the numerator of tf111
        # this method is simple and assumed as valid in this test
        true_z = np.sort(tf111[0, 0].zeros())
        # Compute the zeros through ab08nd, which is tested here
        z = np.sort(sys111.zeros())

        np.testing.assert_almost_equal(true_z, z)

    @slycotonly
    def test_zero_mimo_sys322_square(self, sys322):
        """Evaluate the zeros of a square MIMO system."""

        z = np.sort(sys322.zeros())
        true_z = np.sort([44.41465, -0.490252, -5.924398])
        np.testing.assert_array_almost_equal(z, true_z)

    @slycotonly
    def test_zero_mimo_sys222_square(self, sys222):
        """Evaluate the zeros of a square MIMO system."""

        z = np.sort(sys222.zeros())
        true_z = np.sort([-10.568501,   3.368501])
        np.testing.assert_array_almost_equal(z, true_z)

    @slycotonly
    def test_zero_mimo_sys623_non_square(self, sys623):
        """Evaluate the zeros of a non square MIMO system."""

        z = np.sort(sys623.zeros())
        true_z = np.sort([2., -1.])
        np.testing.assert_array_almost_equal(z, true_z)

    def test_add_ss(self, sys222, sys322):
        """Add two MIMO systems."""

        A = [[-3., 4., 2., 0., 0.], [-1., -3., 0., 0., 0.],
             [2., 5., 3., 0., 0.], [0., 0., 0., 4., 1.], [0., 0., 0., 2., -3.]]
        B = [[1., 4.], [-3., -3.], [-2., 1.], [5., 2.], [-3., -3.]]
        C = [[4., 2., -3., 2., -4.], [1., 4., 3., 0., 1.]]
        D = [[1., 6.], [1., 0.]]

        sys = sys322 + sys222

        np.testing.assert_array_almost_equal(sys.A, A)
        np.testing.assert_array_almost_equal(sys.B, B)
        np.testing.assert_array_almost_equal(sys.C, C)
        np.testing.assert_array_almost_equal(sys.D, D)

    def test_subtract_ss(self, sys222, sys322):
        """Subtract two MIMO systems."""

        A = [[-3., 4., 2., 0., 0.], [-1., -3., 0., 0., 0.],
             [2., 5., 3., 0., 0.], [0., 0., 0., 4., 1.], [0., 0., 0., 2., -3.]]
        B = [[1., 4.], [-3., -3.], [-2., 1.], [5., 2.], [-3., -3.]]
        C = [[4., 2., -3., -2., 4.], [1., 4., 3., 0., -1.]]
        D = [[-5., 2.], [-1., 2.]]

        sys = sys322 - sys222

        np.testing.assert_array_almost_equal(sys.A, A)
        np.testing.assert_array_almost_equal(sys.B, B)
        np.testing.assert_array_almost_equal(sys.C, C)
        np.testing.assert_array_almost_equal(sys.D, D)

    def test_multiply_ss(self, sys222, sys322):
        """Multiply two MIMO systems."""

        A = [[4., 1., 0., 0., 0.], [2., -3., 0., 0., 0.], [2., 0., -3., 4., 2.],
             [-6., 9., -1., -3., 0.], [-4., 9., 2., 5., 3.]]
        B = [[5., 2.], [-3., -3.], [7., -2.], [-12., -3.], [-5., -5.]]
        C = [[-4., 12., 4., 2., -3.], [0., 1., 1., 4., 3.]]
        D = [[-2., -8.], [1., -1.]]

        sys = sys322 * sys222

        np.testing.assert_array_almost_equal(sys.A, A)
        np.testing.assert_array_almost_equal(sys.B, B)
        np.testing.assert_array_almost_equal(sys.C, C)
        np.testing.assert_array_almost_equal(sys.D, D)

    @pytest.mark.parametrize("omega, resp",
                             [(1.,
                               np.array([[ 4.37636761e-05-0.01522976j,
                                          -7.92603939e-01+0.02617068j],
                                         [-3.31544858e-01+0.0576105j,
                                          1.28919037e-01-0.14382495j]])),
                              (32,
                               np.array([[-1.16548243e-05-3.13444825e-04j,
                                          -7.99936828e-01+4.54201816e-06j],
                                         [-3.00137118e-01+3.42881660e-03j,
                                          6.32015038e-04-1.21462255e-02j]]))])
    @pytest.mark.parametrize("dt", [None, 0, 1e-3])
    def test_call(self, dt, omega, resp):
        """Evaluate the frequency response at single frequencies"""
        A = [[-2, 0.5], [0.5, -0.3]]
        B = [[0.3, -1.3], [0.1, 0.]]
        C = [[0., 0.1], [-0.3, -0.2]]
        D = [[0., -0.8], [-0.3, 0.]]
        sys = StateSpace(A, B, C, D)

        if dt:
            sys = sample_system(sys, dt)
            s = np.exp(omega * 1j * dt)
        else:
            s = omega * 1j

        # Correct versions of the call
        np.testing.assert_allclose(evalfr(sys, s), resp, atol=1e-3)
        np.testing.assert_allclose(sys(s), resp, atol=1e-3)

        # Deprecated name of the call (should generate error)
        with pytest.raises(AttributeError):
            sys.evalfr(omega)


    @slycotonly
    def test_freq_resp(self):
        """Evaluate the frequency response at multiple frequencies."""

        A = [[-2, 0.5], [0.5, -0.3]]
        B = [[0.3, -1.3], [0.1, 0.]]
        C = [[0., 0.1], [-0.3, -0.2]]
        D = [[0., -0.8], [-0.3, 0.]]
        sys = StateSpace(A, B, C, D)

        true_mag = [[[0.0852992637230322, 0.00103596611395218],
                    [0.935374692849736, 0.799380720864549]],
                   [[0.55656854563842, 0.301542699860857],
                    [0.609178071542849, 0.0382108097985257]]]
        true_phase = [[[-0.566195599644593, -1.68063565332582],
                      [3.0465958317514, 3.14141384339534]],
                     [[2.90457947657161, 3.10601268291914],
                      [-0.438157380501337, -1.40720969147217]]]
        true_omega = [0.1, 10.]

        mag, phase, omega = sys.frequency_response(true_omega)

        np.testing.assert_almost_equal(mag, true_mag)
        np.testing.assert_almost_equal(phase, true_phase)
        np.testing.assert_almost_equal(omega, true_omega)

        # Deprecated version of the call (should return warning)
        with pytest.warns(DeprecationWarning, match="will be removed"):
            mag, phase, omega = sys.freqresp(true_omega)
            np.testing.assert_almost_equal(mag, true_mag)

    @slycotonly
    def test_minreal(self):
        """Test a minreal model reduction."""
        # A = [-2, 0.5, 0; 0.5, -0.3, 0; 0, 0, -0.1]
        A = [[-2, 0.5, 0], [0.5, -0.3, 0], [0, 0, -0.1]]
        # B = [0.3, -1.3; 0.1, 0; 1, 0]
        B = [[0.3, -1.3], [0.1, 0.], [1.0, 0.0]]
        # C = [0, 0.1, 0; -0.3, -0.2, 0]
        C = [[0., 0.1, 0.0], [-0.3, -0.2, 0.0]]
        # D = [0 -0.8; -0.3 0]
        D = [[0., -0.8], [-0.3, 0.]]
        # sys = ss(A, B, C, D)

        sys = StateSpace(A, B, C, D)
        sysr = sys.minreal()
        assert sysr.nstates == 2
        assert sysr.ninputs == sys.ninputs
        assert sysr.noutputs == sys.noutputs
        np.testing.assert_array_almost_equal(
            eigvals(sysr.A), [-2.136154, -0.1638459])

    def test_append_ss(self):
        """Test appending two state-space systems."""
        A1 = [[-2, 0.5, 0], [0.5, -0.3, 0], [0, 0, -0.1]]
        B1 = [[0.3, -1.3], [0.1, 0.], [1.0, 0.0]]
        C1 = [[0., 0.1, 0.0], [-0.3, -0.2, 0.0]]
        D1 = [[0., -0.8], [-0.3, 0.]]
        A2 = [[-1.]]
        B2 = [[1.2]]
        C2 = [[0.5]]
        D2 = [[0.4]]
        A3 = [[-2, 0.5, 0, 0], [0.5, -0.3, 0, 0], [0, 0, -0.1, 0],
              [0, 0, 0., -1.]]
        B3 = [[0.3, -1.3, 0], [0.1, 0., 0], [1.0, 0.0, 0], [0., 0, 1.2]]
        C3 = [[0., 0.1, 0.0, 0.0], [-0.3, -0.2, 0.0, 0.0], [0., 0., 0., 0.5]]
        D3 = [[0., -0.8, 0.], [-0.3, 0., 0.], [0., 0., 0.4]]
        sys1 = StateSpace(A1, B1, C1, D1)
        sys2 = StateSpace(A2, B2, C2, D2)
        sys3 = StateSpace(A3, B3, C3, D3)
        sys3c = sys1.append(sys2)
        np.testing.assert_array_almost_equal(sys3.A, sys3c.A)
        np.testing.assert_array_almost_equal(sys3.B, sys3c.B)
        np.testing.assert_array_almost_equal(sys3.C, sys3c.C)
        np.testing.assert_array_almost_equal(sys3.D, sys3c.D)

    def test_append_tf(self):
        """Test appending a state-space system with a tf"""
        A1 = [[-2, 0.5, 0], [0.5, -0.3, 0], [0, 0, -0.1]]
        B1 = [[0.3, -1.3], [0.1, 0.], [1.0, 0.0]]
        C1 = [[0., 0.1, 0.0], [-0.3, -0.2, 0.0]]
        D1 = [[0., -0.8], [-0.3, 0.]]
        s = TransferFunction([1, 0], [1])
        h = 1 / (s + 1) / (s + 2)
        sys1 = StateSpace(A1, B1, C1, D1)
        sys2 = _convert_to_statespace(h)
        sys3c = sys1.append(sys2)
        np.testing.assert_array_almost_equal(sys1.A, sys3c.A[:3, :3])
        np.testing.assert_array_almost_equal(sys1.B, sys3c.B[:3, :2])
        np.testing.assert_array_almost_equal(sys1.C, sys3c.C[:2, :3])
        np.testing.assert_array_almost_equal(sys1.D, sys3c.D[:2, :2])
        np.testing.assert_array_almost_equal(sys2.A, sys3c.A[3:, 3:])
        np.testing.assert_array_almost_equal(sys2.B, sys3c.B[3:, 2:])
        np.testing.assert_array_almost_equal(sys2.C, sys3c.C[2:, 3:])
        np.testing.assert_array_almost_equal(sys2.D, sys3c.D[2:, 2:])
        np.testing.assert_array_almost_equal(sys3c.A[:3, 3:], np.zeros((3, 2)))
        np.testing.assert_array_almost_equal(sys3c.A[3:, :3], np.zeros((2, 3)))

    def test_array_access_ss(self):

        sys1 = StateSpace([[1., 2.], [3., 4.]],
                          [[5., 6.], [6., 8.]],
                          [[9., 10.], [11., 12.]],
                          [[13., 14.], [15., 16.]], 1)

        sys1_11 = sys1[0, 1]
        np.testing.assert_array_almost_equal(sys1_11.A,
                                             sys1.A)
        np.testing.assert_array_almost_equal(sys1_11.B,
                                             sys1.B[:, 1:2])
        np.testing.assert_array_almost_equal(sys1_11.C,
                                             sys1.C[0:1, :])
        np.testing.assert_array_almost_equal(sys1_11.D,
                                             sys1.D[0, 1])

        assert sys1.dt == sys1_11.dt

    def test_dc_gain_cont(self):
        """Test DC gain for continuous-time state-space systems."""
        sys = StateSpace(-2., 6., 5., 0)
        np.testing.assert_allclose(sys.dcgain(), 15.)

        sys2 = StateSpace(-2, [6., 4.], [[5.], [7.], [11]], np.zeros((3, 2)))
        expected = np.array([[15., 10.], [21., 14.], [33., 22.]])
        np.testing.assert_allclose(sys2.dcgain(), expected)

        sys3 = StateSpace(0., 1., 1., 0.)
        np.testing.assert_equal(sys3.dcgain(), np.inf)

    def test_dc_gain_discr(self):
        """Test DC gain for discrete-time state-space systems."""
        # static gain
        sys = StateSpace([], [], [], 2, True)
        np.testing.assert_allclose(sys.dcgain(), 2)

        # averaging filter
        sys = StateSpace(0.5, 0.5, 1, 0, True)
        np.testing.assert_allclose(sys.dcgain(), 1)

        # differencer
        sys = StateSpace(0, 1, -1, 1, True)
        np.testing.assert_allclose(sys.dcgain(), 0)

        # summer
        sys = StateSpace(1, 1, 1, 0, True)
        np.testing.assert_equal(sys.dcgain(), np.inf)

    @pytest.mark.parametrize("outputs", range(1, 6))
    @pytest.mark.parametrize("inputs", range(1, 6))
    @pytest.mark.parametrize("dt", [None, 0, 1, True],
                             ids=["dtNone", "c", "dt1", "dtTrue"])
    def test_dc_gain_integrator(self, outputs, inputs, dt):
        """DC gain w/ pole at origin returns appropriately sized array of inf.

        the SISO case is also tested in test_dc_gain_{cont,discr}
        time systems (dt=0)
        """
        states = max(inputs, outputs)

        # a matrix that is singular at DC, and has no "useless" states as in
        # _remove_useless_states
        a = np.triu(np.tile(2, (states, states)))
        # eigenvalues all +2, except for ...
        a[0, 0] = 0 if dt in [0, None] else 1
        b = np.eye(max(inputs, states))[:states, :inputs]
        c = np.eye(max(outputs, states))[:outputs, :states]
        d = np.zeros((outputs, inputs))
        sys = StateSpace(a, b, c, d, dt)
        dc = np.full_like(d, np.inf, dtype=float)
        if sys.issiso():
            dc = dc.squeeze()

        try:
            np.testing.assert_array_equal(dc, sys.dcgain())
        except NotImplementedError:
            # Skip MIMO tests if there is no slycot
            pytest.skip("slycot required for MIMO dcgain")

    def test_scalar_static_gain(self):
        """Regression: can we create a scalar static gain?

        make sure StateSpace internals, specifically ABC matrix
        sizes, are OK for LTI operations
        """
        g1 = StateSpace([], [], [], [2])
        g2 = StateSpace([], [], [], [3])
        assert g1.dt == None
        assert g2.dt == None

        g3 = g1 * g2
        assert 6 == g3.D[0, 0]
        assert g3.dt == None

        g4 = g1 + g2
        assert 5 == g4.D[0, 0]
        assert g4.dt == None

        g5 = g1.feedback(g2)
        np.testing.assert_allclose(2. / 7, g5.D[0, 0])
        assert g5.dt == None

        g6 = g1.append(g2)
        np.testing.assert_allclose(np.diag([2, 3]), g6.D)
        assert g6.dt == None

    def test_matrix_static_gain(self):
        """Regression: can we create matrix static gains?"""
        d1 = np.array([[1, 2, 3], [4, 5, 6]])
        d2 = np.array([[7, 8], [9, 10], [11, 12]])
        g1 = StateSpace([], [], [], d1)

        # _remove_useless_states was making A = [[0]]
        assert (0, 0) == g1.A.shape

        g2 = StateSpace([], [], [], d2)
        g3 = StateSpace([], [], [], d2.T)

        h1 = g1 * g2
        np.testing.assert_allclose(d1 @ d2, h1.D)
        h2 = g1 + g3
        np.testing.assert_allclose(d1 + d2.T, h2.D)
        h3 = g1.feedback(g2)
        np.testing.assert_array_almost_equal(
            solve(np.eye(2) + d1 @ d2, d1), h3.D)
        h4 = g1.append(g2)
        np.testing.assert_allclose(block_diag(d1, d2), h4.D)

    def test_remove_useless_states(self):
        """Regression: _remove_useless_states gives correct ABC sizes."""
        g1 = StateSpace(np.zeros((3, 3)), np.zeros((3, 4)),
                        np.zeros((5, 3)), np.zeros((5, 4)),
                        remove_useless_states=True)
        assert (0, 0) == g1.A.shape
        assert (0, 4) == g1.B.shape
        assert (5, 0) == g1.C.shape
        assert (5, 4) == g1.D.shape
        assert 0 == g1.nstates

    @pytest.mark.parametrize("A, B, C, D",
                             [([1], [], [], [1]),
                              ([1], [1], [], [1]),
                              ([1], [], [1], [1]),
                              ([], [1], [], [1]),
                              ([], [1], [1], [1]),
                              ([], [], [1], [1]),
                              ([1], [1], [1], [])])
    def test_bad_empty_matrices(self, A, B, C, D):
        """Mismatched ABCD matrices when some are empty."""
        with pytest.raises(ValueError):
            StateSpace(A, B, C, D)


    def test_minreal_static_gain(self):
        """Regression: minreal on static gain was failing."""
        g1 = StateSpace([], [], [], [1])
        g2 = g1.minreal()
        np.testing.assert_array_equal(g1.A, g2.A)
        np.testing.assert_array_equal(g1.B, g2.B)
        np.testing.assert_array_equal(g1.C, g2.C)
        np.testing.assert_allclose(g1.D, g2.D)

    def test_empty(self):
        """Regression: can we create an empty StateSpace object?"""
        g1 = StateSpace([], [], [], [])
        assert 0 == g1.nstates
        assert 0 == g1.ninputs
        assert 0 == g1.noutputs

    def test_matrix_to_state_space(self):
        """_convert_to_statespace(matrix) gives ss([],[],[],D)"""
        with pytest.deprecated_call():
            D = np.matrix([[1, 2, 3], [4, 5, 6]])
        g = _convert_to_statespace(D)

        np.testing.assert_array_equal(np.empty((0, 0)), g.A)
        np.testing.assert_array_equal(np.empty((0, D.shape[1])), g.B)
        np.testing.assert_array_equal(np.empty((D.shape[0], 0)), g.C)
        np.testing.assert_allclose(D, g.D)

    def test_lft(self):
        """ test lft function with result obtained from matlab implementation"""
        # test case
        A = [[1, 2, 3],
             [1, 4, 5],
             [2, 3, 4]]
        B = [[0, 2],
             [5, 6],
             [5, 2]]
        C = [[1, 4, 5],
             [2, 3, 0]]
        D = [[0, 0],
             [3, 0]]
        P = StateSpace(A, B, C, D)
        Ak = [[0, 2, 3],
              [2, 3, 5],
              [2, 1, 9]]
        Bk = [[1, 1],
              [2, 3],
              [9, 4]]
        Ck = [[1, 4, 5],
              [2, 3, 6]]
        Dk = [[0, 2],
              [0, 0]]
        K = StateSpace(Ak, Bk, Ck, Dk)

        # case 1
        pk = P.lft(K, 2, 1)
        Amatlab = [1, 2, 3, 4, 6, 12, 1, 4, 5, 17, 38, 61, 2, 3, 4, 9, 26, 37,
                   2, 3, 0, 3, 14, 18, 4, 6, 0, 8, 27, 35, 18, 27, 0, 29, 109,
                   144]
        Bmatlab = [0, 10, 10, 7, 15, 58]
        Cmatlab = [1, 4, 5, 0, 0, 0]
        Dmatlab = [0]
        np.testing.assert_allclose(np.array(pk.A).reshape(-1), Amatlab)
        np.testing.assert_allclose(np.array(pk.B).reshape(-1), Bmatlab)
        np.testing.assert_allclose(np.array(pk.C).reshape(-1), Cmatlab)
        np.testing.assert_allclose(np.array(pk.D).reshape(-1), Dmatlab)

        # case 2
        pk = P.lft(K)
        Amatlab = [1, 2, 3, 4, 6, 12, -3, -2, 5, 11, 14, 31, -2, -3, 4, 3, 2,
                   7, 0.6, 3.4, 5, -0.6, -0.4, 0, 0.8, 6.2, 10, 0.2, -4.2,
                   -4, 7.4, 33.6, 45, -0.4, -8.6, -3]
        Bmatlab = []
        Cmatlab = []
        Dmatlab = []
        np.testing.assert_allclose(np.array(pk.A).reshape(-1), Amatlab)
        np.testing.assert_allclose(np.array(pk.B).reshape(-1), Bmatlab)
        np.testing.assert_allclose(np.array(pk.C).reshape(-1), Cmatlab)
        np.testing.assert_allclose(np.array(pk.D).reshape(-1), Dmatlab)

    def test_repr(self, sys322):
        """Test string representation"""
        ref322 = "\n".join(["StateSpace(array([[-3.,  4.,  2.],",
                            "       [-1., -3.,  0.],",
                            "       [ 2.,  5.,  3.]]), array([[ 1.,  4.],",
                            "       [-3., -3.],",
                            "       [-2.,  1.]]), array([[ 4.,  2., -3.],",
                            "       [ 1.,  4.,  3.]]), array([[-2.,  4.],",
                            "       [ 0.,  1.]]){dt})"])
        assert repr(sys322) == ref322.format(dt='')
        sysd = StateSpace(sys322.A, sys322.B,
                          sys322.C, sys322.D, 0.4)
        assert repr(sysd), ref322.format(dt=" == 0.4")
        array = np.array  # noqa
        sysd2 = eval(repr(sysd))
        np.testing.assert_allclose(sysd.A, sysd2.A)
        np.testing.assert_allclose(sysd.B, sysd2.B)
        np.testing.assert_allclose(sysd.C, sysd2.C)
        np.testing.assert_allclose(sysd.D, sysd2.D)

    def test_str(self, sys322):
        """Test that printing the system works"""
        tsys = sys322
        tref = ("A = [[-3.  4.  2.]\n"
                "     [-1. -3.  0.]\n"
                "     [ 2.  5.  3.]]\n"
                "\n"
                "B = [[ 1.  4.]\n"
                "     [-3. -3.]\n"
                "     [-2.  1.]]\n"
                "\n"
                "C = [[ 4.  2. -3.]\n"
                "     [ 1.  4.  3.]]\n"
                "\n"
                "D = [[-2.  4.]\n"
                "     [ 0.  1.]]\n")
        assert str(tsys) == tref
        tsysdtunspec = StateSpace(tsys.A, tsys.B, tsys.C, tsys.D, True)
        assert str(tsysdtunspec) == tref + "\ndt = True\n"
        sysdt1 = StateSpace(tsys.A, tsys.B, tsys.C, tsys.D, 1.)
        assert str(sysdt1) == tref + "\ndt = {}\n".format(1.)

    def test_pole_static(self):
        """Regression: poles() of static gain is empty array."""
        np.testing.assert_array_equal(np.array([]),
                                      StateSpace([], [], [], [[1]]).poles())

    def test_horner(self, sys322):
        """Test horner() function"""
        # Make sure we can compute the transfer function at a complex value
        sys322.horner(1. + 1.j)

        # Make sure result agrees with frequency response
        mag, phase, omega = sys322.frequency_response([1])
        np.testing.assert_array_almost_equal(
            np.squeeze(sys322.horner(1.j)),
            mag[:, :, 0] * np.exp(1.j * phase[:, :, 0]))

    @pytest.mark.parametrize('x',
        [[1, 1], [[1], [1]], np.atleast_2d([1,1]).T])
    @pytest.mark.parametrize('u', [0, 1, np.atleast_1d(2)])
    def test_dynamics_and_output_siso(self, x, u, sys121):
        uref = np.atleast_1d(u)
        assert_array_almost_equal(
            sys121.dynamics(0, x, u),
            (sys121.A @ x).reshape((-1,)) + (sys121.B @ uref).reshape((-1,)))
        assert_array_almost_equal(
            sys121.output(0, x, u),
            (sys121.C @ x).reshape((-1,)) + (sys121.D @ uref).reshape((-1,)))
        assert_array_almost_equal(
            sys121.dynamics(0, x),
            (sys121.A @ x).reshape((-1,)))
        assert_array_almost_equal(
            sys121.output(0, x),
            (sys121.C @ x).reshape((-1,)))

    # too few and too many states and inputs
    @pytest.mark.parametrize('x', [0, 1, [], [1, 2, 3], np.atleast_1d(2)])
    def test_error_x_dynamics_and_output_siso(self, x, sys121):
        with pytest.raises(ValueError):
            sys121.dynamics(0, x)
        with pytest.raises(ValueError):
            sys121.output(0, x)
    @pytest.mark.parametrize('u', [[1, 1], np.atleast_1d((2, 2))])
    def test_error_u_dynamics_output_siso(self, u, sys121):
        with pytest.raises(ValueError):
            sys121.dynamics(0, 1, u)
        with pytest.raises(ValueError):
            sys121.output(0, 1, u)

    @pytest.mark.parametrize('x',
        [[1, 1], [[1], [1]], np.atleast_2d([1,1]).T])
    @pytest.mark.parametrize('u',
        [[1, 1], [[1], [1]], np.atleast_2d([1,1]).T])
    def test_dynamics_and_output_mimo(self, x, u, sys222):
        assert_array_almost_equal(
            sys222.dynamics(0, x, u),
            (sys222.A @ x).reshape((-1,)) + (sys222.B @ u).reshape((-1,)))
        assert_array_almost_equal(
            sys222.output(0, x, u),
            (sys222.C @ x).reshape((-1,)) + (sys222.D @ u).reshape((-1,)))
        assert_array_almost_equal(
            sys222.dynamics(0, x),
            (sys222.A @ x).reshape((-1,)))
        assert_array_almost_equal(
            sys222.output(0, x),
            (sys222.C @ x).reshape((-1,)))

    # too few and too many states and inputs
    @pytest.mark.parametrize('x', [0, 1, [1, 1, 1]])
    def test_error_x_dynamics_mimo(self, x, sys222):
        with pytest.raises(ValueError):
            sys222.dynamics(0, x)
        with pytest.raises(ValueError):
            sys222.output(0, x)
    @pytest.mark.parametrize('u', [1, [1, 1, 1]])
    def test_error_u_dynamics_mimo(self, u, sys222):
        with pytest.raises(ValueError):
            sys222.dynamics(0, (1, 1), u)
        with pytest.raises(ValueError):
            sys222.output(0, (1, 1), u)
    
    def test_sample_named_signals(self):
        sysc = ct.StateSpace(1.1, 1, 1, 1, inputs='u', outputs='y', states='a')

        # Full form of the call
        sysd = sysc.sample(0.1, name='sampled')
        assert sysd.name == 'sampled'
        assert sysd.find_input('u') == 0
        assert sysd.find_output('y') == 0
        assert sysd.find_state('a') == 0

        # If we copy signal names w/out a system name, append '$sampled'
        sysd = sysc.sample(0.1)
        assert sysd.name == sysc.name + '$sampled'

        # If copy is False, signal names should not be copied
        sysd_nocopy = sysc.sample(0.1, copy_names=False)
        assert sysd_nocopy.find_input('u') is None
        assert sysd_nocopy.find_output('y') is None
        assert sysd_nocopy.find_state('a') is None

        # if signal names are provided, they should override those of sysc
        sysd_newnames = sysc.sample(0.1, inputs='v', outputs='x', states='b')
        assert sysd_newnames.find_input('v') == 0
        assert sysd_newnames.find_input('u') is None
        assert sysd_newnames.find_output('x') == 0
        assert sysd_newnames.find_output('y') is None
        assert sysd_newnames.find_state('b') == 0
        assert sysd_newnames.find_state('a') is None        
        # test just one name
        sysd_newnames = sysc.sample(0.1, inputs='v')
        assert sysd_newnames.find_input('v') == 0
        assert sysd_newnames.find_input('u') is None
        assert sysd_newnames.find_output('y') == 0
        assert sysd_newnames.find_output('x') is None
        
class TestRss:
    """These are tests for the proper functionality of statesp.rss."""

    # Maxmimum number of states to test + 1
    maxStates = 10
    # Maximum number of inputs and outputs to test + 1
    maxIO = 5

    @pytest.mark.parametrize('states', range(1, maxStates))
    @pytest.mark.parametrize('outputs', range(1, maxIO))
    @pytest.mark.parametrize('inputs', range(1, maxIO))
    def test_shape(self, states, outputs, inputs):
        """Test that rss outputs have the right state, input, and output size."""
        sys = rss(states, outputs, inputs)
        assert sys.nstates == states
        assert sys.ninputs == inputs
        assert sys.noutputs == outputs

    @pytest.mark.parametrize('states', range(1, maxStates))
    @pytest.mark.parametrize('outputs', range(1, maxIO))
    @pytest.mark.parametrize('inputs', range(1, maxIO))
    def test_pole(self, states, outputs, inputs):
        """Test that the poles of rss outputs have a negative real part."""
        sys = rss(states, outputs, inputs)
        p = sys.poles()
        for z in p:
            assert z.real < 0

    @pytest.mark.parametrize('strictly_proper', [True, False])
    def test_strictly_proper(self, strictly_proper):
        """Test that the strictly_proper argument returns a correct D."""
        for i in range(100):
            # The probability that drss(..., strictly_proper=False) returns an
            # all zero D 100 times in a row is 0.5**100 = 7.89e-31
            sys = rss(1, 1, 1, strictly_proper=strictly_proper)
            if np.all(sys.D == 0.) == strictly_proper:
                break
        assert np.all(sys.D == 0.) == strictly_proper

    @pytest.mark.parametrize('par, errmatch',
                             [((-1, 1, 1, 'c'), 'states must be'),
                              ((1, -1, 1, 'c'), 'inputs must be'),
                              ((1, 1, -1, 'c'), 'outputs must be'),
                              ((1, 1, 1, 'x'), 'cdtype must be'),
                              ])
    def test_rss_invalid(self, par, errmatch):
        """Test invalid inputs for rss() and drss()."""
        with pytest.raises(ValueError, match=errmatch):
            _rss_generate(*par)


class TestDrss:
    """These are tests for the proper functionality of statesp.drss."""

    # Maximum number of states to test + 1
    maxStates = 10
    # Maximum number of inputs and outputs to test + 1
    maxIO = 5

    @pytest.mark.parametrize('states', range(1, maxStates))
    @pytest.mark.parametrize('outputs', range(1, maxIO))
    @pytest.mark.parametrize('inputs', range(1, maxIO))
    def test_shape(self, states, outputs, inputs):
        """Test that drss outputs have the right state, input, and output size."""
        sys = drss(states, outputs, inputs)
        assert sys.nstates == states
        assert sys.ninputs == inputs
        assert sys.noutputs == outputs
        assert sys.dt is True

    @pytest.mark.parametrize('states', range(1, maxStates))
    @pytest.mark.parametrize('outputs', range(1, maxIO))
    @pytest.mark.parametrize('inputs', range(1, maxIO))
    def test_pole(self, states, outputs, inputs):
        """Test that the poles of drss outputs have less than unit magnitude."""
        sys = drss(states, outputs, inputs)
        p = sys.poles()
        for z in p:
            assert abs(z) < 1

    @pytest.mark.parametrize('strictly_proper', [True, False])
    def test_strictly_proper(self, strictly_proper):
        """Test that the strictly_proper argument returns a correct D."""
        for i in range(100):
            # The probability that drss(..., strictly_proper=False) returns an
            # all zero D 100 times in a row is 0.5**100 = 7.89e-31
            sys = drss(1, 1, 1, strictly_proper=strictly_proper)
            if np.all(sys.D == 0.) == strictly_proper:
                break
        assert np.all(sys.D == 0.) == strictly_proper


class TestLTIConverter:
    """Test returnScipySignalLTI method"""

    @pytest.fixture
    def mimoss(self, request):
        """Test system with various dt values"""
        n = 5
        m = 3
        p = 2
        bx, bu = np.mgrid[1:n + 1, 1:m + 1]
        cy, cx = np.mgrid[1:p + 1, 1:n + 1]
        dy, du = np.mgrid[1:p + 1, 1:m + 1]
        return StateSpace(np.eye(5) + np.eye(5, 5, 1),
                          bx * bu,
                          cy * cx,
                          dy * du,
                          request.param)

    @pytest.mark.parametrize("mimoss",
                             [None,
                              0,
                              0.1,
                              1,
                              True],
                             indirect=True)
    def test_returnScipySignalLTI(self, mimoss):
        """Test returnScipySignalLTI method with strict=False"""
        sslti = mimoss.returnScipySignalLTI(strict=False)
        for i in range(mimoss.noutputs):
            for j in range(mimoss.ninputs):
                np.testing.assert_allclose(sslti[i][j].A, mimoss.A)
                np.testing.assert_allclose(sslti[i][j].B, mimoss.B[:,
                                                                   j:j + 1])
                np.testing.assert_allclose(sslti[i][j].C, mimoss.C[i:i + 1,
                                                                   :])
                np.testing.assert_allclose(sslti[i][j].D, mimoss.D[i:i + 1,
                                                                   j:j + 1])
                if mimoss.dt == 0:
                    assert sslti[i][j].dt is None
                else:
                    assert sslti[i][j].dt == mimoss.dt

    @pytest.mark.parametrize("mimoss", [None], indirect=True)
    def test_returnScipySignalLTI_error(self, mimoss):
        """Test returnScipySignalLTI method with dt=None and strict=True"""
        with pytest.raises(ValueError):
            mimoss.returnScipySignalLTI()
        with pytest.raises(ValueError):
            mimoss.returnScipySignalLTI(strict=True)


class TestStateSpaceConfig:
    """Test the configuration of the StateSpace module"""

    @pytest.fixture
    def matarrayout(self):
        """Override autoused global fixture within this class"""
        pass

    def test_statespace_defaults(self, matarrayout):
        """Make sure the tests are run with the configured defaults"""
        for k, v in _statesp_defaults.items():
            assert defaults[k] == v, \
                "{} is {} but expected {}".format(k, defaults[k], v)


# test data for test_latex_repr below
LTX_G1 = ([[np.pi, 1e100], [-1.23456789, 5e-23]],
          [[0], [1]],
          [[987654321, 0.001234]],
          [[5]])

LTX_G2 = ([],
          [],
          [],
          [[1.2345, -2e-200], [-1, 0]])

LTX_G1_REF = {
    'p3_p' : '$$\n\\left(\\begin{array}{rllrll|rll}\n3.&\\hspace{-1em}14&\\hspace{-1em}\\phantom{\\cdot}&1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{100}&0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n-1.&\\hspace{-1em}23&\\hspace{-1em}\\phantom{\\cdot}&5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-23}&1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\hline\n9.&\\hspace{-1em}88&\\hspace{-1em}\\cdot10^{8}&0.&\\hspace{-1em}00123&\\hspace{-1em}\\phantom{\\cdot}&5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n$$',

    'p5_p' : '$$\n\\left(\\begin{array}{rllrll|rll}\n3.&\\hspace{-1em}1416&\\hspace{-1em}\\phantom{\\cdot}&1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{100}&0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n-1.&\\hspace{-1em}2346&\\hspace{-1em}\\phantom{\\cdot}&5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-23}&1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\hline\n9.&\\hspace{-1em}8765&\\hspace{-1em}\\cdot10^{8}&0.&\\hspace{-1em}001234&\\hspace{-1em}\\phantom{\\cdot}&5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n$$',

    'p3_s' : '$$\n\\begin{array}{ll}\nA = \\left(\\begin{array}{rllrll}\n3.&\\hspace{-1em}14&\\hspace{-1em}\\phantom{\\cdot}&1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{100}\\\\\n-1.&\\hspace{-1em}23&\\hspace{-1em}\\phantom{\\cdot}&5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-23}\\\\\n\\end{array}\\right)\n&\nB = \\left(\\begin{array}{rll}\n0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n\\\\\nC = \\left(\\begin{array}{rllrll}\n9.&\\hspace{-1em}88&\\hspace{-1em}\\cdot10^{8}&0.&\\hspace{-1em}00123&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n&\nD = \\left(\\begin{array}{rll}\n5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n\\end{array}\n$$',

    'p5_s' : '$$\n\\begin{array}{ll}\nA = \\left(\\begin{array}{rllrll}\n3.&\\hspace{-1em}1416&\\hspace{-1em}\\phantom{\\cdot}&1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{100}\\\\\n-1.&\\hspace{-1em}2346&\\hspace{-1em}\\phantom{\\cdot}&5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-23}\\\\\n\\end{array}\\right)\n&\nB = \\left(\\begin{array}{rll}\n0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n\\\\\nC = \\left(\\begin{array}{rllrll}\n9.&\\hspace{-1em}8765&\\hspace{-1em}\\cdot10^{8}&0.&\\hspace{-1em}001234&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n&\nD = \\left(\\begin{array}{rll}\n5\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n\\end{array}\n$$',
}

LTX_G2_REF = {
    'p3_p' : '$$\n\\left(\\begin{array}{rllrll}\n1.&\\hspace{-1em}23&\\hspace{-1em}\\phantom{\\cdot}&-2\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-200}\\\\\n-1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}&0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n$$',

    'p5_p' : '$$\n\\left(\\begin{array}{rllrll}\n1.&\\hspace{-1em}2345&\\hspace{-1em}\\phantom{\\cdot}&-2\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-200}\\\\\n-1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}&0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n$$',

    'p3_s' : '$$\n\\begin{array}{ll}\nD = \\left(\\begin{array}{rllrll}\n1.&\\hspace{-1em}23&\\hspace{-1em}\\phantom{\\cdot}&-2\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-200}\\\\\n-1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}&0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n\\end{array}\n$$',

    'p5_s' : '$$\n\\begin{array}{ll}\nD = \\left(\\begin{array}{rllrll}\n1.&\\hspace{-1em}2345&\\hspace{-1em}\\phantom{\\cdot}&-2\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\cdot10^{-200}\\\\\n-1\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}&0\\phantom{.}&\\hspace{-1em}&\\hspace{-1em}\\phantom{\\cdot}\\\\\n\\end{array}\\right)\n\\end{array}\n$$',
}

refkey_n = {None: 'p3', '.3g': 'p3', '.5g': 'p5'}
refkey_r = {None: 'p', 'partitioned': 'p', 'separate': 's'}

@pytest.mark.parametrize(" gmats,  ref",
                         [(LTX_G1, LTX_G1_REF),
                          (LTX_G2, LTX_G2_REF)])
@pytest.mark.parametrize("dt, dtref",
                         [(0, ""),
                          (None, ""),
                          (True, r"~,~dt=~\mathrm{{True}}"),
                          (0.1, r"~,~dt={dt:{fmt}}")])
@pytest.mark.parametrize("repr_type", [None, "partitioned", "separate"])
@pytest.mark.parametrize("num_format", [None, ".3g", ".5g"])
def test_latex_repr(gmats, ref, dt, dtref, repr_type, num_format, editsdefaults):
    """Test `._latex_repr_` with different config values

    This is a 'gold image' test, so if you change behaviour,
    you'll need to regenerate the reference results.
    Try something like:
        control.reset_defaults()
        print(f'p3_p : {g1._repr_latex_()!r}')
    """
    from control import set_defaults
    if num_format is not None:
        set_defaults('statesp', latex_num_format=num_format)

    if repr_type is not None:
        set_defaults('statesp', latex_repr_type=repr_type)

    g = StateSpace(*(gmats+(dt,)))
    refkey = "{}_{}".format(refkey_n[num_format], refkey_r[repr_type])
    dt_latex = dtref.format(dt=dt, fmt=defaults['statesp.latex_num_format'])
    ref_latex = ref[refkey][:-3] + dt_latex + ref[refkey][-3:]
    assert g._repr_latex_() == ref_latex


@pytest.mark.parametrize(
    "op",
    [pytest.param(getattr(operator, s), id=s) for s in ('add', 'sub', 'mul')])
@pytest.mark.parametrize(
    "tf, arr",
    [pytest.param(ct.tf([1], [0.5, 1]), np.array(2.), id="0D scalar"),
     pytest.param(ct.tf([1], [0.5, 1]), np.array([2.]), id="1D scalar"),
     pytest.param(ct.tf([1], [0.5, 1]), np.array([[2.]]), id="2D scalar")])
def test_xferfcn_ndarray_precedence(op, tf, arr):
    # Apply the operator to the transfer function and array
    ss = ct.tf2ss(tf)
    result = op(ss, arr)
    assert isinstance(result, ct.StateSpace)

    # Apply the operator to the array and transfer function
    ss = ct.tf2ss(tf)
    result = op(arr, ss)
    assert isinstance(result, ct.StateSpace)


def test_latex_repr_testsize(editsdefaults):
    # _repr_latex_ returns None when size > maxsize
    from control import set_defaults

    maxsize = defaults['statesp.latex_maxsize']
    nstates = maxsize // 2
    ninputs = maxsize - nstates
    noutputs = ninputs

    assert nstates > 0
    assert ninputs > 0

    g = rss(nstates, ninputs, noutputs)
    assert isinstance(g._repr_latex_(), str)

    set_defaults('statesp', latex_maxsize=maxsize - 1)
    assert g._repr_latex_() is None

    set_defaults('statesp', latex_maxsize=-1)
    assert g._repr_latex_() is None

    gstatic = ss([], [], [], 1)
    assert gstatic._repr_latex_() is None


class TestLinfnorm:
    # these are simple tests; we assume ab13dd is correct
    # python-control specific behaviour is:
    #   - checking for continuous- and discrete-time
    #   - scaling fpeak for discrete-time
    #   - handling static gains

    # the underdamped gpeak and fpeak are found from
    #   gpeak = 1/(2*zeta*(1-zeta**2)**0.5)
    #   fpeak = wn*(1-2*zeta**2)**0.5
    @pytest.fixture(params=[
        ('static', ct.tf, ([1.23],[1]), 1.23, 0),
        ('underdamped', ct.tf, ([100],[1, 2*0.5*10, 100]), 1.1547005, 7.0710678),
        ])
    def ct_siso(self, request):
        name, systype, sysargs, refgpeak, reffpeak = request.param
        return systype(*sysargs), refgpeak, reffpeak

    @pytest.fixture(params=[
        ('underdamped', ct.tf, ([100],[1, 2*0.5*10, 100]), 1e-4, 1.1547005, 7.0710678),
        ])
    def dt_siso(self, request):
        name, systype, sysargs, dt, refgpeak, reffpeak = request.param
        return ct.c2d(systype(*sysargs), dt), refgpeak, reffpeak

    @slycotonly
    def test_linfnorm_ct_siso(self, ct_siso):
        sys, refgpeak, reffpeak = ct_siso
        gpeak, fpeak = linfnorm(sys)
        np.testing.assert_allclose(gpeak, refgpeak)
        np.testing.assert_allclose(fpeak, reffpeak)

    @slycotonly
    def test_linfnorm_dt_siso(self, dt_siso):
        sys, refgpeak, reffpeak = dt_siso
        gpeak, fpeak = linfnorm(sys)
        # c2d pole-mapping has round-off
        np.testing.assert_allclose(gpeak, refgpeak)
        np.testing.assert_allclose(fpeak, reffpeak)

    @slycotonly
    def test_linfnorm_ct_mimo(self, ct_siso):
        siso, refgpeak, reffpeak = ct_siso
        sys = ct.append(siso, siso)
        gpeak, fpeak = linfnorm(sys)
        np.testing.assert_allclose(gpeak, refgpeak)
        np.testing.assert_allclose(fpeak, reffpeak)


@pytest.mark.parametrize("args, static", [
    (([], [], [], 1), True),       # ctime, empty state
    (([], [], [], 1, 1), True),    # dtime, empty state
    ((0, 0, 0, 1), False),         # ctime, unused state
    ((-1, 0, 0, 1), False),        # ctime, exponential decay
    ((-1, 0, 0, 0), False),        # ctime, no input, no output
    ((0, 0, 0, 1, 1), False),      # dtime, integrator
    ((1, 0, 0, 1, 1), False),      # dtime, unused state
    ((0, 0, 0, 1, None), False),   # unspecified, unused state
])
def test_isstatic(args, static):
    sys = ct.StateSpace(*args)
    assert sys._isstatic() == static

# Make sure that using params for StateSpace objects generates a warning
def test_params_warning():
    sys = StateSpace(-1, 1, 1, 0)

    with pytest.warns(UserWarning, match="params keyword ignored"):
        sys.dynamics(0, [0], [0], {'k': 5})

    with pytest.warns(UserWarning, match="params keyword ignored"):
        sys.output(0, [0], [0], {'k': 5})


