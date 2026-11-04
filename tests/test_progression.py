from pixel_buddy.progression import Growth, xp_required
from pixel_buddy.store import GameStore


def test_progression_curve():
    assert [xp_required(n) for n in [1, 2, 5, 10, 20, 30]] == [60, 70, 100, 150, 250, 350]


def test_level_up_and_xp_carry():
    g = Growth()
    levels, coins = g.advance(60 * 65)
    assert levels == 1
    assert g.level == 2 and g.xp == 5
    assert coins == 90  # 50 level-up + two 30-min time bonuses


def test_fractional_time_and_no_negative():
    g = Growth()
    assert g.advance(-9) == (0,0)
    g.advance(.6)
    g.advance(.6)
    assert g.total_seconds == 1


def test_save_purchase_equip(tmp_path):
    path = tmp_path / 'buddy.sqlite3'
    s = GameStore(path)
    s.growth.level = 10
    s.growth.coins = 1000
    assert '완료' in s.purchase('dual')
    assert s.growth.coins == 350
    assert s.equipped['컴퓨터'] == 'dual'
    s.close()
    loaded = GameStore(path)
    assert loaded.equipped['컴퓨터'] == 'dual'
    assert loaded.growth.coins == 350
    loaded.close()


def test_level_restriction(tmp_path):
    s = GameStore(tmp_path / 'game.db')
    s.growth.coins = 9000
    assert 'Lv.10' in s.purchase('dual')
    s.close()
