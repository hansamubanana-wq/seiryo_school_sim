"""
パネルUIコンポーネント
"""
import pygame
from typing import List, Tuple

from src.graphics.colors import Colors, get_font
import config


class Panel:
    """情報表示用パネル"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        bg_color: Tuple[int, int, int] = Colors.PANEL_BG,
        alpha: int = 230,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.bg_color = bg_color
        self.alpha = alpha

        self.lines: List[Tuple[str, Tuple[int, int, int]]] = []
        self.padding = 10
        self.line_height = 26

    @property
    def font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_NORMAL)

    @property
    def title_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_LARGE)

    def clear(self) -> None:
        """表示内容をクリア"""
        self.lines.clear()

    def add_line(self, text: str, color: Tuple[int, int, int] = Colors.UI_TEXT) -> None:
        """テキスト行を追加"""
        self.lines.append((text, color))

    def add_separator(self) -> None:
        """区切り線を追加"""
        self.lines.append(("---", Colors.UI_BORDER))

    def set_position(self, x: int, y: int) -> None:
        """位置を設定"""
        self.rect.x = x
        self.rect.y = y

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        # 半透明パネル背景
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        panel_surface.fill((*self.bg_color, self.alpha))

        # 枠線
        pygame.draw.rect(panel_surface, Colors.UI_BORDER, (0, 0, self.rect.width, self.rect.height), 2)

        surface.blit(panel_surface, self.rect.topleft)

        # タイトル
        y_offset = self.padding
        if self.title:
            title_surface = self.title_font.render(self.title, True, Colors.UI_TEXT)
            surface.blit(title_surface, (self.rect.x + self.padding, self.rect.y + y_offset))
            y_offset += self.line_height + 5

            # タイトル下の区切り線
            pygame.draw.line(
                surface,
                Colors.UI_BORDER,
                (self.rect.x + self.padding, self.rect.y + y_offset),
                (self.rect.x + self.rect.width - self.padding, self.rect.y + y_offset),
                1
            )
            y_offset += 10

        # 各行を描画
        for text, color in self.lines:
            if text == "---":
                # 区切り線
                pygame.draw.line(
                    surface,
                    color,
                    (self.rect.x + self.padding, self.rect.y + y_offset + self.line_height // 2),
                    (self.rect.x + self.rect.width - self.padding, self.rect.y + y_offset + self.line_height // 2),
                    1
                )
            else:
                text_surface = self.font.render(text, True, color)
                surface.blit(text_surface, (self.rect.x + self.padding, self.rect.y + y_offset))
            y_offset += self.line_height


class StatusBar:
    """ステータスバー（プログレスバー付き）"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        max_value: float = 100.0,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value: float = 0
        self.max_value = max_value

    @property
    def font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_SMALL)

    def set_value(self, value: float) -> None:
        """値を設定"""
        self.value = max(0, min(self.max_value, value))

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        # ラベル
        label_surface = self.font.render(self.label, True, Colors.UI_TEXT)
        surface.blit(label_surface, (self.rect.x, self.rect.y))

        # バー背景
        bar_rect = pygame.Rect(
            self.rect.x,
            self.rect.y + 20,
            self.rect.width,
            self.rect.height - 20
        )
        pygame.draw.rect(surface, Colors.DARK_GRAY, bar_rect)

        # バー（値に応じた色と長さ）
        ratio = self.value / self.max_value
        fill_width = int(bar_rect.width * ratio)

        color = Colors.get_status_color(self.value)
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
        pygame.draw.rect(surface, color, fill_rect)

        # 枠
        pygame.draw.rect(surface, Colors.UI_BORDER, bar_rect, 1)

        # 値テキスト
        value_text = f"{self.value:.0f}/{self.max_value:.0f}"
        value_surface = self.font.render(value_text, True, Colors.UI_TEXT)
        value_rect = value_surface.get_rect(center=bar_rect.center)
        surface.blit(value_surface, value_rect)
