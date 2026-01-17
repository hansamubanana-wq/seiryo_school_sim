import pygame
from typing import Tuple
import config

class Facility:
    def __init__(self, type_id: str, grid_x: int, grid_y: int):
        self.type_id = type_id  # 'classroom', 'gym' などのID
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # 設定からデータをロード
        data = config.FACILITY_DATA.get(type_id, {})
        self.name = data.get('name', '不明な施設')
        
        # サイズ決定 (幅, 高さ) - 単位:タイル
        # 体育館と食堂は大きくする
        if type_id == 'gym':
            self.width, self.height = 4, 3
        elif type_id == 'cafeteria':
            self.width, self.height = 3, 2
        elif type_id == 'library':
            self.width, self.height = 3, 2
        else:
            self.width, self.height = 2, 2  # 教室などは2x2

        self.color = self._get_color(type_id)

    def _get_color(self, type_id: str) -> Tuple[int, int, int]:
        """種類ごとの色を返す"""
        if type_id == 'classroom': return (240, 230, 140)  # カーキ
        if type_id == 'science_lab': return (100, 149, 237) # 青
        if type_id == 'library': return (139, 69, 19)      # 茶色
        if type_id == 'gym': return (70, 130, 180)         # 濃い青
        if type_id == 'cafeteria': return (255, 165, 0)    # オレンジ
        return (200, 200, 200)

    @property
    def rect(self):
        """描画用矩形を取得（MapRendererでサイズ調整が必要だが基本値を返す）"""
        return pygame.Rect(self.grid_x, self.grid_y, self.width, self.height)