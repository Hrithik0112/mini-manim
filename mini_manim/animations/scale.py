"""
Scale animation: animates an MObject's scale factor.
"""

from typing import Callable

from mini_manim.core.animation import Animation
from mini_manim.easing import linear


class Scale(Animation):
    """
    Animation that scales an MObject from its current scale to a target scale.
    
    Args:
        mobject: The MObject to animate.
        target_scale: Target scale factor (1.0 = no change, 2.0 = double size).
        duration: Duration of the animation in seconds.
        easing: Easing function.
    """
    
    def __init__(
        self,
        mobject,
        target_scale: float,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        super().__init__(mobject, duration, easing)
        self.target_scale = target_scale
    
    def _capture_final_state(self) -> dict:
        """Capture the target scale as the final state."""
        # If target_scale is relative (e.g., 1.5 means scale by 1.5x),
        # multiply by current scale. If absolute, use as-is.
        # We'll interpret it as relative to initial scale
        initial_scale = self._initial_state['scale_factor']
        return {
            'scale_factor': initial_scale * self.target_scale,
        }
    
    def _interpolate(self, alpha: float) -> None:
        """Interpolate scale from initial to target."""
        start_scale = self._initial_state['scale_factor']
        end_scale = self._final_state['scale_factor']
        
        # Linear interpolation
        self.mobject.scale_factor = start_scale + alpha * (end_scale - start_scale)

