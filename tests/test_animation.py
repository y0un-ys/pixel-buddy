import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from pixel_buddy.animation import ANIMATION_MODES, animation_frame, pose_for


def test_animations_all_have_four_steps():
    for mode in ANIMATION_MODES:
        assert [pose_for(mode, i) for i in range(4)]
        assert len(set(pose_for(mode, i) for i in range(4))) >= 3, mode


def test_animation_clock_stays_in_frame_range():
    assert [animation_frame(i, 1) for i in range(9)] == [0,1,2,3,0,1,2,3,0]
    assert [animation_frame(i) for i in (0,3,4,8,12,16)] == [0,0,1,2,3,0]
    assert animation_frame(-100) == 0


def test_mouse_click_is_correlated_with_cursor_motion():
    poses = [pose_for('mouse', i) for i in range(4)]
    assert sum(p.mouse_click for p in poses) == 1
    assert len(set(p.cursor_x for p in poses)) > 1
    assert len(set(p.mouse_x for p in poses)) > 1


def test_gameplay_bounce_and_popcorn_actions():
    assert max(pose_for('gaming', i).game_jump for i in range(4)) > 0
    assert min(pose_for('watching', i).popcorn_y for i in range(4)) < 0
    assert len({pose_for('typing', i).key_highlight for i in range(4)}) == 4
