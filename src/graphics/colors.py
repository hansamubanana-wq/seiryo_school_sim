import pygame
import config

class FontManager:
    """日本語フォント管理クラス（シングルトン）"""
    _instance = None
    
    def __init__(self):
        self._fonts = {}
        self._font_name = self._find_japanese_font()
        
    @classmethod
    def get(cls, size: int) -> pygame.font.Font:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.get_font(size)
        
    def _find_japanese_font(self):
        """利用可能な日本語フォントを探す"""
        available = pygame.font.get_fonts()
        for target in config.FONT_NAMES:
            target_clean = target.lower().replace(" ", "")
            for sys_font in available:
                if target_clean in sys_font.lower().replace(" ", ""):
                    return sys_font
        return None
        
    def get_font(self, size: int) -> pygame.font.Font:
        if size not in self._fonts:
            if self._font_name:
                self._fonts[size] = pygame.font.SysFont(self._font_name, size)
            else:
                self._fonts[size] = pygame.font.Font(None, size)
        return self._fonts[size]

def get_font(size: int) -> pygame.font.Font:
    """グローバルヘルパー関数"""
    return FontManager.get(size)

class Colors:
    """カラーパレット定義"""
    # 基本色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # UI配色
    BACKGROUND = (245, 245, 240)      # 全体の背景色
    UI_BG = (255, 255, 255)           # パネルやダイアログの背景
    UI_BORDER = (100, 100, 100)       # 枠線
    UI_PANEL_BG = (240, 240, 240)     # ボタンなどの背景
    
    UI_TEXT = (50, 50, 50)            # 通常テキスト
    UI_TEXT_DARK = (20, 20, 20)       # 濃いテキスト
    
    # ★ここが消えていました！復活させたボタン設定
    BUTTON_NORMAL = (230, 230, 230)   # 通常時のボタン色
    BUTTON_HOVER = (200, 200, 200)    # ホバー時のボタン色
    BUTTON_TEXT = (20, 20, 20)        # ボタンの文字色
    
    # アクセントカラー
    ACCENT_GREEN = (46, 204, 113)     # 雇用ボタンなど
    ACCENT_BLUE = (52, 152, 219)      # 宣伝ボタンなど
    
    # ステータス
    STATUS_GOOD = (39, 174, 96)
    STATUS_NORMAL = (149, 165, 166)
    STATUS_BAD = (231, 76, 60)        # 解雇ボタンなど
    
    # お金
    MONEY_POSITIVE = (39, 174, 96)
    MONEY_NEGATIVE = (192, 57, 43)
    
    # マップ・建物
    GRASS = (144, 238, 144)
    BUILDING_CLASSROOM = (240, 230, 140)
    DARK_GRAY = (60, 60, 60)
    
    @staticmethod
    def get_money_color(amount: int):
        return Colors.MONEY_POSITIVE if amount >= 0 else Colors.MONEY_NEGATIVE

    @staticmethod
    def get_status_color(value: int, low=30, high=70):
        if value < low: return Colors.STATUS_BAD
        if value < high: return Colors.STATUS_NORMAL
        return Colors.STATUS_GOOD