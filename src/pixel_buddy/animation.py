"""Deterministic four-frame pose data for compact desktop-pet animations.

No Qt dependency: animation changes can be tested on every platform.
"""

from dataclasses import dataclass

ANIMATION_MODES = ('typing', 'mouse', 'watching', 'gaming', 'idle')
FRAME_COUNT = 4


@dataclass(frozen=True)
class Pose:
    left_paw_y: int = 0
    right_paw_y: int = 0
    mouse_x: int = 0
    mouse_click: bool = False
    cursor_x: int = 0
    cursor_y: int = 0
    game_jump: int = 0
    popcorn_y: int = 0
    breathing: int = 0
    video_progress: int = 0
    key_highlight: int = 0


def animation_frame(frame: int, ticks_per_frame: int = 4) -> int:
    """Return a looped 0..3 index. Negative/invalid values are harmless."""
    if ticks_per_frame < 1:
        raise ValueError('ticks_per_frame must be positive')
    return (max(0, frame) // ticks_per_frame) % FRAME_COUNT


def pose_for(mode: str, frame: int) -> Pose:
    """Mode-specific four-step animation; all drawings follow these poses."""
    step = frame % FRAME_COUNT
    if mode == 'typing':
        return Pose(
            left_paw_y=(-2, 1, 0, 2)[step],
            right_paw_y=(2, 0, -2, 1)[step],
            key_highlight=(0, 3, 6, 2)[step],
        )
    if mode == 'mouse':
        return Pose(
            left_paw_y=(0, 0, -1, 0)[step],
            right_paw_y=(0, -1, -2, 0)[step],
            mouse_x=(0, 1, 3, 2)[step],
            mouse_click=(step == 2),
            cursor_x=(0, 4, 7, 5)[step],
            cursor_y=(0, -1, 2, 3)[step],
        )
    if mode == 'gaming':
        return Pose(
            left_paw_y=(0, 1, -2, 0)[step],
            right_paw_y=(0, -1, 1, 0)[step],
            game_jump=(0, 3, 6, 2)[step],
        )
    if mode == 'watching':
        return Pose(
            left_paw_y=(0, -1, -3, -1)[step],
            right_paw_y=(1, 0, -2, 1)[step],
            popcorn_y=(0, -2, -4, -1)[step],
            video_progress=(0, 3, 6, 9)[step],
        )
    return Pose(breathing=(0, 1, 2, 1)[step])
