"""
メインゲーム画面（建設機能付き）
"""
import pygame
from typing import Callable, TYPE_CHECKING, Optional

import config
from src.graphics.colors import Colors, get_font
from src.ui.components.button import Button
from src.ui.components.panel import Panel, StatusBar
from src.graphics.map_renderer import MapRenderer  # 追加
from src.ui.dialogs.build_dialog import BuildDialog # 追加

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
        
        # マップレンダラー
        self.map_renderer = MapRenderer()
        
        # 建設モード状態
        self.is_build_mode = False
        self.selected_building_type: Optional[str] = None
        self.show_build_dialog = False
        self.build_dialog: Optional[BuildDialog] = None

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

    def _init_panels(self) -> None:
        self.info_panel = Panel(10, 10, 300, 220, "学校情報")
        self.finance_panel = Panel(10, 240, 300, 180, "財務状況")
        # 教師パネルの位置を調整（マップに被らないように左下に移動するか、一時的に非表示にするなど）
        # ここではマップが大きくなったので、教師パネルを少し下に縮めるか移動します
        self.teacher_panel = Panel(10, 430, 300, 150, "教師一覧")

    def _init_buttons(self) -> None:
        button_y = config.SCREEN_HEIGHT - 60

        self.hire_button = Button(
            10, button_y, 110, 45, "先生雇用",
            callback=self.on_hire, color=Colors.ACCENT_GREEN,
        )

        self.fire_button = Button(
            130, button_y, 110, 45, "先生解雇",
            callback=self.on_fire, color=Colors.STATUS_BAD,
        )

        self.promote_button = Button(
            250, button_y, 110, 45, "宣伝",
            callback=self.on_promote, color=Colors.ACCENT_BLUE,
        )
        
        # ★建設ボタンを追加
        self.build_button = Button(
            370, button_y, 110, 45, "施設建設",
            callback=self._open_build_dialog, color=(255, 140, 0), # オレンジ
        )

        # 速度ボタン
        speed_y = button_y
        self.speed_buttons = [
            Button(config.SCREEN_WIDTH - 180, speed_y, 50, 45, "1x", callback=lambda: self.on_speed_change(1.0)),
            Button(config.SCREEN_WIDTH - 125, speed_y, 50, 45, "3x", callback=lambda: self.on_speed_change(3.0)),
            Button(config.SCREEN_WIDTH - 70, speed_y, 60, 45, "10x", callback=lambda: self.on_speed_change(10.0)),
        ]

    def _init_status_bars(self) -> None:
        # ステータスバーをマップの上に被らない位置へ（とりあえず右上に）
        # マップが右側を占有するので、バーは左パネルの上に重ねるか、マップの上にオーバーレイするか
        # ここでは「学校情報パネル」の中に数値を出すだけにして、バーは一旦マップ上部に配置
        bar_x = 350
        bar_width = 200
        # 簡易表示に変更
        self.education_bar = StatusBar(bar_x, 10, bar_width, 30, "教育")
        self.satisfaction_bar = StatusBar(bar_x + 220, 10, bar_width, 30, "満足")
        self.reputation_bar = StatusBar(bar_x + 440, 10, bar_width, 30, "評判")

    # --- 建設関連メソッド ---
    def _open_build_dialog(self):
        self.show_build_dialog = True
        self.is_build_mode = False # ダイアログが開くときはモード解除
        self.build_dialog = BuildDialog(
            on_select_callback=self._on_building_selected,
            on_close_callback=self._close_build_dialog
        )
    
    def _close_build_dialog(self):
        self.show_build_dialog = False
        self.build_dialog = None

    def _on_building_selected(self, type_id):
        """建設ダイアログで施設を選んだら建設モードへ"""
        self.selected_building_type = type_id
        self.is_build_mode = True
        self._close_build_dialog()

    def handle_event(self, event: pygame.event.Event) -> None:
        # ダイアログ表示中はダイアログのイベントのみ
        if self.show_build_dialog and self.build_dialog:
            self.build_dialog.handle_event(event)
            return

        # 建設モード中のクリック処理
        if self.is_build_mode and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # 左クリック
                grid_x, grid_y = self.map_renderer._screen_to_grid(event.pos)
                if grid_x >= 0:
                    # 建設実行！
                    if self.school.add_facility(self.selected_building_type, grid_x, grid_y):
                        # 成功したらモード継続（連続建設）するか、終了するか
                        # ここではモード解除
                        self.is_build_mode = False
                        self.selected_building_type = None
            
            elif event.button == 3: # 右クリック
                self.is_build_mode = False # キャンセル
                self.selected_building_type = None
            return

        # 通常モードのUIイベント
        self.hire_button.handle_event(event)
        self.fire_button.handle_event(event)
        self.promote_button.handle_event(event)
        self.build_button.handle_event(event) # 追加

        for btn in self.speed_buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        if self.show_build_dialog: return

        self.hire_button.update()
        self.fire_button.update()
        self.promote_button.update()
        self.build_button.update()
        for btn in self.speed_buttons:
            btn.update()

        self._update_info_panel()
        self._update_finance_panel()
        self._update_teacher_panel()

        self.education_bar.set_value(self.school.education_quality)
        self.satisfaction_bar.set_value(self.school.satisfaction)
        self.reputation_bar.set_value(self.school.reputation)

    def _update_info_panel(self) -> None:
        self.info_panel.clear()
        self.info_panel.add_line(f"{self.time_manager.date_string}")
        self.info_panel.add_line(f"生徒: {self.school.student_count}/{self.school.capacity}")
        self.info_panel.add_line(f"教師: {self.school.teacher_count}")

    def _update_finance_panel(self) -> None:
        self.finance_panel.clear()
        money_color = Colors.get_money_color(self.school.money)
        self.finance_panel.add_line(f"資金: {self.school.money:,}", money_color)
        income = self.school.monthly_income
        expense = self.school.monthly_expense
        balance = self.school.monthly_balance
        self.finance_panel.add_line(f"収支: {balance:+,}", Colors.get_money_color(balance))

    def _update_teacher_panel(self) -> None:
        self.teacher_panel.clear()
        for teacher in self.school.teachers[:4]:
            self.teacher_panel.add_line(f"{teacher.name} ({teacher.subject})", Colors.UI_TEXT)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(Colors.BACKGROUND)

        # 1. マップ描画（最背面）
        self.map_renderer.draw(surface, self.school)

        # 2. 建設プレビュー
        if self.is_build_mode and self.selected_building_type:
            mx, my = pygame.mouse.get_pos()
            self.map_renderer.draw_preview(surface, self.selected_building_type, (mx, my))

        # 3. UIパネルとボタン
        self.info_panel.render(surface)
        self.finance_panel.render(surface)
        self.teacher_panel.render(surface)
        
        self.education_bar.render(surface)
        self.satisfaction_bar.render(surface)
        self.reputation_bar.render(surface)

        self.hire_button.render(surface)
        self.fire_button.render(surface)
        self.promote_button.render(surface)
        self.build_button.render(surface) # 追加

        for btn in self.speed_buttons:
            btn.render(surface)

        # 4. ダイアログ（最前面）
        if self.show_build_dialog and self.build_dialog:
            self.build_dialog.render(surface)