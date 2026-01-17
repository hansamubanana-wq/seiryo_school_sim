from .game_state import GameState

__all__ = ['GameState']

# Gameは循環インポート回避のため、直接インポートが必要:
# from src.core.game import Game
