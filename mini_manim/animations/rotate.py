"""
Rotate animation: animates an MObject's rotation.
"""

from typing import Callable

from mini_manim.core.animation import Animation
from mini_manim.easing import linear


class Rotate(Animation):
    """
    Animation that rotates an MObject by a given angle.
    
    Args:
        mobject: The MObject to animate.
        angle: Angle to rotate by in radians (positive = counter-clockwise).
        duration: Duration of the animation in seconds.
        easing: Easing function.
    """
    
    def __init__(
        self,
        mobject,
        angle: float,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        super().__init__(mobject, duration, easing)
        self.angle = angle  # Total angle to rotate
    
    def _capture_final_state(self) -> dict:
        """Capture the target rotation (initial + angle)."""
        initial_rotation = self._initial_state['rotation']
        return {
            'rotation': initial_rotation + self.angle,
        }
    
    def _interpolate(self, alpha: float) -> None:
        """Interpolate rotation from initial to target."""
        start_rotation = self._initial_state['rotation']
        end_rotation = self._final_state['rotation']
        
        # Linear interpolation
        self.mobject.rotation = start_rotation + alpha * (end_rotation - start_rotation)

