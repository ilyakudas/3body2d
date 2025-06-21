"""
bodies.py - Defines the Body class for the three-body simulation.

This module contains the Body dataclass which represents a celestial body
with mass, position, velocity, and other properties for visualization.
"""

from dataclasses import dataclass, field
from collections import deque
import pygame
from pygame.math import Vector2
from typing import Tuple, List, Optional


@dataclass
class Body:
    """
    Represents a celestial body in the simulation.
    
    Attributes:
        mass: Mass of the body in kg
        pos: Position vector (x, y) in meters
        vel: Velocity vector (vx, vy) in meters/second
        radius: Radius for rendering in pixels
        color: RGB color tuple for rendering
        trail_length: Maximum number of positions to store in the trail
    """
    mass: float
    pos: Vector2
    vel: Vector2
    radius: int
    color: Tuple[int, int, int]
    trail_length: int = 500
    
    # Fields that are computed or initialized during runtime
    acc: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    trail: deque = field(default_factory=deque)
    
    def __post_init__(self):
        """Initialize fields after instance creation."""
        # Convert pos and vel to Vector2 if they're not already
        if not isinstance(self.pos, Vector2):
            self.pos = Vector2(self.pos)
        if not isinstance(self.vel, Vector2):
            self.vel = Vector2(self.vel)
        
        # Initialize trail with current position
        self.trail = deque(maxlen=self.trail_length)
        self.trail.append(Vector2(self.pos))
    
    def update_trail(self):
        """Add current position to the trail."""
        self.trail.append(Vector2(self.pos))
    
    def reset_acceleration(self):
        """Reset acceleration to zero."""
        self.acc = Vector2(0, 0)
    
    def apply_force(self, force: Vector2):
        """
        Apply a force to the body, updating its acceleration.
        
        Args:
            force: Force vector to apply (in Newtons)
        """
        # F = ma -> a = F/m
        self.acc += force / self.mass
    
    def update(self, dt: float):
        """
        Update position and velocity based on current acceleration.
        
        Args:
            dt: Time step in seconds
        """
        # Simple Euler integration (can be replaced with more accurate methods)
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.update_trail()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Body':
        """
        Create a Body instance from a dictionary.
        
        Args:
            data: Dictionary containing body parameters
            
        Returns:
            A new Body instance
        """
        return cls(
            mass=data.get('mass', 1.0),
            pos=Vector2(data.get('position', [0, 0])),
            vel=Vector2(data.get('velocity', [0, 0])),
            radius=data.get('radius', 10),
            color=tuple(data.get('color', [255, 255, 255])),
            trail_length=data.get('trail_length', 500)
        )
    
    def to_dict(self) -> dict:
        """
        Convert Body to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the Body
        """
        return {
            'mass': self.mass,
            'position': [self.pos.x, self.pos.y],
            'velocity': [self.vel.x, self.vel.y],
            'radius': self.radius,
            'color': list(self.color),
            'trail_length': self.trail_length
        }
