"""Numerical checks of the model, coordinate conventions and solver failures."""
import unittest
import numpy as np
from controller import Controller
from model import Settings, reference, scheduled_model, error_dynamics, advance, tracking_error


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.c = Settings()

    def test_reference_derivatives(self):
        for name in ['oval', 'figure_eight', 'lane_change']:
            for t in [3., 11., 23.]:
                h = 1e-4
                ref = reference(name, [t-h, t, t+h], self.c)
                velocity = (ref[2, :2]-ref[0, :2])/(2*h)
                np.testing.assert_allclose(velocity, ref[1, 3]*np.array([np.cos(ref[1, 2]), np.sin(ref[1, 2])]), atol=1e-7)
                self.assertAlmostEqual((ref[2, 3]-ref[0, 3])/(2*h), ref[1, 5], places=7)

    def test_lpv_matches_local_error_jacobian(self):
        for t in [2., 13., 25.]:
            ref = reference('figure_eight', t, self.c)[0]
            command = ref[[6, 5]]
            a, b = scheduled_model(ref, self.c)
            h = 1e-6
            ja = np.column_stack([(error_dynamics(h*e, command, ref, self.c)-error_dynamics(-h*e, command, ref, self.c))/(2*h) for e in np.eye(4)])
            jb = np.column_stack([(error_dynamics(np.zeros(4), command+h*e, ref, self.c)-error_dynamics(np.zeros(4), command-h*e, ref, self.c))/(2*h) for e in np.eye(2)])
            np.testing.assert_allclose((a-np.eye(4))/self.c.dt, ja, atol=1e-7)
            np.testing.assert_allclose(b/self.c.dt, jb, atol=1e-7)

    def test_rk4_constant_turn_matches_circle(self):
        z = np.array([0., 0., 0., 4.])
        steering = 0.15
        for k in range(100):
            z = advance(z, np.array([steering, 0.]), k*self.c.dt, 'oval', self.c)
        yaw = 4*np.tan(steering)/self.c.wheelbase*10
        radius = self.c.wheelbase/np.tan(steering)
        np.testing.assert_allclose(z[:2], [radius*np.sin(yaw), radius*(1-np.cos(yaw))], atol=1e-8)

    def test_error_frame_and_wrap(self):
        ref = np.array([0., 0., np.pi/2, 4.])
        e = tracking_error(np.array([-2., 3., np.pi/2+2*np.pi, 5.]), ref)
        np.testing.assert_allclose(e, [3, 2, 0, 1], atol=1e-12)

    def test_straight_equilibrium_and_infeasible_problem(self):
        preview = np.zeros((self.c.horizon+1, 7))
        preview[:, 3] = 4
        ctrl = Controller(self.c)
        u, _, _ = ctrl.command(np.zeros(4), preview, np.zeros(2))
        np.testing.assert_allclose(u, 0, atol=1e-8)
        # Previous steering is too far outside limits to re-enter in one step.
        with self.assertRaises(RuntimeError):
            ctrl.command(np.zeros(4), preview, np.array([2., 0.]))


if __name__ == '__main__':
    unittest.main()
