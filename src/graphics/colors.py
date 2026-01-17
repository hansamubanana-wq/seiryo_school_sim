"""
カラー定義とフォント管理
"""
import pygame
from typing import Optional, Dict

import config


class FontManager:
    """日本語フォント管理クラス（シングルトン）"""
    _instance: Optional['FontManager'] = None
    _initialized: bool = False

    def __new__(cls) -> 'FontManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if FontManager._initialized:
            return
        FontManager._initialized = True
        self._fonts: Dict[int, pygame.font.Font] = {}
        self._font_name: Optional[str] = None

    def _find_japanese_font(self) -> Optional[str]:
        """利用可能な日本語フォントを探す"""
        if self._font_name:
            return self._font_name

        available_fonts = pygame.font.get_fonts()
        for font_name in config.FONT_NAMES:
            # フォント名の正規化（スペースを除去して小文字に）
            normalized = font_name.lower().replace(" ", "")
            for available in available_fonts:
                if normalized in available.lower().replace(" ", ""):
                    self._font_name = available
                    return self._font_name

        # 見つからない場合はNone（デフォルトフォント使用）
        return None

    def get_font(self, size: int) -> pygame.font.Font:
        """指定サイズのフォントを取得（キャッシュ付き）"""
        if size not in self._fonts:
            font_name = self._find_japanese_font()
            if font_name:
                self._fonts[size] = pygame.font.SysFont(font_name, size)
            else:
                # フォールバック：デフォルトフォント
                self._fonts[size] = pygame.font.Font(None, size)
        return self._fonts[size]

    @classmethod
    def get(cls, size: int) -> pygame.font.Font:
        """クラスメソッドでフォント取得"""
        return cls().get_font(size)


# グローバルフォントマネージャー
def get_font(size: int) -> pygame.font.Font:
    """フォント取得のショートカット関数"""
    return FontManager.get(size)


class Colors:
    """ゲーム内で使用する色の定義"""

    # 基本色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)

    # 背景色
    BACKGROUND = (240, 240, 235)
    PANEL_BG = (50, 50, 60)
    PANEL_BG_LIGHT = (70, 70, 85)

    # UI色
    UI_TEXT = (255, 255, 255)
    UI_TEXT_DARK = (30, 30, 30)
    UI_BORDER = (100, 100, 110)

    # ボタン色
    BUTTON_NORMAL = (80, 80, 100)
    BUTTON_HOVER = (100, 100, 130)
    BUTTON_PRESSED = (60, 60, 80)
    BUTTON_DISABLED = (60, 60, 60)

    # 資金関連
    MONEY_POSITIVE = (100, 200, 100)
    MONEY_NEGATIVE = (200, 100, 100)
    MONEY_NEUTRAL = (200, 200, 100)

    # ステータス色
    STATUS_GOOD = (100, 200, 100)
    STATUS_NORMAL = (200, 200, 100)
    STATUS_BAD = (200, 100, 100)

    # 学校関連
    BUILDING_CLASSROOM = (200, 180, 150)
    BUILDING_SPECIAL = (150, 150, 200)
    GRASS = (120, 180, 100)
    ROAD = (180, 180, 180)

    # アクセント
    ACCENT_BLUE = (100, 150, 200)
    ACCENT_GREEN = (100, 180, 120)
    ACCENT_ORANGE = (220, 150, 80)

    @staticmethod
    def get_money_color(amount: int) -> tuple:
        """金額に応じた色を返す"""
        if amount > 0:
            return Colors.MONEY_POSITIVE
        elif amount < 0:
            return Colors.MONEY_NEGATIVE
        return Colors.MONEY_NEUTRAL

    @staticmethod
    def get_status_color(value: float, low_threshold: float = 30, high_threshold: float = 70) -> tuple:
        """ステータス値に応じた色を返す（0-100想定）"""
        if value >= high_threshold:
            return Colors.STATUS_GOOD
        elif value >= low_threshold:
            return Colors.STATUS_NORMAL
        return Colors.STATUS_BAD
