"""
Command-line interface for Mini-Manim.
"""

import sys
import importlib.util
import click
from pathlib import Path

from mini_manim.core.scene import Scene
from mini_manim.constants import (
    DEFAULT_FPS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    RESOLUTION_720P,
    RESOLUTION_1080P,
    RESOLUTION_4K,
)


def load_scene_class(script_path: str, scene_name: str) -> type[Scene]:
    """
    Dynamically load a Scene class from a Python file.
    
    Args:
        script_path: Path to the Python script.
        scene_name: Name of the Scene class to load.
        
    Returns:
        The Scene class.
        
    Raises:
        FileNotFoundError: If the script file doesn't exist.
        AttributeError: If the scene class is not found in the script.
    """
    script_path = Path(script_path).resolve()
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Load the module
    spec = importlib.util.spec_from_file_location("scene_module", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {script_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["scene_module"] = module
    spec.loader.exec_module(module)
    
    # Get the scene class
    if not hasattr(module, scene_name):
        available = [name for name in dir(module) if not name.startswith("_")]
        raise AttributeError(
            f"Scene class '{scene_name}' not found in {script_path}.\n"
            f"Available names: {', '.join(available)}"
        )
    
    scene_class = getattr(module, scene_name)
    
    if not issubclass(scene_class, Scene):
        raise TypeError(f"{scene_name} is not a subclass of Scene")
    
    return scene_class


@click.group()
def cli():
    """Mini-Manim: A minimal, programmatic animation engine."""
    pass


@cli.command()
@click.argument("script", type=click.Path(exists=True))
@click.option(
    "--scene",
    "-s",
    default=None,
    help="Name of the Scene class to render (default: first Scene subclass found)",
)
@click.option(
    "--output",
    "-o",
    "--out",
    default="output.mp4",
    help="Output video file path (default: output.mp4)",
)
@click.option(
    "--fps",
    default=DEFAULT_FPS,
    type=int,
    help=f"Frames per second (default: {DEFAULT_FPS})",
)
@click.option(
    "--resolution",
    "-r",
    type=click.Choice(["720p", "1080p", "4k"], case_sensitive=False),
    default="1080p",
    help="Video resolution preset (default: 1080p)",
)
@click.option(
    "--width",
    type=int,
    default=None,
    help="Video width in pixels (overrides --resolution)",
)
@click.option(
    "--height",
    type=int,
    default=None,
    help="Video height in pixels (overrides --resolution)",
)
@click.option(
    "--export-frames",
    is_flag=True,
    help="Export individual PNG frames instead of video",
)
@click.option(
    "--frames-dir",
    default="frames",
    help="Directory for exported frames (default: frames)",
)
@click.option(
    "--background",
    "--bg",
    default="0,0,0",
    help="Background color as R,G,B (0-1 range, default: 0,0,0 for black)",
)
def render(
    script: str,
    scene: str | None,
    output: str,
    fps: int,
    resolution: str,
    width: int | None,
    height: int | None,
    export_frames: bool,
    frames_dir: str,
    background: str,
):
    """
    Render a scene to a video file.
    
    SCRIPT: Path to the Python script containing the Scene class.
    """
    try:
        # Parse background color
        try:
            bg_parts = [float(x.strip()) for x in background.split(",")]
            if len(bg_parts) != 3:
                raise ValueError("Background color must have 3 components (R,G,B)")
            background_color = tuple(bg_parts)
        except ValueError as e:
            click.echo(f"Error parsing background color: {e}", err=True)
            sys.exit(1)
        
        # Determine resolution
        if width is not None and height is not None:
            video_width = width
            video_height = height
        else:
            resolution_map = {
                "720p": RESOLUTION_720P,
                "1080p": RESOLUTION_1080P,
                "4k": RESOLUTION_4K,
            }
            video_width, video_height = resolution_map[resolution.lower()]
        
        # Load scene class
        click.echo(f"Loading script: {script}")
        
        if scene is None:
            # Try to find the first Scene subclass
            click.echo("No scene specified, searching for Scene classes...")
            spec = importlib.util.spec_from_file_location("scene_module", script)
            if spec is None or spec.loader is None:
                click.echo(f"Error: Could not load module from {script}", err=True)
                sys.exit(1)
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["scene_module"] = module
            spec.loader.exec_module(module)
            
            # Find Scene subclasses
            scene_classes = [
                name
                for name in dir(module)
                if not name.startswith("_")
                and isinstance(getattr(module, name), type)
                and issubclass(getattr(module, name), Scene)
                and getattr(module, name) != Scene
            ]
            
            if not scene_classes:
                click.echo(
                    "Error: No Scene class found in script. Please specify with --scene.",
                    err=True,
                )
                sys.exit(1)
            
            if len(scene_classes) > 1:
                click.echo(
                    f"Multiple Scene classes found: {', '.join(scene_classes)}\n"
                    f"Using '{scene_classes[0]}'. Specify --scene to choose a different one.",
                    err=True,
                )
            
            scene_name = scene_classes[0]
        else:
            scene_name = scene
        
        scene_class = load_scene_class(script, scene_name)
        click.echo(f"Found scene class: {scene_name}")
        
        # Create and construct scene
        click.echo("Creating scene...")
        scene_instance = scene_class()
        scene_instance.construct()
        
        # Render
        if export_frames:
            click.echo(f"Exporting frames to: {frames_dir}")
            from mini_manim.core.renderer import CairoRenderer
            
            renderer = CairoRenderer(width=video_width, height=video_height)
            renderer.render_to_file(
                scene_instance, frames_dir, fps, background_color
            )
            click.echo(f"✓ Exported frames to {frames_dir}/")
        else:
            click.echo(f"Rendering video: {output}")
            click.echo(f"  Resolution: {video_width}x{video_height}")
            click.echo(f"  FPS: {fps}")
            
            scene_instance.render(
                output,
                fps=fps,
                width=video_width,
                height=video_height,
                background_color=background_color,
            )
            click.echo(f"✓ Video rendered: {output}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        if "--debug" in sys.argv or "-d" in sys.argv:
            traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

