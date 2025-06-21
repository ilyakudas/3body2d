"""
test_physics.py - Unit tests for the physics engine.

This module contains tests to validate the physics engine,
particularly focusing on force symmetry and energy conservation.
"""

import sys
import os
import unittest
from pygame.math import Vector2

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bodies import Body
from physics import PhysicsEngine


class TestPhysics(unittest.TestCase):
    """Test cases for the physics engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a physics engine with a scaled G for easier testing
        self.G = 1.0  # Use G=1 for simplicity in tests
        self.physics_engine = PhysicsEngine(G=self.G)
        
        # Create some test bodies
        self.body1 = Body(
            mass=1.0,
            pos=Vector2(0, 0),
            vel=Vector2(0, 0),
            radius=1,
            color=(255, 0, 0)
        )
        
        self.body2 = Body(
            mass=2.0,
            pos=Vector2(1, 0),
            vel=Vector2(0, 0),
            radius=1,
            color=(0, 255, 0)
        )
        
        self.body3 = Body(
            mass=3.0,
            pos=Vector2(0, 1),
            vel=Vector2(0, 0),
            radius=1,
            color=(0, 0, 255)
        )
    
    def test_force_symmetry(self):
        """Test that gravitational forces are symmetric."""
        # Calculate force from body1 to body2
        force_1_to_2 = self.physics_engine.calculate_gravitational_force(self.body1, self.body2)
        
        # Calculate force from body2 to body1 (should be equal and opposite)
        force_2_to_1 = self.physics_engine.calculate_gravitational_force(self.body2, self.body1)
        
        # Check that forces are equal and opposite
        self.assertAlmostEqual(force_1_to_2.x, -force_2_to_1.x, places=10)
        self.assertAlmostEqual(force_1_to_2.y, -force_2_to_1.y, places=10)
    
    def test_force_magnitude(self):
        """Test that gravitational force magnitude follows Newton's law."""
        # Calculate force from body1 to body2
        force = self.physics_engine.calculate_gravitational_force(self.body1, self.body2)
        
        # Expected force magnitude: F = G * m1 * m2 / r^2
        # Distance is 1, masses are 1 and 2, G is 1
        expected_magnitude = self.G * self.body1.mass * self.body2.mass / 1.0**2
        
        # Check force magnitude
        self.assertAlmostEqual(force.length(), expected_magnitude, places=10)
    
    def test_energy_conservation_euler(self):
        """Test energy conservation with Euler integration."""
        # Create a simple two-body system with initial velocity
        # This creates a more stable orbit scenario
        body1 = Body(
            mass=100.0,
            pos=Vector2(0, 0),
            vel=Vector2(0, 0),
            radius=1,
            color=(255, 0, 0)
        )
        
        body2 = Body(
            mass=1.0,
            pos=Vector2(10, 0),
            vel=Vector2(0, 3),  # Tangential velocity for circular-ish orbit
            radius=1,
            color=(0, 255, 0)
        )
        
        bodies = [body1, body2]
        
        # Get initial energy
        initial_ke, initial_pe, initial_total = self.physics_engine.calculate_system_energy(bodies)
        
        # Run simulation for a few steps with a smaller timestep
        dt = 0.001  # Smaller timestep for better stability
        steps = 100
        for _ in range(steps):
            self.physics_engine.step_euler(bodies, dt)
        
        # Get final energy
        final_ke, final_pe, final_total = self.physics_engine.calculate_system_energy(bodies)
        
        # Calculate energy drift as percentage
        if abs(initial_total) < 1e-10:
            energy_drift = abs(final_total - initial_total)
        else:
            energy_drift = abs((final_total - initial_total) / initial_total) * 100
        
        # For Euler, we expect significant drift, but it should be within reasonable bounds for small dt
        # This is a loose test since Euler is not energy-conserving
        self.assertLess(energy_drift, 10.0, f"Energy drift too high: {energy_drift}%")
    
    def test_energy_conservation_verlet(self):
        """Test energy conservation with Velocity Verlet integration."""
        # Create a simple two-body system with initial velocity
        # This creates a more stable orbit scenario
        body1 = Body(
            mass=100.0,
            pos=Vector2(0, 0),
            vel=Vector2(0, 0),
            radius=1,
            color=(255, 0, 0)
        )
        
        body2 = Body(
            mass=1.0,
            pos=Vector2(10, 0),
            vel=Vector2(0, 3),  # Tangential velocity for circular-ish orbit
            radius=1,
            color=(0, 255, 0)
        )
        
        bodies = [body1, body2]
        
        # Get initial energy
        initial_ke, initial_pe, initial_total = self.physics_engine.calculate_system_energy(bodies)
        
        # Run simulation for a few steps with a smaller timestep
        dt = 0.001  # Smaller timestep for better stability
        steps = 1000  # More steps for a longer simulation
        for _ in range(steps):
            self.physics_engine.step_verlet(bodies, dt)
        
        # Get final energy
        final_ke, final_pe, final_total = self.physics_engine.calculate_system_energy(bodies)
        
        # Calculate energy drift as percentage
        if abs(initial_total) < 1e-10:
            energy_drift = abs(final_total - initial_total)
        else:
            energy_drift = abs((final_total - initial_total) / initial_total) * 100
        
        # Verlet should conserve energy much better than Euler
        self.assertLess(energy_drift, 1.0, f"Energy drift too high: {energy_drift}%")
    
    def test_three_body_energy(self):
        """Test energy conservation in a three-body system."""
        # Create a more stable three-body system (similar to a Lagrange point setup)
        body1 = Body(
            mass=1000.0,
            pos=Vector2(0, 0),
            vel=Vector2(0, 0),
            radius=5,
            color=(255, 255, 0)  # Yellow (sun)
        )
        
        body2 = Body(
            mass=10.0,
            pos=Vector2(100, 0),
            vel=Vector2(0, 3),  # Orbital velocity
            radius=2,
            color=(0, 0, 255)  # Blue (planet)
        )
        
        body3 = Body(
            mass=0.1,
            pos=Vector2(105, 0),  # Near body2
            vel=Vector2(0, 3.5),  # Similar orbital velocity
            radius=1,
            color=(255, 0, 0)  # Red (moon)
        )
        
        bodies = [body1, body2, body3]
        
        # Get initial energy
        initial_ke, initial_pe, initial_total = self.physics_engine.calculate_system_energy(bodies)
        
        # Run simulation for a few steps with Verlet and smaller timestep
        dt = 0.0005  # Very small timestep for stability in 3-body system
        steps = 1000
        for _ in range(steps):
            self.physics_engine.step_verlet(bodies, dt)
        
        # Get final energy
        final_ke, final_pe, final_total = self.physics_engine.calculate_system_energy(bodies)
        
        # Calculate energy drift as percentage
        if abs(initial_total) < 1e-10:
            energy_drift = abs(final_total - initial_total)
        else:
            energy_drift = abs((final_total - initial_total) / initial_total) * 100
        
        # Three-body systems are chaotic, so we allow a bit more drift
        self.assertLess(energy_drift, 2.0, f"Energy drift too high: {energy_drift}%")


if __name__ == '__main__':
    unittest.main()
