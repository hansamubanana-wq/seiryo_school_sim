"""
メインゲームループ
"""
import pygame
import sys
from typing import Optional, TYPE_CHECKING

import config
from src.core.game_state import GameState

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager


class Game:
    """メインゲームクラス - Pygameの初期化とメインループを管理"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITLE)

        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # ゲームマネージャー初期化
        self.game_manager: Optional[GameManager] = None

    def initialize(self) -> None:
        """ゲーム初期化"""
        from src.managers.game_manager import GameManager
        self.game_manager = GameManager()
        self.game_manager.initialize()

    def run(self) -> None:
        """メインゲームループ"""
        self.initialize()

        while self.running:
            # デルタタイム計算（秒単位）
            dt = self.clock.tick(config.FPS) / 1000.0

            # イベント処理
            self._handle_events()

            # 更新
            self._update(dt)

            # 描画
            self._render()

        self._cleanup()

    def _handle_events(self) -> None:
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESCでゲーム終了確認（今はそのまま終了）
                    if self.game_manager.state == GameState.PLAYING:
                        self.game_manager.state = GameState.PAUSED
                    elif self.game_manager.state == GameState.PAUSED:
                        self.game_manager.state = GameState.PLAYING
                    elif self.game_manager.state == GameState.TITLE:
                        self.running = False

            # ゲームマネージャーにイベントを渡す
            if self.game_manager:
                self.game_manager.handle_event(event)

    def _update(self, dt: float) -> None:
        """ゲーム状態更新"""
        if self.game_manager:
            self.game_manager.update(dt)

    def _render(self) -> None:
        """描画処理"""
        if self.game_manager:
            self.game_manager.render(self.screen)
        pygame.display.flip()

    def _cleanup(self) -> None:
        """終了処理"""
        pygame.quit()
        sys.exit()
