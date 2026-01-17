"""
メインゲーム画面
"""
import pygame
from typing import Callable, TYPE_CHECKING

import config
from src.graphics.colors import Colors, get_font
from src.ui.components.button import Button
from src.ui.components.panel import Panel, StatusBar

if TYPE_CHECKING:
    from src.entities.school import School
    from src.systems.time_manager import TimeManager


class GameScreen:
    """メインゲーム画面"""

    def __init__(
        self,
        school: 'School',
        time_manager: 'TimeManager',
        on_hire: Callable,
        on_fire: Callable,
        on_promote: Callable,
        on_speed_change: Callable,
    ):
        self.school = school
        self.time_manager = time_manager

        # コールバック
        self.on_hire = on_hire
        self.on_fire = on_fire
        self.on_promote = on_promote
        self.on_speed_change = on_speed_change

        # UI初期化
        self._init_panels()
        self._init_buttons()
        self._init_status_bars()

    @property
    def font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_NORMAL)

    @property
    def large_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_LARGE)

    @property
    def small_font(self) -> pygame.font.Font:
        return get_font(config.FONT_SIZE_SMALL)

    def _init_panels(self) -> None:
        """パネル初期化"""
        # 学校情報パネル（左上）
        self.info_panel = Panel(10, 10, 300, 220, "学校情報")

        # 財務パネル（左下）
        self.finance_panel = Panel(10, 240, 300, 180, "財務状況")

        # 教師リストパネル（右側）
        self.teacher_panel = Panel(config.SCREEN_WIDTH - 320, 10, 310, 450, "教師一覧")

    def _init_buttons(self) -> None:
        """ボタン初期化"""
        button_y = config.SCREEN_HEIGHT - 60

        # アクションボタン（日本語、幅を調整）
        self.hire_button = Button(
            10, button_y, 130, 45,
            "先生を雇う",
            callback=self.on_hire,
            font_size=config.FONT_SIZE_NORMAL,
            color=Colors.ACCENT_GREEN,
        )

        self.fire_button = Button(
            150, button_y, 130, 45,
            "先生を解雇",
            callback=self.on_fire,
            font_size=config.FONT_SIZE_NORMAL,
            color=Colors.STATUS_BAD,
        )

        self.promote_button = Button(
            290, button_y, 110, 45,
            "宣伝する",
            callback=self.on_promote,
            font_size=config.FONT_SIZE_NORMAL,
            color=Colors.ACCENT_BLUE,
        )

        # 速度ボタン
        speed_y = button_y
        self.speed_buttons = [
            Button(config.SCREEN_WIDTH - 180, speed_y, 50, 45, "1x",
                   callback=lambda: self.on_speed_change(1.0),
                   font_size=config.FONT_SIZE_NORMAL),
            Button(config.SCREEN_WIDTH - 125, speed_y, 50, 45, "3x",
                   callback=lambda: self.on_speed_change(3.0),
                   font_size=config.FONT_SIZE_NORMAL),
            Button(config.SCREEN_WIDTH - 70, speed_y, 60, 45, "10x",
                   callback=lambda: self.on_speed_change(10.0),
                   font_size=config.FONT_SIZE_NORMAL),
        ]

    def _init_status_bars(self) -> None:
        """ステータスバー初期化"""
        bar_x = 330
        bar_width = 220

        self.education_bar = StatusBar(bar_x, 20, bar_width, 45, "教育力")
        self.satisfaction_bar = StatusBar(bar_x, 80, bar_width, 45, "満足度")
        self.reputation_bar = StatusBar(bar_x, 140, bar_width, 45, "評判")

    def handle_event(self, event: pygame.event.Event) -> None:
        """イベント処理"""
        self.hire_button.handle_event(event)
        self.fire_button.handle_event(event)
        self.promote_button.handle_event(event)

        for btn in self.speed_buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        """更新"""
        # ボタン更新
        self.hire_button.update()
        self.fire_button.update()
        self.promote_button.update()
        for btn in self.speed_buttons:
            btn.update()

        # パネル内容更新
        self._update_info_panel()
        self._update_finance_panel()
        self._update_teacher_panel()

        # ステータスバー更新
        self.education_bar.set_value(self.school.education_quality)
        self.satisfaction_bar.set_value(self.school.satisfaction)
        self.reputation_bar.set_value(self.school.reputation)

    def _update_info_panel(self) -> None:
        """学校情報パネル更新"""
        self.info_panel.clear()
        self.info_panel.add_line(f"日付: {self.time_manager.date_string}")
        self.info_panel.add_separator()
        self.info_panel.add_line(f"生徒数: {self.school.student_count} / {self.school.capacity}人")
        self.info_panel.add_line(f"教師数: {self.school.teacher_count}人")

        # 生徒教師比率
        ratio = self.school.student_count / max(self.school.teacher_count, 1)
        ratio_color = Colors.STATUS_GOOD if ratio <= 20 else (
            Colors.STATUS_NORMAL if ratio <= 30 else Colors.STATUS_BAD
        )
        self.info_panel.add_line(f"生徒/教師: {ratio:.1f}:1", ratio_color)

    def _update_finance_panel(self) -> None:
        """財務パネル更新"""
        self.finance_panel.clear()

        # 資金
        money_color = Colors.get_money_color(self.school.money)
        self.finance_panel.add_line(f"資金: {self.school.money:,}円", money_color)

        self.finance_panel.add_separator()

        # 月間収支
        income = self.school.monthly_income
        expense = self.school.monthly_expense
        balance = self.school.monthly_balance

        self.finance_panel.add_line(f"収入: +{income:,}円", Colors.MONEY_POSITIVE)
        self.finance_panel.add_line(f"支出: -{expense:,}円", Colors.MONEY_NEGATIVE)

        balance_color = Colors.get_money_color(balance)
        balance_sign = "+" if balance >= 0 else ""
        self.finance_panel.add_line(f"収支: {balance_sign}{balance:,}円", balance_color)

    def _update_teacher_panel(self) -> None:
        """教師パネル更新"""
        self.teacher_panel.clear()

        if not self.school.teachers:
            self.teacher_panel.add_line("教師がいません")
            return

        for teacher in self.school.teachers[:8]:  # 最大8人表示
            skill_color = Colors.get_status_color(teacher.skill, 40, 70)
            self.teacher_panel.add_line(
                f"{teacher.name} ({teacher.subject})",
                Colors.UI_TEXT
            )
            self.teacher_panel.add_line(
                f"  能力:{teacher.skill} 給与:{teacher.salary//10000}万円",
                skill_color
            )

        if len(self.school.teachers) > 8:
            self.teacher_panel.add_line(f"... 他{len(self.school.teachers) - 8}人")

    def render(self, surface: pygame.Surface) -> None:
        """描画"""
        # 背景
        surface.fill(Colors.BACKGROUND)

        # 簡易マップ表示（中央エリア）
        self._render_simple_map(surface)

        # パネル
        self.info_panel.render(surface)
        self.finance_panel.render(surface)
        self.teacher_panel.render(surface)

        # ステータスバー
        self.education_bar.render(surface)
        self.satisfaction_bar.render(surface)
        self.reputation_bar.render(surface)

        # ボタン
        self.hire_button.render(surface)
        self.fire_button.render(surface)
        self.promote_button.render(surface)

        for btn in self.speed_buttons:
            btn.render(surface)

        # 速度表示
        speed_text = f"速度: {self.time_manager.game_speed:.0f}倍"
        if self.time_manager.paused:
            speed_text = "一時停止中"
        speed_surface = self.font.render(speed_text, True, Colors.UI_TEXT_DARK)
        surface.blit(speed_surface, (config.SCREEN_WIDTH - 200, config.SCREEN_HEIGHT - 95))

    def _render_simple_map(self, surface: pygame.Surface) -> None:
        """簡易マップ描画（プレースホルダー）"""
        map_rect = pygame.Rect(330, 200, 350, 300)

        # 背景（芝生）
        pygame.draw.rect(surface, Colors.GRASS, map_rect)

        # 校舎（メインビルディング）
        building_rect = pygame.Rect(map_rect.x + 50, map_rect.y + 50, 150, 100)
        pygame.draw.rect(surface, Colors.BUILDING_CLASSROOM, building_rect)
        pygame.draw.rect(surface, Colors.DARK_GRAY, building_rect, 2)

        # テキスト
        text = self.font.render("本校舎", True, Colors.UI_TEXT_DARK)
        text_rect = text.get_rect(center=building_rect.center)
        surface.blit(text, text_rect)

        # グラウンド
        ground_rect = pygame.Rect(map_rect.x + 220, map_rect.y + 150, 100, 100)
        pygame.draw.rect(surface, (200, 180, 150), ground_rect)
        pygame.draw.rect(surface, Colors.DARK_GRAY, ground_rect, 1)

        ground_text = self.font.render("校庭", True, Colors.UI_TEXT_DARK)
        ground_text_rect = ground_text.get_rect(center=ground_rect.center)
        surface.blit(ground_text, ground_text_rect)

        # マップ枠
        pygame.draw.rect(surface, Colors.DARK_GRAY, map_rect, 2)
