"""statefbk_test.py - test state feedback functions

RMM, 30 Mar 2011 (based on TestStatefbk from v0.4a)
"""

import numpy as np
import pytest

import control as ct
from control import lqe, dlqe, poles, rss, ss, tf
from control.exception import ControlDimension, ControlSlycot, \
    ControlArgument, slycot_check
from control.mateqn import care, dare
from control.statefbk import (ctrb, obsv, place, place_varga, lqr, dlqr,
                              gram, acker)
from control.tests.conftest import (slycotonly, check_deprecated_matrix,
                                    ismatarrayout, asmatarrayout)


@pytest.fixture
def fixedseed():
    """Get consistent test results"""
    np.random.seed(0)


class TestStatefbk:
    """Test state feedback functions"""

    # Maximum number of states to test + 1
    maxStates = 5
    # Maximum number of inputs and outputs to test + 1
    maxTries = 4
    # Set to True to print systems to the output.
    debug = False

    def testCtrbSISO(self, matarrayin, matarrayout):
        A = matarrayin([[1., 2.], [3., 4.]])
        B = matarrayin([[5.], [7.]])
        Wctrue = np.array([[5., 19.], [7., 43.]])

        with check_deprecated_matrix():
            Wc = ctrb(A, B)
        assert ismatarrayout(Wc)

        np.testing.assert_array_almost_equal(Wc, Wctrue)

    def testCtrbMIMO(self, matarrayin):
        A = matarrayin([[1., 2.], [3., 4.]])
        B = matarrayin([[5., 6.], [7., 8.]])
        Wctrue = np.array([[5., 6., 19., 22.], [7., 8., 43., 50.]])
        Wc = ctrb(A, B)
        np.testing.assert_array_almost_equal(Wc, Wctrue)

        # Make sure default type values are correct
        assert ismatarrayout(Wc)

    def testObsvSISO(self, matarrayin):
        A = matarrayin([[1., 2.], [3., 4.]])
        C = matarrayin([[5., 7.]])
        Wotrue = np.array([[5., 7.], [26., 38.]])
        Wo = obsv(A, C)
        np.testing.assert_array_almost_equal(Wo, Wotrue)

        # Make sure default type values are correct
        assert ismatarrayout(Wo)


    def testObsvMIMO(self, matarrayin):
        A = matarrayin([[1., 2.], [3., 4.]])
        C = matarrayin([[5., 6.], [7., 8.]])
        Wotrue = np.array([[5., 6.], [7., 8.], [23., 34.], [31., 46.]])
        Wo = obsv(A, C)
        np.testing.assert_array_almost_equal(Wo, Wotrue)

    def testCtrbObsvDuality(self, matarrayin):
        A = matarrayin([[1.2, -2.3], [3.4, -4.5]])
        B = matarrayin([[5.8, 6.9], [8., 9.1]])
        Wc = ctrb(A, B)
        A = np.transpose(A)
        C = np.transpose(B)
        Wo = np.transpose(obsv(A, C))
        np.testing.assert_array_almost_equal(Wc,Wo)

    @slycotonly
    def testGramWc(self, matarrayin, matarrayout):
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5., 6.], [7., 8.]])
        C = matarrayin([[4., 5.], [6., 7.]])
        D = matarrayin([[13., 14.], [15., 16.]])
        sys = ss(A, B, C, D)
        Wctrue = np.array([[18.5, 24.5], [24.5, 32.5]])

        with check_deprecated_matrix():
            Wc = gram(sys, 'c')

        assert ismatarrayout(Wc)
        np.testing.assert_array_almost_equal(Wc, Wctrue)

    @slycotonly
    def testGramRc(self, matarrayin):
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5., 6.], [7., 8.]])
        C = matarrayin([[4., 5.], [6., 7.]])
        D = matarrayin([[13., 14.], [15., 16.]])
        sys = ss(A, B, C, D)
        Rctrue = np.array([[4.30116263, 5.6961343], [0., 0.23249528]])
        Rc = gram(sys, 'cf')
        np.testing.assert_array_almost_equal(Rc, Rctrue)

    @slycotonly
    def testGramWo(self, matarrayin):
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5., 6.], [7., 8.]])
        C = matarrayin([[4., 5.], [6., 7.]])
        D = matarrayin([[13., 14.], [15., 16.]])
        sys = ss(A, B, C, D)
        Wotrue = np.array([[257.5, -94.5], [-94.5, 56.5]])
        Wo = gram(sys, 'o')
        np.testing.assert_array_almost_equal(Wo, Wotrue)

    @slycotonly
    def testGramWo2(self, matarrayin):
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5.], [7.]])
        C = matarrayin([[6., 8.]])
        D = matarrayin([[9.]])
        sys = ss(A,B,C,D)
        Wotrue = np.array([[198., -72.], [-72., 44.]])
        Wo = gram(sys, 'o')
        np.testing.assert_array_almost_equal(Wo, Wotrue)

    @slycotonly
    def testGramRo(self, matarrayin):
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5., 6.], [7., 8.]])
        C = matarrayin([[4., 5.], [6., 7.]])
        D = matarrayin([[13., 14.], [15., 16.]])
        sys = ss(A, B, C, D)
        Rotrue = np.array([[16.04680654, -5.8890222], [0., 4.67112593]])
        Ro = gram(sys, 'of')
        np.testing.assert_array_almost_equal(Ro, Rotrue)

    def testGramsys(self):
        num =[1.]
        den = [1., 1., 1.]
        sys = tf(num,den)
        with pytest.raises(ValueError):
            gram(sys, 'o')
        with pytest.raises(ValueError):
            gram(sys, 'c')

    def testAcker(self, fixedseed):
        for states in range(1, self.maxStates):
            for i in range(self.maxTries):
                # start with a random SS system and transform to TF then
                # back to SS, check that the matrices are the same.
                sys = rss(states, 1, 1)
                if (self.debug):
                    print(sys)

                # Make sure the system is not degenerate
                Cmat = ctrb(sys.A, sys.B)
                if np.linalg.matrix_rank(Cmat) != states:
                    if (self.debug):
                        print("  skipping (not reachable or ill conditioned)")
                        continue

                # Place the poles at random locations
                des = rss(states, 1, 1)
                desired = poles(des)

                # Now place the poles using acker
                K = acker(sys.A, sys.B, desired)
                new = ss(sys.A - sys.B * K, sys.B, sys.C, sys.D)
                placed = poles(new)

                # Debugging code
                # diff = np.sort(poles) - np.sort(placed)
                # if not all(diff < 0.001):
                #     print("Found a problem:")
                #     print(sys)
                #     print("desired = ", poles)

                np.testing.assert_array_almost_equal(
                    np.sort(desired), np.sort(placed), decimal=4)

    def checkPlaced(self, P_expected, P_placed):
        """Check that placed poles are correct"""
        # No guarantee of the ordering, so sort them
        P_expected = np.squeeze(np.asarray(P_expected))
        P_expected.sort()
        P_placed.sort()
        np.testing.assert_array_almost_equal(P_expected, P_placed)

    def testPlace(self, matarrayin):
        # Matrices shamelessly stolen from scipy example code.
        A = matarrayin([[1.380, -0.2077, 6.715, -5.676],
                        [-0.5814, -4.290, 0, 0.6750],
                        [1.067, 4.273, -6.654, 5.893],
                        [0.0480, 4.273, 1.343, -2.104]])
        B = matarrayin([[0, 5.679],
                        [1.136, 1.136],
                        [0, 0],
                        [-3.146, 0]])
        P = matarrayin([-0.5 + 1j, -0.5 - 1j, -5.0566, -8.6659])
        K = place(A, B, P)
        assert ismatarrayout(K)
        P_placed = np.linalg.eigvals(A - B @ K)
        self.checkPlaced(P, P_placed)

        # Test that the dimension checks work.
        with pytest.raises(ControlDimension):
            place(A[1:, :], B, P)
        with pytest.raises(ControlDimension):
            place(A, B[1:, :], P)

        # Check that we get an error if we ask for too many poles in the same
        # location. Here, rank(B) = 2, so lets place three at the same spot.
        P_repeated = matarrayin([-0.5, -0.5, -0.5, -8.6659])
        with pytest.raises(ValueError):
            place(A, B, P_repeated)

    @slycotonly
    def testPlace_varga_continuous(self, matarrayin):
        """
        Check that we can place eigenvalues for dtime=False
        """
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5.], [7.]])

        P = [-2., -2.]
        K = place_varga(A, B, P)
        P_placed = np.linalg.eigvals(A - B @ K)
        self.checkPlaced(P, P_placed)

        # Test that the dimension checks work.
        np.testing.assert_raises(ControlDimension, place, A[1:, :], B, P)
        np.testing.assert_raises(ControlDimension, place, A, B[1:, :], P)

        # Regression test against bug #177
        # https://github.com/python-control/python-control/issues/177
        A = matarrayin([[0, 1], [100, 0]])
        B = matarrayin([[0], [1]])
        P = matarrayin([-20 + 10*1j, -20 - 10*1j])
        K = place_varga(A, B, P)
        P_placed = np.linalg.eigvals(A - B @ K)
        self.checkPlaced(P, P_placed)


    @slycotonly
    def testPlace_varga_continuous_partial_eigs(self, matarrayin):
        """
        Check that we are able to use the alpha parameter to only place
        a subset of the eigenvalues, for the continous time case.
        """
        # A matrix has eigenvalues at s=-1, and s=-2. Choose alpha = -1.5
        # and check that eigenvalue at s=-2 stays put.
        A = matarrayin([[1., -2.], [3., -4.]])
        B = matarrayin([[5.], [7.]])

        P = matarrayin([-3.])
        P_expected = np.array([-2.0, -3.0])
        alpha = -1.5
        K = place_varga(A, B, P, alpha=alpha)

        P_placed = np.linalg.eigvals(A - B @ K)
        # No guarantee of the ordering, so sort them
        self.checkPlaced(P_expected, P_placed)

    @slycotonly
    def testPlace_varga_discrete(self, matarrayin):
        """
        Check that we can place poles using dtime=True (discrete time)
        """
        A = matarrayin([[1., 0], [0, 0.5]])
        B = matarrayin([[5.], [7.]])

        P = matarrayin([0.5, 0.5])
        K = place_varga(A, B, P, dtime=True)
        P_placed = np.linalg.eigvals(A - B @ K)
        # No guarantee of the ordering, so sort them
        self.checkPlaced(P, P_placed)

    @slycotonly
    def testPlace_varga_discrete_partial_eigs(self, matarrayin):
        """"
        Check that we can only assign a single eigenvalue in the discrete
        time case.
        """
        # A matrix has eigenvalues at 1.0 and 0.5. Set alpha = 0.51, and
        # check that the eigenvalue at 0.5 is not moved.
        A = matarrayin([[1., 0], [0, 0.5]])
        B = matarrayin([[5.], [7.]])
        P = matarrayin([0.2, 0.6])
        P_expected = np.array([0.5, 0.6])
        alpha = 0.51
        K = place_varga(A, B, P, dtime=True, alpha=alpha)
        P_placed = np.linalg.eigvals(A - B @ K)
        self.checkPlaced(P_expected, P_placed)

    def check_LQR(self, K, S, poles, Q, R):
        S_expected = asmatarrayout(np.sqrt(Q @ R))
        K_expected = asmatarrayout(S_expected / R)
        poles_expected = -np.squeeze(np.asarray(K_expected))
        np.testing.assert_array_almost_equal(S, S_expected)
        np.testing.assert_array_almost_equal(K, K_expected)
        np.testing.assert_array_almost_equal(poles, poles_expected)

    def check_DLQR(self, K, S, poles, Q, R):
        S_expected = asmatarrayout(Q)
        K_expected = asmatarrayout(0)
        poles_expected = -np.squeeze(np.asarray(K_expected))
        np.testing.assert_array_almost_equal(S, S_expected)
        np.testing.assert_array_almost_equal(K, K_expected)
        np.testing.assert_array_almost_equal(poles, poles_expected)

    @pytest.mark.parametrize("method", [None, 'slycot', 'scipy'])
    def test_LQR_integrator(self, matarrayin, matarrayout, method):
        if method == 'slycot' and not slycot_check():
            return
        A, B, Q, R = (matarrayin([[X]]) for X in [0., 1., 10., 2.])
        K, S, poles = lqr(A, B, Q, R, method=method)
        self.check_LQR(K, S, poles, Q, R)

    @pytest.mark.parametrize("method", [None, 'slycot', 'scipy'])
    def test_LQR_3args(self, matarrayin, matarrayout, method):
        if method == 'slycot' and not slycot_check():
            return
        sys = ss(0., 1., 1., 0.)
        Q, R = (matarrayin([[X]]) for X in [10., 2.])
        K, S, poles = lqr(sys, Q, R, method=method)
        self.check_LQR(K, S, poles, Q, R)

    @pytest.mark.parametrize("method", [None, 'slycot', 'scipy'])
    def test_DLQR_3args(self, matarrayin, matarrayout, method):
        if method == 'slycot' and not slycot_check():
            return
        dsys = ss(0., 1., 1., 0., .1)
        Q, R = (matarrayin([[X]]) for X in [10., 2.])
        K, S, poles = dlqr(dsys, Q, R, method=method)
        self.check_DLQR(K, S, poles, Q, R)

    def test_DLQR_4args(self, matarrayin, matarrayout):
        A, B, Q, R = (matarrayin([[X]]) for X in [0., 1., 10., 2.])
        K, S, poles = dlqr(A, B, Q, R)
        self.check_DLQR(K, S, poles, Q, R)

    @pytest.mark.parametrize("cdlqr", [lqr, dlqr])
    def test_lqr_badmethod(self, cdlqr):
        A, B, Q, R = 0, 1, 10, 2
        with pytest.raises(ControlArgument, match="Unknown method"):
            K, S, poles = cdlqr(A, B, Q, R, method='nosuchmethod')

    @pytest.mark.parametrize("cdlqr", [lqr, dlqr])
    def test_lqr_slycot_not_installed(self, cdlqr):
        A, B, Q, R = 0, 1, 10, 2
        if not slycot_check():
            with pytest.raises(ControlSlycot, match="Can't find slycot"):
                K, S, poles = cdlqr(A, B, Q, R, method='slycot')

    @pytest.mark.xfail(reason="warning not implemented")
    def testLQR_warning(self):
        """Test lqr()

        Make sure we get a warning if [Q N;N' R] is not positive semi-definite
        """
        # from matlab_test siso.ss2 (testLQR); probably not referenced before
        # not yet implemented check
        A = np.array([[-2, 3, 1],
                      [-1, 0, 0],
                      [0, 1, 0]])
        B = np.array([[-1, 0, 0]]).T
        Q = np.eye(3)
        R = np.eye(1)
        N = np.array([[1, 1, 2]]).T
        # assert any(np.linalg.eigvals(np.block([[Q, N], [N.T, R]])) < 0)
        with pytest.warns(UserWarning):
            (K, S, E) = lqr(A, B, Q, R, N)

    @pytest.mark.parametrize("cdlqr", [lqr, dlqr])
    def test_lqr_call_format(self, cdlqr):
        # Create a random state space system for testing
        sys = rss(2, 3, 2)
        sys.dt = None           # treat as either continuous or discrete time

        # Weighting matrices
        Q = np.eye(sys.nstates)
        R = np.eye(sys.ninputs)
        N = np.zeros((sys.nstates, sys.ninputs))

        # Standard calling format
        Kref, Sref, Eref = cdlqr(sys.A, sys.B, Q, R)

        # Call with system instead of matricees
        K, S, E = cdlqr(sys, Q, R)
        np.testing.assert_array_almost_equal(Kref, K)
        np.testing.assert_array_almost_equal(Sref, S)
        np.testing.assert_array_almost_equal(Eref, E)

        # Pass a cross-weighting matrix
        K, S, E = cdlqr(sys, Q, R, N)
        np.testing.assert_array_almost_equal(Kref, K)
        np.testing.assert_array_almost_equal(Sref, S)
        np.testing.assert_array_almost_equal(Eref, E)

        # Inconsistent system dimensions
        with pytest.raises(ct.ControlDimension, match="Incompatible dimen"):
            K, S, E = cdlqr(sys.A, sys.C, Q, R)

        # Incorrect covariance matrix dimensions
        with pytest.raises(ct.ControlDimension, match="Q must be a square"):
            K, S, E = cdlqr(sys.A, sys.B, sys.C, R, Q)

        # Too few input arguments
        with pytest.raises(ct.ControlArgument, match="not enough input"):
            K, S, E = cdlqr(sys.A, sys.B)

        # First argument is the wrong type (use SISO for non-slycot tests)
        sys_tf = tf(rss(3, 1, 1))
        sys_tf.dt = None        # treat as either continuous or discrete time
        with pytest.raises(ct.ControlArgument, match="LTI system must be"):
            K, S, E = cdlqr(sys_tf, Q, R)

    @pytest.mark.xfail(reason="warning not implemented")
    def testDLQR_warning(self):
        """Test dlqr()

        Make sure we get a warning if [Q N;N' R] is not positive semi-definite
        """
        # from matlab_test siso.ss2 (testLQR); probably not referenced before
        # not yet implemented check
        A = np.array([[-2, 3, 1],
                      [-1, 0, 0],
                      [0, 1, 0]])
        B = np.array([[-1, 0, 0]]).T
        Q = np.eye(3)
        R = np.eye(1)
        N = np.array([[1, 1, 2]]).T
        # assert any(np.linalg.eigvals(np.block([[Q, N], [N.T, R]])) < 0)
        with pytest.warns(UserWarning):
            (K, S, E) = dlqr(A, B, Q, R, N)

    def test_care(self, matarrayin):
        """Test stabilizing and anti-stabilizing feedback, continuous"""
        A = matarrayin(np.diag([1, -1]))
        B = matarrayin(np.identity(2))
        Q = matarrayin(np.identity(2))
        R = matarrayin(np.identity(2))
        S = matarrayin(np.zeros((2, 2)))
        E = matarrayin(np.identity(2))

        X, L, G = care(A, B, Q, R, S, E, stabilizing=True)
        assert np.all(np.real(L) < 0)

        if slycot_check():
            X, L, G = care(A, B, Q, R, S, E, stabilizing=False)
            assert np.all(np.real(L) > 0)
        else:
            with pytest.raises(ControlArgument, match="'scipy' not valid"):
                X, L, G = care(A, B, Q, R, S, E, stabilizing=False)

    @pytest.mark.parametrize(
        "stabilizing",
        [True, pytest.param(False, marks=slycotonly)])
    def test_dare(self, matarrayin, stabilizing):
        """Test stabilizing and anti-stabilizing feedback, discrete"""
        A = matarrayin(np.diag([0.5, 2]))
        B = matarrayin(np.identity(2))
        Q = matarrayin(np.identity(2))
        R = matarrayin(np.identity(2))
        S = matarrayin(np.zeros((2, 2)))
        E = matarrayin(np.identity(2))

        X, L, G = dare(A, B, Q, R, S, E, stabilizing=stabilizing)
        sgn = {True: -1, False: 1}[stabilizing]
        assert np.all(sgn * (np.abs(L) - 1) > 0)

    def test_lqr_discrete(self):
        """Test overloading of lqr operator for discrete time systems"""
        csys = ct.rss(2, 1, 1)
        dsys = ct.drss(2, 1, 1)
        Q = np.eye(2)
        R = np.eye(1)

        # Calling with a system versus explicit A, B should be the sam
        K_csys, S_csys, E_csys = ct.lqr(csys, Q, R)
        K_expl, S_expl, E_expl = ct.lqr(csys.A, csys.B, Q, R)
        np.testing.assert_almost_equal(K_csys, K_expl)
        np.testing.assert_almost_equal(S_csys, S_expl)
        np.testing.assert_almost_equal(E_csys, E_expl)

        # Calling lqr() with a discrete time system should call dlqr()
        K_lqr, S_lqr, E_lqr = ct.lqr(dsys, Q, R)
        K_dlqr, S_dlqr, E_dlqr = ct.dlqr(dsys, Q, R)
        np.testing.assert_almost_equal(K_lqr, K_dlqr)
        np.testing.assert_almost_equal(S_lqr, S_dlqr)
        np.testing.assert_almost_equal(E_lqr, E_dlqr)

        # Calling lqr() with no timebase should call lqr()
        asys = ct.ss(csys.A, csys.B, csys.C, csys.D, dt=None)
        K_asys, S_asys, E_asys = ct.lqr(asys, Q, R)
        K_expl, S_expl, E_expl = ct.lqr(csys.A, csys.B, Q, R)
        np.testing.assert_almost_equal(K_asys, K_expl)
        np.testing.assert_almost_equal(S_asys, S_expl)
        np.testing.assert_almost_equal(E_asys, E_expl)

        # Calling dlqr() with a continuous time system should raise an error
        with pytest.raises(ControlArgument, match="dsys must be discrete"):
            K, S, E = ct.dlqr(csys, Q, R)

    @pytest.mark.parametrize(
        'nstates, noutputs, ninputs, nintegrators, type',
        [(2,      0,        1,       0,            None),
         (2,      1,        1,       0,            None),
         (4,      0,        2,       0,            None),
         (4,      3,        2,       0,            None),
         (2,      0,        1,       1,            None),
         (4,      0,        2,       2,            None),
         (4,      3,        2,       2,            None),
         (2,      0,        1,       0,            'nonlinear'),
         (4,      0,        2,       2,            'nonlinear'),
         (4,      3,        2,       2,            'nonlinear'),
        ])
    def test_statefbk_iosys(
            self, nstates, ninputs, noutputs, nintegrators, type):
        # Create the system to be controlled (and estimator)
        # TODO: make sure it is controllable?
        if noutputs == 0:
            # Create a system with full state output
            sys = ct.rss(nstates, nstates, ninputs, strictly_proper=True)
            sys.C = np.eye(nstates)
            est = None

        else:
            # Create a system with of the desired size
            sys = ct.rss(nstates, noutputs, ninputs, strictly_proper=True)

            # Create an estimator with different signal names
            L, _, _ = ct.lqe(
                sys.A, sys.B, sys.C, np.eye(ninputs), np.eye(noutputs))
            est = ss(
                sys.A - L @ sys.C, np.hstack([L, sys.B]), np.eye(nstates), 0,
                inputs=sys.output_labels + sys.input_labels,
                outputs=[f'xhat[{i}]' for i in range(nstates)])

        # Decide whether to include integral action
        if nintegrators:
            # Choose the first 'n' outputs as integral terms
            C_int = np.eye(nintegrators, nstates)

            # Set up an augmented system for LQR computation
            # TODO: move this computation into LQR
            A_aug = np.block([
                [sys.A, np.zeros((sys.nstates, nintegrators))],
                [C_int, np.zeros((nintegrators, nintegrators))]
            ])
            B_aug = np.vstack([sys.B, np.zeros((nintegrators, ninputs))])
            C_aug = np.hstack([sys.C, np.zeros((sys.C.shape[0], nintegrators))])
            aug = ss(A_aug, B_aug, C_aug, 0)
        else:
            C_int = np.zeros((0, nstates))
            aug = sys

        # Design an LQR controller
        K, _, _ = ct.lqr(aug, np.eye(nstates + nintegrators), np.eye(ninputs))
        Kp, Ki = K[:, :nstates], K[:, nstates:]

        # Create an I/O system for the controller
        ctrl, clsys = ct.create_statefbk_iosystem(
            sys, K, integral_action=C_int, estimator=est, type=type)

        # If we used a nonlinear controller, linearize it for testing
        if type == 'nonlinear':
            clsys = clsys.linearize(0, 0)

        # Make sure the linear system elements are correct
        if noutputs == 0:
            # No estimator
            Ac = np.block([
                [sys.A - sys.B @ Kp, -sys.B @ Ki],
                [C_int, np.zeros((nintegrators, nintegrators))]
            ])
            Bc = np.block([
                [sys.B @ Kp, sys.B],
                [-C_int, np.zeros((nintegrators, ninputs))]
            ])
            Cc = np.block([
                [np.eye(nstates), np.zeros((nstates, nintegrators))],
                [-Kp, -Ki]
            ])
            Dc = np.block([
                [np.zeros((nstates, nstates + ninputs))],
                [Kp, np.eye(ninputs)]
            ])
        else:
            # Estimator
            Be1, Be2 = est.B[:, :noutputs], est.B[:, noutputs:]
            Ac = np.block([
                [sys.A, -sys.B @ Ki, -sys.B @ Kp],
                [np.zeros((nintegrators, nstates + nintegrators)), C_int],
                [Be1 @ sys.C, -Be2 @ Ki, est.A - Be2 @ Kp]
                ])
            Bc = np.block([
                [sys.B @ Kp, sys.B],
                [-C_int, np.zeros((nintegrators, ninputs))],
                [Be2 @ Kp, Be2]
            ])
            Cc = np.block([
                [sys.C, np.zeros((noutputs, nintegrators + nstates))],
                [np.zeros_like(Kp), -Ki, -Kp]
            ])
            Dc = np.block([
                [np.zeros((noutputs, nstates + ninputs))],
                [Kp, np.eye(ninputs)]
            ])

        # Check to make sure everything matches
        np.testing.assert_array_almost_equal(clsys.A, Ac)
        np.testing.assert_array_almost_equal(clsys.B, Bc)
        np.testing.assert_array_almost_equal(clsys.C, Cc)
        np.testing.assert_array_almost_equal(clsys.D, Dc)

    def test_lqr_integral_continuous(self):
        # Generate a continuous time system for testing
        sys = ct.rss(4, 4, 2, strictly_proper=True)
        sys.C = np.eye(4)       # reset output to be full state
        C_int = np.eye(2, 4)    # integrate outputs for first two states
        nintegrators = C_int.shape[0]

        # Generate a controller with integral action
        K, _, _ = ct.lqr(
            sys, np.eye(sys.nstates + nintegrators), np.eye(sys.ninputs),
            integral_action=C_int)
        Kp, Ki = K[:, :sys.nstates], K[:, sys.nstates:]

        # Create an I/O system for the controller
        ctrl, clsys = ct.create_statefbk_iosystem(
            sys, K, integral_action=C_int)

        # Construct the state space matrices for the controller
        # Controller inputs = xd, ud, x
        # Controller state = z (integral of x-xd)
        # Controller output = ud - Kp(x - xd) - Ki z
        A_ctrl = np.zeros((nintegrators, nintegrators))
        B_ctrl = np.block([
            [-C_int, np.zeros((nintegrators, sys.ninputs)), C_int]
        ])
        C_ctrl = -K[:, sys.nstates:]
        D_ctrl = np.block([[Kp, np.eye(nintegrators), -Kp]])

        # Check to make sure everything matches
        np.testing.assert_array_almost_equal(ctrl.A, A_ctrl)
        np.testing.assert_array_almost_equal(ctrl.B, B_ctrl)
        np.testing.assert_array_almost_equal(ctrl.C, C_ctrl)
        np.testing.assert_array_almost_equal(ctrl.D, D_ctrl)

        # Construct the state space matrices for the closed loop system
        A_clsys = np.block([
            [sys.A - sys.B @ Kp, -sys.B @ Ki],
            [C_int, np.zeros((nintegrators, nintegrators))]
        ])
        B_clsys = np.block([
            [sys.B @ Kp, sys.B],
            [-C_int, np.zeros((nintegrators, sys.ninputs))]
        ])
        C_clsys = np.block([
            [np.eye(sys.nstates), np.zeros((sys.nstates, nintegrators))],
            [-Kp, -Ki]
        ])
        D_clsys = np.block([
            [np.zeros((sys.nstates, sys.nstates + sys.ninputs))],
            [Kp, np.eye(sys.ninputs)]
        ])

        # Check to make sure closed loop matches
        np.testing.assert_array_almost_equal(clsys.A, A_clsys)
        np.testing.assert_array_almost_equal(clsys.B, B_clsys)
        np.testing.assert_array_almost_equal(clsys.C, C_clsys)
        np.testing.assert_array_almost_equal(clsys.D, D_clsys)

        # Check the poles of the closed loop system
        assert all(np.real(clsys.poles()) < 0)

        # Make sure controller infinite zero frequency gain
        if slycot_check():
            ctrl_tf = tf(ctrl)
            assert abs(ctrl_tf(1e-9)[0][0]) > 1e6
            assert abs(ctrl_tf(1e-9)[1][1]) > 1e6

    def test_lqr_integral_discrete(self):
        # Generate a discrete time system for testing
        sys = ct.drss(4, 4, 2, strictly_proper=True)
        sys.C = np.eye(4)       # reset output to be full state
        C_int = np.eye(2, 4)    # integrate outputs for first two states
        nintegrators = C_int.shape[0]

        # Generate a controller with integral action
        K, _, _ = ct.lqr(
            sys, np.eye(sys.nstates + nintegrators), np.eye(sys.ninputs),
            integral_action=C_int)
        Kp, Ki = K[:, :sys.nstates], K[:, sys.nstates:]

        # Create an I/O system for the controller
        ctrl, clsys = ct.create_statefbk_iosystem(
            sys, K, integral_action=C_int)

        # Construct the state space matrices by hand
        A_ctrl = np.eye(nintegrators)
        B_ctrl = np.block([
            [-C_int, np.zeros((nintegrators, sys.ninputs)), C_int]
        ])
        C_ctrl = -K[:, sys.nstates:]
        D_ctrl = np.block([[Kp, np.eye(nintegrators), -Kp]])

        # Check to make sure everything matches
        assert ct.isdtime(clsys)
        np.testing.assert_array_almost_equal(ctrl.A, A_ctrl)
        np.testing.assert_array_almost_equal(ctrl.B, B_ctrl)
        np.testing.assert_array_almost_equal(ctrl.C, C_ctrl)
        np.testing.assert_array_almost_equal(ctrl.D, D_ctrl)

    @pytest.mark.parametrize(
        "rss_fun, lqr_fun",
        [(ct.rss, lqr), (ct.drss, dlqr)])
    def test_lqr_errors(self, rss_fun, lqr_fun):
        # Generate a discrete time system for testing
        sys = rss_fun(4, 4, 2, strictly_proper=True)

        with pytest.raises(ControlArgument, match="must pass an array"):
            K, _, _ = lqr_fun(
                sys, np.eye(sys.nstates), np.eye(sys.ninputs),
                integral_action="invalid argument")

        with pytest.raises(ControlArgument, match="gain size must match"):
            C_int = np.eye(2, 3)
            K, _, _ = lqr_fun(
                sys, np.eye(sys.nstates), np.eye(sys.ninputs),
                integral_action=C_int)

        with pytest.raises(TypeError, match="unrecognized keywords"):
            K, _, _ = lqr_fun(
                sys, np.eye(sys.nstates), np.eye(sys.ninputs),
                integrator=None)

    def test_statefbk_errors(self):
        sys = ct.rss(4, 4, 2, strictly_proper=True)
        K, _, _ = ct.lqr(sys, np.eye(sys.nstates), np.eye(sys.ninputs))

        with pytest.raises(ControlArgument, match="must be I/O system"):
            sys_tf = ct.tf([1], [1, 1])
            ctrl, clsys = ct.create_statefbk_iosystem(sys_tf, K)

        with pytest.raises(ControlArgument, match="output size must match"):
            est = ct.rss(3, 3, 2)
            ctrl, clsys = ct.create_statefbk_iosystem(sys, K, estimator=est)

        with pytest.raises(ControlArgument, match="must be the full state"):
            sys_nf = ct.rss(4, 3, 2, strictly_proper=True)
            ctrl, clsys = ct.create_statefbk_iosystem(sys_nf, K)

        with pytest.raises(ControlArgument, match="gain must be an array"):
            ctrl, clsys = ct.create_statefbk_iosystem(sys, "bad argument")

        with pytest.raises(ControlArgument, match="unknown type"):
            ctrl, clsys = ct.create_statefbk_iosystem(sys, K, type=1)

        # Errors involving integral action
        C_int = np.eye(2, 4)
        K_int, _, _ = ct.lqr(
            sys, np.eye(sys.nstates + C_int.shape[0]), np.eye(sys.ninputs),
            integral_action=C_int)

        with pytest.raises(ControlArgument, match="must pass an array"):
            ctrl, clsys = ct.create_statefbk_iosystem(
                sys, K_int, integral_action="bad argument")

        with pytest.raises(ControlArgument, match="must be an array of size"):
            ctrl, clsys = ct.create_statefbk_iosystem(
                sys, K, integral_action=C_int)
