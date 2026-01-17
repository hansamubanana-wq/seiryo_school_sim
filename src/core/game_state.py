"""
ゲーム状態の列挙型
"""
from enum import Enum, auto


class GameState(Enum):
    """ゲームの状態を表す列挙型"""
    TITLE = auto()          # タイトル画面
    PLAYING = auto()        # ゲームプレイ中
    PAUSED = auto()         # 一時停止
    MONTHLY_REPORT = auto() # 月次レポート表示
    YEARLY_REPORT = auto()  # 年次レポート表示
    HIRE_DIALOG = auto()    # 教師雇用ダイアログ
    BUILD_DIALOG = auto()   # 施設建設ダイアログ
    PROMOTION_DIALOG = auto()  # 宣伝ダイアログ
    GAME_OVER = auto()      # ゲームオーバー（破産）
    VICTORY = auto()        # 勝利条件達成
