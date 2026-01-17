"""
教師雇用ダイアログ
"""
import pygame
from typing import Callable, List, TYPE_CHECKING

import config
from src.graphics.colors import Colors, get_font
from src.ui.components.button import Button
from src.entities.teacher import Teacher
from src.data.teacher_data import generate_teacher_candidates

if TYPE_CHECKING:
    from src.entities.school import School


class HireDialog:
    """教師雇用ダイアログ"""

    def __init__(
        self,
        school: 'School',
        on_close: Callable,
        on_hire: Callable[[Teacher], None],
    ):
        self.school = school
        self.on_close = on_close
        self.on_hire = on_hire

        # ダイアログサイズ（日本語に合わせて拡大）
        self.width = 650
        self.height = 480
        self.x = (config.SCREEN_WIDTH - self.width) // 2
        self.y = (config.SCREEN_HEIGHT - self.height) // 2

        # 候補者リスト
        self.candidates: List[Teacher] = []
        self.refresh_candidates()

        # UI
        self._init_ui()

    @property
    def font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_NORMAL)

    @property
    def title_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_LARGE)

    @property
    def small_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_SMALL)

    def refresh_candidates(self) -> None:
        """候補者リストを更新"""
        self.candidates = generate_teacher_candidates(4)

    def _init_ui(self) -> None:
        """UI初期化"""
        # 閉じるボタン
        self.close_button = Button(
            self.x + self.width - 100,
            self.y + self.height - 55,
            90, 45,
            "閉じる",
            callback=self.on_close,
            font_size=config.FONT_SIZE_NORMAL,
        )

        # リフレッシュボタン
        self.refresh_button = Button(
            self.x + 10,
            self.y + self.height - 55,
            150, 45,
            "別の候補者",
            callback=self._on_refresh,
            font_size=config.FONT_SIZE_NORMAL,
            color=Colors.ACCENT_BLUE,
        )

        # 雇用ボタン（候補者ごと）
        self.hire_buttons: List[Button] = []
        self._update_hire_buttons()

    def _on_refresh(self) -> None:
        """候補者リフレッシュ"""
        self.refresh_candidates()
        self._update_hire_buttons()

    def _update_hire_buttons(self) -> None:
        """雇用ボタンを更新"""
        self.hire_buttons.clear()

        for i, candidate in enumerate(self.candidates):
            y_pos = self.y + 90 + i * 90

            def make_hire_callback(teacher):
                return lambda: self._hire_teacher(teacher)

            btn = Button(
                self.x + self.width - 100,
                y_pos + 25,
                80, 40,
                "雇用",
                callback=make_hire_callback(candidate),
                font_size=config.FONT_SIZE_NORMAL,
                color=Colors.ACCENT_GREEN,
            )

            # 雇用可能かチェック
            btn.set_enabled(self.school.can_afford(candidate.salary))

            self.hire_buttons.append(btn)

    def _hire_teacher(self, teacher: Teacher) -> None:
        """教師を雇用"""
        self.on_hire(teacher)
        self.refresh_candidates()
        self._update_hire_buttons()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        self.close_button.handle_event(event)
        self.refresh_button.handle_event(event)

        for btn in self.hire_buttons:
            btn.handle_event(event)

        # ダイアログ外クリックで閉じる
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if not dialog_rect.collidepoint(event.pos):
                    self.on_close()
                    return True

        return True

    def update(self) -> None:
        """更新"""
        self.close_button.update()
        self.refresh_button.update()
        for btn in self.hire_buttons:
            btn.update()

        # 雇用可能状態を更新
        for i, btn in enumerate(self.hire_buttons):
            if i < len(self.candidates):
                btn.set_enabled(self.school.can_afford(self.candidates[i].salary))

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        # オーバーレイ
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # ダイアログ背景
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, Colors.PANEL_BG, dialog_rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, dialog_rect, 3)

        # タイトル
        title = self.title_font.render("教師を雇用する", True, Colors.UI_TEXT)
        surface.blit(title, (self.x + 20, self.y + 15))

        # 現在の資金
        money_text = f"利用可能資金: {self.school.money:,}円"
        money_surface = self.font.render(money_text, True, Colors.MONEY_POSITIVE)
        surface.blit(money_surface, (self.x + 20, self.y + 55))

        # 候補者リスト
        for i, candidate in enumerate(self.candidates):
            y_pos = self.y + 90 + i * 90
            self._render_candidate(surface, candidate, y_pos)

        # ボタン
        self.close_button.render(surface)
        self.refresh_button.render(surface)
        for btn in self.hire_buttons:
            btn.render(surface)

    def _render_candidate(self, surface: pygame.Surface, teacher: Teacher, y: int) -> None:
        """候補者を描画"""
        # 背景
        bg_rect = pygame.Rect(self.x + 10, y, self.width - 120, 80)
        pygame.draw.rect(surface, Colors.PANEL_BG_LIGHT, bg_rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, bg_rect, 1)

        # 名前
        name_text = self.font.render(teacher.name, True, Colors.UI_TEXT)
        surface.blit(name_text, (self.x + 20, y + 10))

        # 教科
        subject_text = self.font.render(f"担当: {teacher.subject}", True, Colors.LIGHT_GRAY)
        surface.blit(subject_text, (self.x + 220, y + 10))

        # スキル
        skill_color = Colors.get_status_color(teacher.skill, 40, 70)
        skill_text = self.font.render(f"教育力: {teacher.skill}", True, skill_color)
        surface.blit(skill_text, (self.x + 20, y + 40))

        # 給与
        salary_text = self.font.render(f"月給: {teacher.salary:,}円", True, Colors.MONEY_NEGATIVE)
        surface.blit(salary_text, (self.x + 220, y + 40))
