"""
ゲームマネージャー - ゲーム全体の状態管理
"""
import pygame
import random
from typing import Optional

import config
from src.core.game_state import GameState
from src.entities.school import School
from src.entities.teacher import Teacher
from src.entities.student import Student
from src.systems.time_manager import TimeManager
from src.systems.economy_system import EconomySystem, MonthlyReport
from src.systems.education_system import EducationSystem
from src.systems.enrollment_system import EnrollmentSystem
from src.data.teacher_data import generate_random_teacher
from src.ui.screens.title_screen import TitleScreen
from src.ui.screens.game_screen import GameScreen
from src.ui.dialogs.hire_dialog import HireDialog
from src.graphics.colors import get_font


class GameManager:
    """ゲーム全体の状態管理"""

    def __init__(self):
        self.state: GameState = GameState.TITLE
        self.school: Optional[School] = None
        self.time_manager: Optional[TimeManager] = None

        # システム
        self.economy_system: Optional[EconomySystem] = None
        self.education_system: Optional[EducationSystem] = None
        self.enrollment_system: Optional[EnrollmentSystem] = None

        # UI
        self.title_screen: Optional[TitleScreen] = None
        self.game_screen: Optional[GameScreen] = None
        self.hire_dialog: Optional[HireDialog] = None

        # 月次レポート
        self.current_report: Optional[MonthlyReport] = None

    def initialize(self) -> None:
        """ゲーム初期化"""
        # タイトル画面
        self.title_screen = TitleScreen(
            on_start=self._start_game,
            on_quit=self._quit_game,
        )

    def _start_game(self) -> None:
        """ゲームを開始"""
        # 学校初期化
        self.school = School()
        self.time_manager = TimeManager()

        # 初期教師配置
        for _ in range(config.INITIAL_TEACHERS):
            teacher = generate_random_teacher()
            self.school.hire_teacher(teacher)

        # 初期生徒配置（学年バランスを考慮）
        for _ in range(config.INITIAL_STUDENTS):
            grade = random.randint(1, 6)
            student = Student(grade=grade)
            self.school.students.append(student)

        # システム初期化
        self.economy_system = EconomySystem(self.school)
        self.education_system = EducationSystem(self.school)
        self.enrollment_system = EnrollmentSystem(self.school)

        # ゲーム画面初期化
        self.game_screen = GameScreen(
            school=self.school,
            time_manager=self.time_manager,
            on_hire=self._open_hire_dialog,
            on_fire=self._fire_teacher,
            on_promote=self._run_promotion,
            on_speed_change=self._change_speed,
        )

        self.state = GameState.PLAYING

    def _quit_game(self) -> None:
        """ゲーム終了"""
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _open_hire_dialog(self) -> None:
        """雇用ダイアログを開く"""
        self.hire_dialog = HireDialog(
            school=self.school,
            on_close=self._close_hire_dialog,
            on_hire=self._hire_teacher,
        )
        self.state = GameState.HIRE_DIALOG

    def _close_hire_dialog(self) -> None:
        """雇用ダイアログを閉じる"""
        self.hire_dialog = None
        self.state = GameState.PLAYING

    def _hire_teacher(self, teacher: Teacher) -> None:
        """教師を雇用"""
        self.school.hire_teacher(teacher)

    def _fire_teacher(self) -> None:
        """教師を解雇（最後に雇った教師）"""
        if self.school.teachers:
            teacher = self.school.teachers[-1]
            self.school.fire_teacher(teacher)

    def _run_promotion(self) -> None:
        """宣伝実行（ポスター）"""
        self.enrollment_system.run_promotion('poster')

    def _change_speed(self, speed: float) -> None:
        """ゲーム速度変更"""
        self.time_manager.set_speed(speed)

    def handle_event(self, event: pygame.event.Event) -> None:
        """イベント処理"""
        if self.state == GameState.TITLE:
            self.title_screen.handle_event(event)

        elif self.state == GameState.PLAYING:
            self.game_screen.handle_event(event)

            # スペースで一時停止
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.time_manager.toggle_pause()

        elif self.state == GameState.HIRE_DIALOG:
            if self.hire_dialog:
                self.hire_dialog.handle_event(event)

        elif self.state == GameState.MONTHLY_REPORT:
            # クリックでレポートを閉じる
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.state = GameState.PLAYING

    def update(self, dt: float) -> None:
        """更新処理"""
        if self.state == GameState.TITLE:
            self.title_screen.update(dt)

        elif self.state == GameState.PLAYING:
            self._update_playing(dt)

        elif self.state == GameState.HIRE_DIALOG:
            if self.hire_dialog:
                self.hire_dialog.update()

    def _update_playing(self, dt: float) -> None:
        """ゲームプレイ中の更新"""
        # 時間経過
        month_passed, year_passed = self.time_manager.update(dt)

        # 月次処理
        if month_passed:
            self._process_monthly()

        # 年次処理
        if year_passed or (month_passed and self.time_manager.is_april()):
            self._process_yearly()

        # 画面更新
        self.game_screen.update(dt)

        # ゲームオーバー判定
        if self.school.is_bankrupt():
            self.state = GameState.GAME_OVER

    def _process_monthly(self) -> None:
        """月次処理"""
        # 評判更新
        self.education_system.update_reputation()

        # 教師月次更新
        self.education_system.update_teachers_monthly()

        # 入退学処理
        satisfaction = self.school.satisfaction
        self.enrollment_system.process_monthly(satisfaction)

        # 経済処理
        self.current_report = self.economy_system.process_monthly()

        # 3月なら卒業処理
        if self.time_manager.is_march():
            self.enrollment_system.process_yearly_graduation()

    def _process_yearly(self) -> None:
        """年次処理（4月）"""
        if self.time_manager.is_april():
            # 新入生入学
            self.enrollment_system.process_yearly_enrollment()

    def render(self, surface: pygame.Surface) -> None:
        """描画処理"""
        if self.state == GameState.TITLE:
            self.title_screen.render(surface)

        elif self.state in (GameState.PLAYING, GameState.PAUSED):
            self.game_screen.render(surface)

            if self.state == GameState.PAUSED:
                self._render_pause_overlay(surface)

        elif self.state == GameState.HIRE_DIALOG:
            self.game_screen.render(surface)
            if self.hire_dialog:
                self.hire_dialog.render(surface)

        elif self.state == GameState.MONTHLY_REPORT:
            self.game_screen.render(surface)
            self._render_monthly_report(surface)

        elif self.state == GameState.GAME_OVER:
            self._render_game_over(surface)

    def _render_pause_overlay(self, surface: pygame.Surface) -> None:
        """一時停止オーバーレイ"""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        font = get_font(config.FONT_SIZE_HUGE)
        text = font.render("一時停止", True, (255, 255, 255))
        text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        surface.blit(text, text_rect)

    def _render_monthly_report(self, surface: pygame.Surface) -> None:
        """月次レポート表示"""
        if not self.current_report:
            return

        # オーバーレイ
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # レポートパネル（日本語用に拡大）
        panel_width = 450
        panel_height = 350
        panel_x = (config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (config.SCREEN_HEIGHT - panel_height) // 2

        pygame.draw.rect(surface, (50, 50, 60), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, (100, 100, 110), (panel_x, panel_y, panel_width, panel_height), 2)

        font = get_font(config.FONT_SIZE_NORMAL)
        title_font = get_font(config.FONT_SIZE_LARGE)
        y = panel_y + 20

        # タイトル
        title = title_font.render(f"月次レポート - {self.time_manager.month_string}", True, (255, 255, 255))
        surface.blit(title, (panel_x + 20, y))
        y += 45

        # 収支詳細
        report = self.current_report
        lines = [
            (f"収入: +{report.income:,}円", (100, 200, 100)),
            (f"  月謝: {report.tuition_income:,}円", (150, 150, 150)),
            (f"  補助金: {report.subsidy_income:,}円", (150, 150, 150)),
            (f"支出: -{report.expense:,}円", (200, 100, 100)),
            (f"  給与: {report.teacher_salary:,}円", (150, 150, 150)),
            (f"  その他: {report.fixed_cost + report.material_cost:,}円", (150, 150, 150)),
        ]

        for text, color in lines:
            line_surface = font.render(text, True, color)
            surface.blit(line_surface, (panel_x + 20, y))
            y += 28

        y += 15
        # 収支
        balance_color = (100, 200, 100) if report.balance >= 0 else (200, 100, 100)
        balance_sign = "+" if report.balance >= 0 else ""
        balance_text = font.render(f"収支: {balance_sign}{report.balance:,}円", True, balance_color)
        surface.blit(balance_text, (panel_x + 20, y))

        y += 35
        total_text = font.render(f"総資金: {report.total_money:,}円", True, (255, 255, 255))
        surface.blit(total_text, (panel_x + 20, y))

        # クリックで閉じる指示
        hint_font = get_font(config.FONT_SIZE_SMALL)
        hint = hint_font.render("クリックで続行", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 25))
        surface.blit(hint, hint_rect)

    def _render_game_over(self, surface: pygame.Surface) -> None:
        """ゲームオーバー画面"""
        surface.fill((30, 30, 40))

        font = get_font(config.FONT_SIZE_HUGE)
        text = font.render("ゲームオーバー", True, (200, 100, 100))
        text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 50))
        surface.blit(text, text_rect)

        sub_font = get_font(config.FONT_SIZE_LARGE)
        sub_text = sub_font.render("学校が破産しました", True, (200, 200, 200))
        sub_rect = sub_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 30))
        surface.blit(sub_text, sub_rect)

        hint_font = get_font(config.FONT_SIZE_NORMAL)
        hint = hint_font.render("ESCキーで終了", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 90))
        surface.blit(hint, hint_rect)
