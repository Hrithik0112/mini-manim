"""
Move animation: animates an MObject's position.
"""

import numpy as np
from typing import Callable

from mini_manim.core.animation import Animation
from mini_manim.easing import linear


class Move(Animation):
    """
    Animation that moves an MObject from its current position to a target position.
    
    Args:
        mobject: The MObject to animate.
        target: Target position (x, y) as numpy array or tuple.
        duration: Duration of the animation in seconds.
        easing: Easing function.
    """
    
    def __init__(
        self,
        mobject,
        target: np.ndarray | tuple[float, float],
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ):
        super().__init__(mobject, duration, easing)
        
        if isinstance(target, tuple):
            self.target = np.array(target, dtype=float)
        else:
            self.target = target.copy()
    
    def _capture_final_state(self) -> dict:
        """Capture the target position as the final state."""
        return {
            'position': self.target.copy(),
        }
    
    def _interpolate(self, alpha: float) -> None:
        """Interpolate position from initial to target."""
        start_pos = self._initial_state['position']
        end_pos = self._final_state['position']
        
        # Linear interpolation
        self.mobject.position = start_pos + alpha * (end_pos - start_pos)

