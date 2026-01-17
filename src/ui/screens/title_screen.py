"""
タイトル画面
"""
import pygame
from typing import Callable

import config
from src.graphics.colors import Colors, get_font
from src.ui.components.button import Button


class TitleScreen:
    """タイトル画面"""

    def __init__(self, on_start: Callable, on_quit: Callable):
        self.on_start = on_start
        self.on_quit = on_quit

        # ボタン（日本語テキスト、幅を広げる）
        button_width = 220
        button_height = 50
        center_x = config.SCREEN_WIDTH // 2 - button_width // 2
        start_y = config.SCREEN_HEIGHT // 2 + 80

        self.start_button = Button(
            center_x, start_y,
            button_width, button_height,
            "ゲーム開始",
            callback=on_start,
            font_size=config.FONT_SIZE_LARGE,
            color=Colors.ACCENT_GREEN,
            hover_color=Colors.STATUS_GOOD,
        )

        self.quit_button = Button(
            center_x, start_y + 70,
            button_width, button_height,
            "終了",
            callback=on_quit,
            font_size=config.FONT_SIZE_LARGE,
        )

    @property
    def title_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_HUGE)

    @property
    def subtitle_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_TITLE)

    @property
    def small_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_SMALL)

    def handle_event(self, event: pygame.event.Event) -> None:
        """イベント処理"""
        self.start_button.handle_event(event)
        self.quit_button.handle_event(event)

    def update(self, dt: float) -> None:
        """更新"""
        self.start_button.update()
        self.quit_button.update()

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        # 背景
        surface.fill(Colors.BACKGROUND)

        # タイトル
        title_text = "青稜中学校・高等学校"
        title_surface = self.title_font.render(title_text, True, Colors.UI_TEXT_DARK)
        title_rect = title_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3 - 20))
        surface.blit(title_surface, title_rect)

        # サブタイトル
        subtitle_text = "〜 学校経営シミュレーション 〜"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, Colors.GRAY)
        subtitle_rect = subtitle_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3 + 50))
        surface.blit(subtitle_surface, subtitle_rect)

        # ボタン
        self.start_button.render(surface)
        self.quit_button.render(surface)

        # バージョン
        version_text = "v0.1.0 - 経営コアシステム"
        version_surface = self.small_font.render(version_text, True, Colors.GRAY)
        surface.blit(version_surface, (10, config.SCREEN_HEIGHT - 30))
