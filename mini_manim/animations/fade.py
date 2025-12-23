"""
Fade animations: animate an MObject's opacity.
"""

from typing import Callable

from mini_manim.core.animation import Animation
from mini_manim.easing import linear


class FadeIn(Animation):
    """
    Animation that fades an MObject in (opacity from 0 to 1).
    
    Args:
        mobject: The MObject to animate.
        duration: Duration of the animation in seconds.
        easing: Easing function.
    """
    
    def __init__(
        self,
        mobject,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        super().__init__(mobject, duration, easing)
    
    def _capture_final_state(self) -> dict:
        """Capture full opacity as the final state."""
        return {
            'opacity': 1.0,
        }
    
    def _interpolate(self, alpha: float) -> None:
        """Interpolate opacity from 0 to 1."""
        # Start from 0, end at 1
        self.mobject.opacity = alpha


class FadeOut(Animation):
    """
    Animation that fades an MObject out (opacity from 1 to 0).
    
    Args:
        mobject: The MObject to animate.
        duration: Duration of the animation in seconds.
        easing: Easing function.
    """
    
    def __init__(
        self,
        mobject,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        super().__init__(mobject, duration, easing)
    
    def _capture_final_state(self) -> dict:
        """Capture zero opacity as the final state."""
        return {
            'opacity': 0.0,
        }
    
    def _interpolate(self, alpha: float) -> None:
        """Interpolate opacity from 1 to 0."""
        # Start from 1, end at 0
        self.mobject.opacity = 1.0 - alpha

