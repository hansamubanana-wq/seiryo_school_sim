"""
ボタンUIコンポーネント
"""
import pygame
from typing import Callable, Optional, Tuple

from src.graphics.colors import Colors, get_font


class Button:
    """クリック可能なボタン"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable] = None,
        font_size: int = 20,
        color: Tuple[int, int, int] = Colors.BUTTON_NORMAL,
        hover_color: Tuple[int, int, int] = Colors.BUTTON_HOVER,
        text_color: Tuple[int, int, int] = Colors.UI_TEXT,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font_size = font_size

        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

        self.is_hovered = False
        self.is_pressed = False
        self.is_enabled = True

    @property
    def font(self) -> pygame.font.Font:
        """日本語対応フォントを取得"""
        return get_font(self.font_size)

    def set_position(self, x: int, y: int) -> None:
        """位置を設定"""
        self.rect.x = x
        self.rect.y = y

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        イベント処理

        Returns:
            クリックされたかどうか
        """
        if not self.is_enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                if self.is_hovered:
                    if self.callback:
                        self.callback()
                    return True

        return False

    def update(self) -> None:
        """更新処理"""
        # マウス位置でホバー状態を更新
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        # 背景色決定
        if not self.is_enabled:
            bg_color = Colors.BUTTON_DISABLED
        elif self.is_pressed:
            bg_color = Colors.BUTTON_PRESSED
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.color

        # ボタン背景
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, self.rect, 2)

        # テキスト
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def set_enabled(self, enabled: bool) -> None:
        """有効/無効を設定"""
        self.is_enabled = enabled


class TextButton(Button):
    """テキストのみのボタン（背景なし）"""

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        if not self.is_enabled:
            color = Colors.GRAY
        elif self.is_hovered:
            color = Colors.ACCENT_BLUE
        else:
            color = self.text_color

        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

        # ホバー時にアンダーライン
        if self.is_hovered and self.is_enabled:
            underline_y = text_rect.bottom + 2
            pygame.draw.line(
                surface,
                color,
                (text_rect.left, underline_y),
                (text_rect.right, underline_y),
                1
            )
