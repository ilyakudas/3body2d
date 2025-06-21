"""
renderer.py - Rendering module for the three-body simulation.

This module handles the visualization of bodies, trails, and UI elements
using Pygame.
"""

import pygame
from pygame.math import Vector2
from typing import List, Tuple, Dict, Any, Optional
from bodies import Body


class Camera:
    """
    Camera class for handling view transformations.
    """
    
    def __init__(self, width: int, height: int, scale: float = 1.0):
        """
        Initialize the camera.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
            scale: Initial zoom scale factor
        """
        self.width = width
        self.height = height
        self.center = Vector2(width // 2, height // 2)
        self.offset = Vector2(0, 0)
        self.scale = scale
    
    def world_to_screen(self, position: Vector2) -> Vector2:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            position: Position in world coordinates
            
        Returns:
            Position in screen coordinates
        """
        # Apply scale and offset, then center on screen
        screen_pos = (position * self.scale) - self.offset + self.center
        return screen_pos
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen coordinates
            
        Returns:
            Position in world coordinates
        """
        # Reverse of world_to_screen
        world_pos = (screen_pos - self.center + self.offset) / self.scale
        return world_pos
    
    def zoom(self, factor: float, mouse_pos: Optional[Vector2] = None):
        """
        Zoom the camera by a factor, optionally centered on mouse position.
        
        Args:
            factor: Zoom factor (>1 to zoom in, <1 to zoom out)
            mouse_pos: Mouse position to center zoom on (or None for screen center)
        """
        if mouse_pos is None:
            mouse_pos = self.center
        
        # Get world position of mouse before zoom
        world_pos = self.screen_to_world(mouse_pos)
        
        # Apply zoom
        self.scale *= factor
        
        # Constrain zoom level
        self.scale = max(0.01, min(100.0, self.scale))
        
        # Adjust offset to keep mouse_pos pointing at the same world position
        new_world_pos = self.screen_to_world(mouse_pos)
        world_offset = world_pos - new_world_pos
        self.offset -= world_offset * self.scale
    
    def pan(self, delta: Vector2):
        """
        Pan the camera by a delta in screen coordinates.
        
        Args:
            delta: Amount to pan in screen coordinates
        """
        self.offset += delta / self.scale


class Renderer:
    """
    Renderer class for visualizing the simulation.
    """
    
    def __init__(self, width: int, height: int, background_color: Tuple[int, int, int] = (0, 0, 0)):
        """
        Initialize the renderer.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
            background_color: RGB color for the background
        """
        self.width = width
        self.height = height
        self.background_color = background_color
        self.screen = None
        self.font = None
        self.camera = Camera(width, height)
        self.trail_alpha = 150  # Alpha value for trail points
        
        # Initialize Pygame if not already done
        if not pygame.get_init():
            pygame.init()
        
        # Create screen and font
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Three-Body Problem Simulation")
        self.font = pygame.font.SysFont("Arial", 16)
    
    def draw_body(self, body: Body):
        """
        Draw a body as a filled circle.
        
        Args:
            body: The body to draw
        """
        # Convert world position to screen position
        screen_pos = self.camera.world_to_screen(body.pos)
        
        # Scale radius based on camera zoom
        scaled_radius = max(1, int(body.radius * self.camera.scale))
        
        # Draw the body
        pygame.draw.circle(self.screen, body.color, (int(screen_pos.x), int(screen_pos.y)), scaled_radius)
    
    def draw_trail(self, body: Body):
        """
        Draw the trail of a body.
        
        Args:
            body: The body whose trail to draw
        """
        if len(body.trail) < 2:
            return
        
        # Convert trail points to screen coordinates
        screen_points = [self.camera.world_to_screen(pos) for pos in body.trail]
        
        # Create a surface for the trail with alpha blending
        trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw trail as a series of lines with decreasing alpha
        alpha_step = self.trail_alpha / len(screen_points)
        for i in range(1, len(screen_points)):
            alpha = int(i * alpha_step)
            color_with_alpha = (*body.color, alpha)
            pygame.draw.line(
                trail_surface, 
                color_with_alpha,
                (int(screen_points[i-1].x), int(screen_points[i-1].y)),
                (int(screen_points[i].x), int(screen_points[i].y)),
                max(1, int(body.radius * self.camera.scale // 3))
            )
        
        # Blit the trail surface onto the main screen
        self.screen.blit(trail_surface, (0, 0))
    
    def draw_hud(self, physics_engine, bodies: List[Body], dt: float, fps: float, paused: bool):
        """
        Draw the heads-up display with simulation information.
        
        Args:
            physics_engine: The physics engine with simulation data
            bodies: List of bodies in the simulation
            dt: Current simulation time step
            fps: Current frames per second
            paused: Whether the simulation is paused
        """
        # Calculate system energy
        kinetic, potential, total = physics_engine.calculate_system_energy(bodies)
        
        # Prepare text lines
        lines = [
            f"FPS: {fps:.1f}",
            f"Sim time: {physics_engine.time_elapsed:.2f} s",
            f"dt: {dt:.6f} s",
            f"Bodies: {len(bodies)}",
            f"Zoom: {self.camera.scale:.2f}x",
            f"KE: {kinetic:.2e}",
            f"PE: {potential:.2e}",
            f"Total E: {total:.2e}",
            "PAUSED" if paused else "RUNNING"
        ]
        
        # Draw text lines
        y_offset = 10
        for line in lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def draw(self, physics_engine, bodies: List[Body], dt: float, fps: float, paused: bool):
        """
        Draw the complete scene.
        
        Args:
            physics_engine: The physics engine with simulation data
            bodies: List of bodies in the simulation
            dt: Current simulation time step
            fps: Current frames per second
            paused: Whether the simulation is paused
        """
        # Fill background
        self.screen.fill(self.background_color)
        
        # Draw trails
        for body in bodies:
            self.draw_trail(body)
        
        # Draw bodies
        for body in bodies:
            self.draw_body(body)
        
        # Draw HUD
        self.draw_hud(physics_engine, bodies, dt, fps, paused)
        
        # Update display
        pygame.display.flip()
