"""
Animation system for Mini-Manim.

This module contains the base Animation class and AnimationBuilder for the fluent DSL.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mini_manim.core.mobject import MObject


class AnimationBuilder:
    """
    Builder class for fluent animation syntax.
    
    Example:
        circle.animate.move_to(RIGHT).scale(1.5)
    """
    
    def __init__(self, mobject: "MObject"):
        self.mobject = mobject
        self._pending_operations = []
    
    def move_to(self, target):
        """Queue a move_to animation."""
        self._pending_operations.append(("move_to", target))
        return self
    
    def scale(self, factor):
        """Queue a scale animation."""
        self._pending_operations.append(("scale", factor))
        return self
    
    def fade_in(self):
        """Queue a fade in animation."""
        self._pending_operations.append(("fade_in", None))
        return self
    
    def fade_out(self):
        """Queue a fade out animation."""
        self._pending_operations.append(("fade_out", None))
        return self
    
    def rotate(self, angle):
        """Queue a rotation animation."""
        self._pending_operations.append(("rotate", angle))
        return self
    
    # This will be properly implemented when we create the Animation classes
    def build(self, duration=1.0, easing=None):
        """Build animation objects from pending operations."""
        # Placeholder - will be implemented in later steps
        return []

