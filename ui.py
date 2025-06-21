"""
ui.py - User interface module for the three-body simulation.

This module handles user input and UI elements for the simulation.
"""

import pygame
from pygame.math import Vector2
from typing import Tuple, Dict, Any, Callable, Optional


class Button:
    """
    Simple button class for UI interactions.
    """
    
    def __init__(self, rect: Tuple[int, int, int, int], text: str, 
                 action: Callable, color: Tuple[int, int, int] = (100, 100, 100),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize a button.
        
        Args:
            rect: Button rectangle (x, y, width, height)
            text: Button text
            action: Function to call when button is clicked
            color: Button color
            hover_color: Button color when hovered
            text_color: Text color
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        
        # Initialize font if Pygame is initialized
        if pygame.font.get_init():
            self.font = pygame.font.SysFont("Arial", 16)
        else:
            self.font = None
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the button on a surface.
        
        Args:
            surface: Surface to draw on
        """
        # Draw button background
        pygame.draw.rect(surface, self.hover_color if self.hovered else self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)  # Border
        
        # Draw text if font is available
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Update button state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
            
        Returns:
            True if button is hovered, False otherwise
        """
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events for the button.
        
        Args:
            event: Pygame event
            
        Returns:
            True if button was clicked, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.action()
                return True
        return False


class Slider:
    """
    Simple slider class for adjusting numeric values.
    """
    
    def __init__(self, rect: Tuple[int, int, int, int], min_value: float, max_value: float, 
                 initial_value: float, label: str, callback: Callable[[float], None],
                 color: Tuple[int, int, int] = (100, 100, 100),
                 handle_color: Tuple[int, int, int] = (200, 200, 200),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize a slider.
        
        Args:
            rect: Slider rectangle (x, y, width, height)
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Initial value
            label: Slider label
            callback: Function to call when value changes
            color: Slider color
            handle_color: Handle color
            text_color: Text color
        """
        self.rect = pygame.Rect(rect)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.callback = callback
        self.color = color
        self.handle_color = handle_color
        self.text_color = text_color
        self.dragging = False
        
        # Calculate handle position
        self.handle_width = 10
        self.handle_height = self.rect.height + 4
        self.update_handle_pos()
        
        # Initialize font if Pygame is initialized
        if pygame.font.get_init():
            self.font = pygame.font.SysFont("Arial", 14)
        else:
            self.font = None
    
    def update_handle_pos(self):
        """Update the handle position based on the current value."""
        value_range = self.max_value - self.min_value
        if value_range == 0:
            value_range = 1  # Avoid division by zero
        
        value_fraction = (self.value - self.min_value) / value_range
        handle_x = self.rect.x + int(value_fraction * self.rect.width) - self.handle_width // 2
        
        self.handle_rect = pygame.Rect(
            handle_x, 
            self.rect.y - 2, 
            self.handle_width, 
            self.handle_height
        )
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the slider on a surface.
        
        Args:
            surface: Surface to draw on
        """
        # Draw slider bar
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw handle
        pygame.draw.rect(surface, self.handle_color, self.handle_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.handle_rect, 1)  # Border
        
        # Draw label and value if font is available
        if self.font:
            # Draw label
            label_surface = self.font.render(f"{self.label}: {self.value:.2f}", True, self.text_color)
            label_rect = label_surface.get_rect(midleft=(self.rect.x, self.rect.y - 10))
            surface.blit(label_surface, label_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events for the slider.
        
        Args:
            event: Pygame event
            
        Returns:
            True if slider value was changed, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Calculate new value based on mouse position
            mouse_x = event.pos[0]
            x_fraction = max(0, min(1, (mouse_x - self.rect.x) / self.rect.width))
            self.value = self.min_value + x_fraction * (self.max_value - self.min_value)
            
            # Update handle position
            self.update_handle_pos()
            
            # Call callback
            self.callback(self.value)
            return True
        
        return False


class UIManager:
    """
    Manager for UI elements.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the UI manager.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
        self.elements = []
    
    def add_element(self, element):
        """
        Add a UI element.
        
        Args:
            element: UI element to add
        """
        self.elements.append(element)
    
    def draw(self):
        """Draw all UI elements."""
        for element in self.elements:
            element.draw(self.screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle events for all UI elements.
        
        Args:
            event: Pygame event
            
        Returns:
            True if any element handled the event, False otherwise
        """
        for element in self.elements:
            if element.handle_event(event):
                return True
        return False
    
    def update(self, mouse_pos: Tuple[int, int]):
        """
        Update all UI elements.
        
        Args:
            mouse_pos: Current mouse position
        """
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update(mouse_pos)
