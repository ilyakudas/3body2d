"""
main.py - Main entry point for the three-body simulation.

This module initializes Pygame, loads configuration, and runs the main simulation loop.
"""

import sys
import pygame
from pygame.math import Vector2
from typing import List, Dict, Any, Tuple, Optional
import argparse

from bodies import Body
from physics import PhysicsEngine
from renderer import Renderer
from ui import UIManager, Button, Slider
from utils import load_config, save_config, create_default_config, save_simulation_state, load_simulation_state


class Simulation:
    """
    Main simulation class that ties everything together.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the simulation.
        
        Args:
            config_path: Path to the configuration file
        """
        # Initialize Pygame
        pygame.init()
        
        # Load configuration
        self.config = load_config(config_path)
        if not self.config:
            self.config = create_default_config()
            save_config(self.config, config_path)
        
        # Extract configuration values
        self.display_config = self.config.get("display", {})
        self.physics_config = self.config.get("physics", {})
        
        # Create window
        self.width = self.display_config.get("width", 800)
        self.height = self.display_config.get("height", 600)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Three-Body Problem Simulation")
        
        # Create clock for timing
        self.clock = pygame.time.Clock()
        
        # Create bodies
        self.bodies = self.create_bodies()
        
        # Create physics engine
        self.physics_engine = PhysicsEngine(
            G=self.physics_config.get("G", 6.674e-11),
            scale_factor=self.physics_config.get("scale_factor", 1.0)
        )
        
        # Create renderer
        self.renderer = Renderer(
            width=self.width,
            height=self.height,
            background_color=self.display_config.get("background_color", (0, 0, 0))
        )
        
        # Simulation state
        self.running = True
        self.paused = False
        self.dt = self.physics_config.get("dt", 0.01)
        self.integrations_per_frame = self.physics_config.get("integrations_per_frame", 10)
        self.integration_method = self.physics_config.get("integration_method", "verlet")
        
        # Create UI manager
        self.ui_manager = UIManager(self.screen)
        self.setup_ui()
        
        # Mouse state for camera control
        self.dragging = False
        self.last_mouse_pos = Vector2(0, 0)
        
        # Initial energy for conservation tracking
        _, _, self.initial_energy = self.physics_engine.calculate_system_energy(self.bodies)
        
        # FPS tracking
        self.fps = 0
    
    def create_bodies(self) -> List[Body]:
        """
        Create bodies from configuration.
        
        Returns:
            List of Body objects
        """
        bodies = []
        for body_config in self.config.get("bodies", []):
            body = Body.from_dict(body_config)
            bodies.append(body)
        return bodies
    
    def setup_ui(self):
        """Set up UI elements."""
        # Add pause button
        pause_button = Button(
            rect=(10, self.height - 40, 80, 30),
            text="Pause",
            action=self.toggle_pause,
            color=(50, 50, 100),
            hover_color=(70, 70, 150)
        )
        self.ui_manager.add_element(pause_button)
        
        # Add reset button
        reset_button = Button(
            rect=(100, self.height - 40, 80, 30),
            text="Reset",
            action=self.reset_simulation,
            color=(100, 50, 50),
            hover_color=(150, 70, 70)
        )
        self.ui_manager.add_element(reset_button)
        
        # Add speed slider
        speed_slider = Slider(
            rect=(200, self.height - 30, 150, 10),
            min_value=0.001,
            max_value=0.1,
            initial_value=self.dt,
            label="Speed",
            callback=self.set_dt,
            color=(70, 70, 70),
            handle_color=(120, 120, 120)
        )
        self.ui_manager.add_element(speed_slider)
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
    
    def reset_simulation(self):
        """Reset the simulation to initial state."""
        self.bodies = self.create_bodies()
        self.physics_engine.time_elapsed = 0.0
        _, _, self.initial_energy = self.physics_engine.calculate_system_energy(self.bodies)
    
    def set_dt(self, value: float):
        """
        Set the simulation time step.
        
        Args:
            value: New time step value
        """
        self.dt = value
    
    def handle_events(self):
        """Handle Pygame events."""
        for event in pygame.event.get():
            # Quit events
            if event.type == pygame.QUIT:
                self.running = False
            
            # Check if UI handled the event
            if self.ui_manager.handle_event(event):
                continue
            
            # Keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.dt *= 2.0
                elif event.key == pygame.K_MINUS:
                    self.dt *= 0.5
                elif event.key == pygame.K_s:
                    save_simulation_state(self.bodies, self.physics_config)
                elif event.key == pygame.K_l:
                    # TODO: Add file dialog for loading
                    pass
            
            # Mouse events for camera control
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.dragging = True
                    self.last_mouse_pos = Vector2(event.pos)
                elif event.button == 4:  # Mouse wheel up
                    self.renderer.camera.zoom(1.1, Vector2(event.pos))
                elif event.button == 5:  # Mouse wheel down
                    self.renderer.camera.zoom(0.9, Vector2(event.pos))
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    current_pos = Vector2(event.pos)
                    delta = current_pos - self.last_mouse_pos
                    self.renderer.camera.pan(delta)
                    self.last_mouse_pos = current_pos
    
    def update(self):
        """Update the simulation state."""
        if not self.paused:
            for _ in range(self.integrations_per_frame):
                self.physics_engine.step(self.bodies, self.dt, self.integration_method)
    
    def draw(self):
        """Draw the simulation."""
        # Calculate FPS
        self.fps = self.clock.get_fps()
        
        # Draw simulation
        self.renderer.draw(self.physics_engine, self.bodies, self.dt, self.fps, self.paused)
        
        # Draw UI
        self.ui_manager.update(pygame.mouse.get_pos())
        self.ui_manager.draw()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Run the main simulation loop."""
        while self.running:
            # Limit frame rate
            dt_real = self.clock.tick(60) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update simulation
            self.update()
            
            # Draw everything
            self.draw()
        
        # Clean up
        pygame.quit()


def main():
    """
    Main entry point for the simulation.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Three-Body Problem Simulation")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--fullscreen", action="store_true", help="Launch in fullscreen mode")
    parser.add_argument("--width", type=int, help="Window width (default: from config or 1280)")
    parser.add_argument("--height", type=int, help="Window height (default: from config or 720)")
    args = parser.parse_args()
    
    # Create and run the simulation
    sim = Simulation(args.config)
    
    # Override config with command-line arguments if provided
    if args.fullscreen:
        sim.display_config["fullscreen"] = True
    if args.width:
        sim.width = args.width
        sim.display_config["width"] = args.width
    if args.height:
        sim.height = args.height
        sim.display_config["height"] = args.height
    
    # Apply display settings
    if sim.display_config.get("fullscreen", False):
        sim.screen = pygame.display.set_mode((sim.width, sim.height), pygame.FULLSCREEN)
    else:
        sim.screen = pygame.display.set_mode((sim.width, sim.height))
    
    sim.run()


if __name__ == "__main__":
    main()
