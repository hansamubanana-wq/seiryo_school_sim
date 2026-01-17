"""
青稜中学校・高等学校 経営シミュレーション
エントリーポイント
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game import Game


def main():
    """ゲームのエントリーポイント"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
