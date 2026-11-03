"""Pure game-economy functions; seconds are counted only while the app runs."""
from dataclasses import dataclass

XP_SECONDS = 60
TIME_BONUS_SECONDS = 30 * 60
TIME_BONUS_COINS = 20


def xp_required(level: int) -> int:
    if level < 1:
        raise ValueError('Level must be >= 1')
    return 60 + 10 * (level - 1)


def level_coins(level_reached: int) -> int:
    if level_reached < 10:
        return 50
    if level_reached < 20:
        return 75
    if level_reached < 30:
        return 100
    return 150


@dataclass
class Growth:
    level: int = 1
    xp: int = 0
    coins: int = 0
    total_seconds: int = 0
    pending_seconds: float = 0.0

    def advance(self, elapsed: float) -> tuple[int, int]:
        """Return (levels gained, coins gained); carry leftover XP forward."""
        if elapsed <= 0:
            return 0, 0
        self.pending_seconds += elapsed
        seconds = int(self.pending_seconds)
        self.pending_seconds -= seconds
        if not seconds:
            return 0, 0
        before = self.total_seconds // TIME_BONUS_SECONDS
        self.total_seconds += seconds
        after = self.total_seconds // TIME_BONUS_SECONDS
        coins = (after - before) * TIME_BONUS_COINS
        self.coins += coins
        self.xp += self.total_seconds // XP_SECONDS - (self.total_seconds - seconds) // XP_SECONDS
        levels = 0
        while self.xp >= xp_required(self.level):
            self.xp -= xp_required(self.level)
            self.level += 1
            levels += 1
            bonus = level_coins(self.level)
            self.coins += bonus
            coins += bonus
        return levels, coins
