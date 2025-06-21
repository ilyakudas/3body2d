"""
physics.py - Physics engine for the three-body simulation.

This module handles the gravitational interactions between bodies
and implements numerical integration methods for updating the simulation.
"""

from typing import List, Tuple, Optional
import pygame
from pygame.math import Vector2
from bodies import Body


class PhysicsEngine:
    """
    Physics engine that handles gravitational interactions and numerical integration.
    """
    
    def __init__(self, G: float = 6.674e-11, scale_factor: float = 1.0):
        """
        Initialize the physics engine.
        
        Args:
            G: Gravitational constant (can be scaled for simulation)
            scale_factor: Scaling factor for converting between simulation and display units
        """
        self.G = G
        self.scale_factor = scale_factor
        self.time_elapsed = 0.0  # Total simulation time elapsed
    
    def calculate_gravitational_force(self, body1: Body, body2: Body) -> Vector2:
        """
        Calculate the gravitational force between two bodies.
        
        Args:
            body1: First body
            body2: Second body
            
        Returns:
            Force vector acting on body1 due to body2
        """
        # Vector from body1 to body2
        r_vector = body2.pos - body1.pos
        
        # Distance between bodies
        distance = r_vector.length()
        
        # Avoid division by zero or very small values
        if distance < 1e-10:
            return Vector2(0, 0)
        
        # Magnitude of force: F = G * m1 * m2 / r^2
        force_magnitude = self.G * body1.mass * body2.mass / (distance * distance)
        
        # Direction of force (unit vector)
        # Use a safer normalization to avoid numerical issues
        try:
            direction = r_vector / distance  # More numerically stable than normalize()
        except (ValueError, ZeroDivisionError):
            return Vector2(0, 0)
        
        # Force vector
        return direction * force_magnitude
    
    def calculate_system_energy(self, bodies: List[Body]) -> Tuple[float, float, float]:
        """
        Calculate the total energy of the system (kinetic + potential).
        
        Args:
            bodies: List of bodies in the simulation
            
        Returns:
            Tuple of (kinetic_energy, potential_energy, total_energy)
        """
        kinetic_energy = 0.0
        potential_energy = 0.0
        
        # Calculate kinetic energy: KE = 0.5 * m * v^2
        for body in bodies:
            # Use dot product for better numerical stability
            v_squared = body.vel.dot(body.vel)
            kinetic_energy += 0.5 * body.mass * v_squared
        
        # Calculate potential energy: PE = -G * m1 * m2 / r
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                body1, body2 = bodies[i], bodies[j]
                r_vector = body2.pos - body1.pos
                distance = r_vector.length()
                
                # Use a minimum distance to avoid singularities
                if distance < 1e-10:
                    distance = 1e-10
                    
                potential_energy -= self.G * body1.mass * body2.mass / distance
        
        total_energy = kinetic_energy + potential_energy
        return kinetic_energy, potential_energy, total_energy
    
    def step_euler(self, bodies: List[Body], dt: float):
        """
        Update the simulation using the simple Euler method.
        
        Args:
            bodies: List of bodies to update
            dt: Time step in seconds
        """
        # Reset accelerations
        for body in bodies:
            body.reset_acceleration()
        
        # Calculate forces and update accelerations
        for i in range(len(bodies)):
            for j in range(len(bodies)):
                if i != j:  # Skip self-interaction
                    force = self.calculate_gravitational_force(bodies[i], bodies[j])
                    bodies[i].apply_force(force)
        
        # Update positions and velocities
        for body in bodies:
            body.update(dt)
        
        # Update simulation time
        self.time_elapsed += dt
    
    def step_verlet(self, bodies: List[Body], dt: float):
        """
        Update the simulation using the Velocity Verlet method for better energy conservation.
        
        Args:
            bodies: List of bodies to update
            dt: Time step in seconds
        """
        # Store initial accelerations
        old_acc = [Vector2(body.acc) for body in bodies]
        
        # Position update using current velocity and acceleration
        # x(t+dt) = x(t) + v(t)*dt + 0.5*a(t)*dt^2
        for i, body in enumerate(bodies):
            # Use separate calculations to avoid accumulation of floating-point errors
            vel_term = body.vel * dt
            acc_term = 0.5 * old_acc[i] * dt * dt
            body.pos += vel_term + acc_term
            body.update_trail()
        
        # Reset accelerations
        for body in bodies:
            body.reset_acceleration()
        
        # Recalculate forces and update accelerations at new positions
        for i in range(len(bodies)):
            for j in range(len(bodies)):
                if i != j:  # Skip self-interaction
                    force = self.calculate_gravitational_force(bodies[i], bodies[j])
                    bodies[i].apply_force(force)
        
        # Velocity update using average of old and new accelerations
        # v(t+dt) = v(t) + 0.5*(a(t) + a(t+dt))*dt
        for i, body in enumerate(bodies):
            acc_avg = 0.5 * (old_acc[i] + body.acc)
            body.vel += acc_avg * dt
        
        # Update simulation time
        self.time_elapsed += dt
    
    def step(self, bodies: List[Body], dt: float, method: str = 'verlet'):
        """
        Update the simulation using the specified integration method.
        
        Args:
            bodies: List of bodies to update
            dt: Time step in seconds
            method: Integration method ('euler' or 'verlet')
        """
        if method.lower() == 'euler':
            self.step_euler(bodies, dt)
        else:  # Default to Verlet
            self.step_verlet(bodies, dt)
