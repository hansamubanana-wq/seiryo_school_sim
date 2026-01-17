"""
生徒エンティティ
"""
from dataclasses import dataclass, field
from uuid import uuid4
import random

import config


@dataclass
class Student:
    """生徒クラス"""
    grade: int              # 学年 (1-6: 中1-高3)

    id: str = field(default_factory=lambda: uuid4().hex[:8])
    satisfaction: float = 50.0      # 個人満足度 (0-100)
    academic: int = field(default_factory=lambda: random.randint(30, 70))  # 学力 (0-100)
    months_enrolled: int = 0        # 在籍月数

    def update_monthly(self, school_satisfaction: float) -> None:
        """月次更新"""
        self.months_enrolled += 1
        # 個人満足度を学校満足度に近づける
        self.satisfaction = self.satisfaction * 0.8 + school_satisfaction * 0.2

    def will_dropout(self, school_satisfaction: float) -> bool:
        """退学判定"""
        dropout_rate = self._calculate_dropout_rate(school_satisfaction)
        return random.random() < dropout_rate

    def _calculate_dropout_rate(self, satisfaction: float) -> float:
        """退学率計算"""
        if satisfaction >= 80:
            return config.DROPOUT_RATE_HIGH_SATISFACTION
        elif satisfaction >= 50:
            # 50-80の間で線形補間
            ratio = (satisfaction - 50) / 30
            return (config.DROPOUT_RATE_MEDIUM_SATISFACTION * (1 - ratio) +
                    config.DROPOUT_RATE_HIGH_SATISFACTION * ratio)
        elif satisfaction >= 20:
            # 20-50の間で線形補間
            ratio = (satisfaction - 20) / 30
            return (config.DROPOUT_RATE_LOW_SATISFACTION * (1 - ratio) +
                    config.DROPOUT_RATE_MEDIUM_SATISFACTION * ratio)
        else:
            # 0-20の間
            ratio = satisfaction / 20
            return (config.DROPOUT_RATE_VERY_LOW * (1 - ratio) +
                    config.DROPOUT_RATE_LOW_SATISFACTION * ratio)

    def should_graduate(self) -> bool:
        """卒業判定（3月時点で呼び出す）"""
        # 中3(grade=3)の30%が外部高校へ、高3(grade=6)は全員卒業
        if self.grade == 6:
            return True
        elif self.grade == 3:
            return random.random() < 0.3
        return False

    def advance_grade(self) -> None:
        """進級処理"""
        if self.grade < 6:
            self.grade += 1

    def __repr__(self) -> str:
        return f"Student(grade={self.grade}, academic={self.academic})"
