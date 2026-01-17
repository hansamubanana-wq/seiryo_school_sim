import pygame
from src.entities.school import School
from src.entities.facility import Facility
from src.graphics.colors import Colors

class MapRenderer:
    def __init__(self):
        self.tile_size = 32
        self.offset_x = 330  # 左パネルの幅 + マージン
        self.offset_y = 10
        
        # マップ領域（画面右側を大きく使う）
        self.map_width = 28  # タイル数
        self.map_height = 20 # タイル数
        self.map_rect = pygame.Rect(
            self.offset_x, 
            self.offset_y, 
            self.map_width * self.tile_size, 
            self.map_height * self.tile_size
        )

    def draw(self, surface: pygame.Surface, school: School):
        """マップ全体を描画"""
        # 1. 背景（芝生）
        pygame.draw.rect(surface, (144, 238, 144), self.map_rect)  # 明るい緑
        pygame.draw.rect(surface, Colors.DARK_GRAY, self.map_rect, 2) # 枠線

        # 2. グリッド線（薄く）
        for x in range(self.map_width + 1):
            px = self.offset_x + x * self.tile_size
            pygame.draw.line(surface, (120, 200, 120), (px, self.offset_y), (px, self.offset_y + self.map_rect.height))
        for y in range(self.map_height + 1):
            py = self.offset_y + y * self.tile_size
            pygame.draw.line(surface, (120, 200, 120), (self.offset_x, py), (self.offset_x + self.map_rect.width, py))

        # 3. 建設済み施設
        for facility in school.facilities:
            rect = self._get_screen_rect(facility)
            self._draw_facility_body(surface, rect, facility.color, facility.name)

    def draw_preview(self, surface: pygame.Surface, type_id: str, mouse_pos: tuple):
        """建設プレビュー（半透明）"""
        grid_x, grid_y = self._screen_to_grid(mouse_pos)
        
        # マップ外なら描画しない
        if grid_x < 0: return

        # 仮のFacilityを作ってサイズを取得
        temp_facility = Facility(type_id, grid_x, grid_y)
        rect = self._get_screen_rect(temp_facility)

        # マップからはみ出るかチェック
        if (temp_facility.grid_x + temp_facility.width > self.map_width or 
            temp_facility.grid_y + temp_facility.height > self.map_height):
            color = (255, 100, 100) # 赤（建設不可）
        else:
            color = (100, 255, 100) # 緑（建設可能）

        # 半透明描画
        s = pygame.Surface((rect.width, rect.height))
        s.set_alpha(150)
        s.fill(color)
        surface.blit(s, (rect.x, rect.y))
        pygame.draw.rect(surface, (50, 50, 50), rect, 1)

    def _draw_facility_body(self, surface, rect, color, name):
        """建物の見た目"""
        # 本体
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (50, 50, 50), rect, 2)
        
        # 屋根っぽいライン
        pygame.draw.line(surface, (255, 255, 255), (rect.left, rect.top), (rect.right, rect.top), 3)

    def _get_screen_rect(self, facility: Facility) -> pygame.Rect:
        return pygame.Rect(
            self.offset_x + facility.grid_x * self.tile_size,
            self.offset_y + facility.grid_y * self.tile_size,
            facility.width * self.tile_size,
            facility.height * self.tile_size
        )

    def _screen_to_grid(self, pos) -> tuple:
        mx, my = pos
        if not self.map_rect.collidepoint(mx, my):
            return -1, -1
        
        rel_x = mx - self.offset_x
        rel_y = my - self.offset_y
        return int(rel_x // self.tile_size), int(rel_y // self.tile_size)