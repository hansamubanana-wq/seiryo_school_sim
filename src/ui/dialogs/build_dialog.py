import pygame
import config
from src.graphics.colors import Colors, get_font
from src.ui.components.button import Button

class BuildDialog:
    def __init__(self, on_select_callback, on_close_callback):
        self.on_select = on_select_callback
        self.on_close = on_close_callback
        
        self.width = 600
        self.height = 500
        self.rect = pygame.Rect(
            (config.SCREEN_WIDTH - self.width) // 2,
            (config.SCREEN_HEIGHT - self.height) // 2,
            self.width, self.height
        )
        
        self.buttons = []
        self._init_ui()

    def _init_ui(self):
        # 閉じるボタン
        self.buttons.append(Button(
            self.rect.right - 110, self.rect.bottom - 60, 100, 40, "閉じる",
            callback=self.on_close, color=Colors.STATUS_NORMAL
        ))

        # 施設リストボタン
        y = self.rect.top + 80
        for key, data in config.FACILITY_DATA.items():
            # ボタンテキストを作成（名称 + 価格）
            text = f"{data['name']} (¥{data['cost']//10000}万)"
            
            # コールバック関数を生成（変数をキャプチャするためにデフォルト引数を使用）
            def make_callback(k):
                return lambda: self.on_select(k)

            btn = Button(
                self.rect.left + 50, y, 500, 50, text,
                callback=make_callback(key),
                color=Colors.UI_PANEL_BG
            )
            self.buttons.append(btn)
            y += 60

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def render(self, surface):
        # 半透明の背景（モーダル用）
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # ダイアログ本体
        pygame.draw.rect(surface, Colors.UI_BG, self.rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, self.rect, 2)

        # タイトル
        title = get_font(32).render("施設建設", True, Colors.UI_TEXT)
        surface.blit(title, (self.rect.left + 20, self.rect.top + 20))

        # ボタン
        for btn in self.buttons:
            btn.render(surface)
            
            # 効果の説明などをボタンの右に表示（簡易版）
            # ここでは省略