"""
utils.py - Utility functions for the three-body simulation.

This module provides helper functions for vector operations,
file I/O, and other miscellaneous tasks.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import pygame
from pygame.math import Vector2
from bodies import Body


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration data
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        return create_default_config()


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def create_default_config() -> Dict[str, Any]:
    """
    Create a default configuration.
    
    Returns:
        Dictionary containing default configuration
    """
    return {
        "bodies": [
            {
                "mass": 1.0e6,
                "position": [0, 0],
                "velocity": [0, 0],
                "radius": 10,
                "color": [255, 255, 0],
                "trail_length": 500
            },
            {
                "mass": 1.0e4,
                "position": [100, 0],
                "velocity": [0, 40],
                "radius": 5,
                "color": [0, 255, 0],
                "trail_length": 500
            },
            {
                "mass": 1.0e4,
                "position": [-100, 0],
                "velocity": [0, -40],
                "radius": 5,
                "color": [0, 0, 255],
                "trail_length": 500
            }
        ],
        "physics": {
            "G": 6.674e-11,
            "dt": 0.01,
            "scale_factor": 1.0,
            "integrations_per_frame": 10,
            "integration_method": "verlet"
        },
        "display": {
            "width": 800,
            "height": 600,
            "background_color": [0, 0, 0],
            "trail_alpha": 150
        }
    }


def save_simulation_state(bodies: List[Body], physics_config: Dict[str, Any]) -> str:
    """
    Save the current simulation state to a file.
    
    Args:
        bodies: List of bodies in the simulation
        physics_config: Physics configuration
        
    Returns:
        Path to the saved file
    """
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"save_{timestamp}.json"
    
    # Convert bodies to dictionaries
    body_dicts = [body.to_dict() for body in bodies]
    
    # Create the save data
    save_data = {
        "bodies": body_dicts,
        "physics": physics_config,
        "timestamp": timestamp
    }
    
    # Save to file
    try:
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"Simulation saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving simulation: {e}")
        return ""


def load_simulation_state(filename: str) -> Tuple[List[Body], Dict[str, Any]]:
    """
    Load a simulation state from a file.
    
    Args:
        filename: Path to the save file
        
    Returns:
        Tuple of (bodies, physics_config)
    """
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)
        
        # Create bodies from the saved data
        bodies = [Body.from_dict(body_dict) for body_dict in save_data.get("bodies", [])]
        physics_config = save_data.get("physics", {})
        
        return bodies, physics_config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading simulation: {e}")
        return [], {}


def distance(v1: Vector2, v2: Vector2) -> float:
    """
    Calculate the Euclidean distance between two vectors.
    
    Args:
        v1: First vector
        v2: Second vector
        
    Returns:
        Distance between the vectors
    """
    return (v2 - v1).length()


def format_scientific(value: float, precision: int = 2) -> str:
    """
    Format a number in scientific notation.
    
    Args:
        value: Number to format
        precision: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{value:.{precision}e}"


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Namespace containing parsed arguments
    """
    import argparse
    parser = argparse.ArgumentParser(description="Three-Body Problem Simulation")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    return parser.parse_args()
