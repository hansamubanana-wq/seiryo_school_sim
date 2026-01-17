"""
時間管理システム
"""
from dataclasses import dataclass, field
from typing import Tuple

import config


@dataclass
class TimeManager:
    """ゲーム内時間を管理"""
    year: int = config.START_YEAR
    month: int = config.START_MONTH
    day: int = 1

    game_speed: float = config.GAME_SPEED_NORMAL
    paused: bool = False

    # 内部カウンター（秒単位の経過時間）
    _day_accumulator: float = field(default=0.0, repr=False)

    @property
    def date_string(self) -> str:
        """日付文字列"""
        return f"{self.year}年{self.month}月{self.day}日"

    @property
    def month_string(self) -> str:
        """年月文字列"""
        return f"{self.year}年{self.month}月"

    def update(self, dt: float) -> Tuple[bool, bool]:
        """
        時間を更新

        Args:
            dt: デルタタイム（秒）

        Returns:
            (月が変わったか, 年が変わったか)
        """
        if self.paused:
            return False, False

        month_changed = False
        year_changed = False

        # 時間を蓄積
        self._day_accumulator += dt * self.game_speed

        # 1秒 = 1日として処理
        while self._day_accumulator >= 1.0:
            self._day_accumulator -= 1.0
            self.day += 1

            # 月末処理
            if self.day > config.DAYS_PER_MONTH:
                self.day = 1
                self.month += 1
                month_changed = True

                # 年末処理
                if self.month > config.MONTHS_PER_YEAR:
                    self.month = 1
                    self.year += 1
                    year_changed = True

        return month_changed, year_changed

    def is_april(self) -> bool:
        """4月かどうか（入学シーズン）"""
        return self.month == 4

    def is_march(self) -> bool:
        """3月かどうか（卒業シーズン）"""
        return self.month == 3

    def set_speed(self, speed: float) -> None:
        """ゲーム速度を設定"""
        self.game_speed = speed

    def toggle_pause(self) -> None:
        """一時停止切り替え"""
        self.paused = not self.paused

    def get_elapsed_months(self, start_year: int, start_month: int) -> int:
        """開始時点からの経過月数"""
        return (self.year - start_year) * 12 + (self.month - start_month)
