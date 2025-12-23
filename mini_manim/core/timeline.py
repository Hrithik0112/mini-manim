"""
Timeline: manages animation scheduling and frame-based playback.

The Timeline tracks animation blocks (sequential or parallel) and determines
which animations are active at any given frame.
"""

from typing import List, Tuple
from mini_manim.core.animation import Animation
from mini_manim.constants import DEFAULT_FPS


class AnimationBlock:
    """
    Represents a block of animations that run together.
    
    An AnimationBlock can contain multiple animations that run either:
    - Sequentially (one after another)
    - In parallel (all at the same time)
    """
    
    def __init__(
        self,
        animations: List[Animation],
        duration: float,
        sequential: bool = False,
    ):
        """
        Initialize an animation block.
        
        Args:
            animations: List of Animation objects in this block.
            duration: Total duration of this block in seconds.
            sequential: If True, animations run one after another.
                       If False, animations run in parallel.
        """
        self.animations = animations
        self.duration = duration
        self.sequential = sequential
        
        # Calculate per-animation duration if sequential
        if sequential and len(animations) > 0:
            self.per_animation_duration = duration / len(animations)
        else:
            self.per_animation_duration = duration
    
    def get_active_animations(self, time: float) -> List[Tuple[Animation, float]]:
        """
        Get animations that are active at the given time, with their local alpha.
        
        Args:
            time: Time within this block (0 to duration).
            
        Returns:
            List of (Animation, alpha) tuples where alpha is in [0, 1].
        """
        active = []
        
        if self.sequential:
            # Animations run one after another
            for i, anim in enumerate(self.animations):
                anim_start = i * self.per_animation_duration
                anim_end = anim_start + self.per_animation_duration
                
                if anim_start <= time < anim_end:
                    # This animation is active
                    local_time = time - anim_start
                    alpha = local_time / self.per_animation_duration
                    active.append((anim, alpha))
                elif time >= anim_end:
                    # Animation has finished
                    active.append((anim, 1.0))
        else:
            # All animations run in parallel
            for anim in self.animations:
                # Use the animation's own duration
                anim_duration = anim.duration
                if time < anim_duration:
                    alpha = time / anim_duration
                    active.append((anim, alpha))
                else:
                    # Animation has finished
                    active.append((anim, 1.0))
        
        return active


class Timeline:
    """
    Timeline manages the scheduling of animation blocks.
    
    The timeline tracks when each block starts and ends, and can determine
    which animations are active at any given frame.
    """
    
    def __init__(self, fps: int = DEFAULT_FPS):
        """
        Initialize a timeline.
        
        Args:
            fps: Frames per second for frame calculations.
        """
        self.fps = fps
        self.blocks: List[Tuple[AnimationBlock, float]] = []  # (block, start_time)
        self.total_duration = 0.0
    
    def add_block(
        self,
        animations: List[Animation],
        duration: float,
        sequential: bool = False,
    ) -> None:
        """
        Add a block of animations to the timeline.
        
        Args:
            animations: List of Animation objects.
            duration: Duration of the block in seconds.
            sequential: If True, animations run sequentially. If False, in parallel.
        """
        block = AnimationBlock(animations, duration, sequential)
        start_time = self.total_duration
        self.blocks.append((block, start_time))
        self.total_duration += duration
    
    def add_sequential(
        self,
        animations: List[Animation],
        duration: float,
    ) -> None:
        """
        Add animations that run sequentially (one after another).
        
        Args:
            animations: List of Animation objects.
            duration: Total duration for all animations combined.
        """
        self.add_block(animations, duration, sequential=True)
    
    def add_parallel(
        self,
        animations: List[Animation],
        duration: float,
    ) -> None:
        """
        Add animations that run in parallel (all at the same time).
        
        Args:
            animations: List of Animation objects.
            duration: Duration of the parallel block (should match longest animation).
        """
        self.add_block(animations, duration, sequential=False)
    
    def get_active_animations(self, frame: int) -> List[Tuple[Animation, float]]:
        """
        Get all animations that are active at the given frame.
        
        Args:
            frame: Frame number (0-indexed).
            
        Returns:
            List of (Animation, alpha) tuples where alpha is in [0, 1].
        """
        time = frame / self.fps
        
        active = []
        for block, start_time in self.blocks:
            block_time = time - start_time
            
            if block_time < 0:
                # Block hasn't started yet
                continue
            
            if block_time >= block.duration:
                # Block has finished - ensure all animations are at final state
                for anim in block.animations:
                    active.append((anim, 1.0))
            else:
                # Block is active
                block_active = block.get_active_animations(block_time)
                active.extend(block_active)
        
        return active
    
    def total_frames(self) -> int:
        """
        Get the total number of frames needed for the entire timeline.
        
        Returns:
            Total frame count (rounded up).
        """
        return int(self.total_duration * self.fps) + 1
    
    def get_frame_time(self, frame: int) -> float:
        """
        Get the time in seconds for a given frame.
        
        Args:
            frame: Frame number (0-indexed).
            
        Returns:
            Time in seconds.
        """
        return frame / self.fps
    
    def reset(self) -> None:
        """Reset the timeline (clear all blocks)."""
        self.blocks.clear()
        self.total_duration = 0.0

