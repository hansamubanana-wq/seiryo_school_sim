"""
入退学システム - 生徒の入学・退学・卒業処理
"""
from dataclasses import dataclass
from typing import List, TYPE_CHECKING
import random
import math

import config
from src.entities.student import Student

if TYPE_CHECKING:
    from src.entities.school import School


@dataclass
class EnrollmentReport:
    """入退学レポート"""
    new_students: int = 0
    dropouts: int = 0
    graduates: int = 0
    advanced: int = 0       # 進級した生徒数


class EnrollmentSystem:
    """入学・退学管理システム"""

    def __init__(self, school: 'School'):
        self.school = school

    def process_monthly_dropouts(self, satisfaction: float) -> int:
        """
        月次の退学処理

        Returns:
            退学者数
        """
        dropouts = 0

        # 退学判定（リストのコピーを作成して反復）
        for student in self.school.students[:]:
            if student.will_dropout(satisfaction):
                self.school.remove_student(student)
                dropouts += 1
            else:
                # 月次更新
                student.update_monthly(satisfaction)

        return dropouts

    def decay_promotion_effect(self) -> None:
        """宣伝効果の減衰処理（月次）"""
        self.school.promotion_effect *= (1 - config.PROMOTION_DECAY_RATE)
        if self.school.promotion_effect < 0.1:
            self.school.promotion_effect = 0

    def process_yearly_graduation(self) -> tuple:
        """
        年次の卒業・進級処理（3月に実行）

        Returns:
            (卒業者数, 進級者数)
        """
        graduates = 0
        advanced = 0

        # 卒業・進級判定（リストのコピーを作成）
        for student in self.school.students[:]:
            if student.should_graduate():
                self.school.remove_student(student)
                graduates += 1
            else:
                student.advance_grade()
                advanced += 1

        return graduates, advanced

    def process_yearly_enrollment(self) -> int:
        """
        年次の入学処理（4月に実行）

        Returns:
            入学者数
        """
        reputation = self.school.reputation
        promotion = self.school.promotion_effect
        capacity = self.school.capacity
        current_students = self.school.student_count

        # 応募者数計算
        base_applicants = config.BASE_APPLICANTS + reputation * config.APPLICANTS_PER_REPUTATION
        promotion_bonus = base_applicants * (promotion / 100) * config.PROMOTION_BONUS_RATE
        total_applicants = int(base_applicants + promotion_bonus)

        # 空きキャパシティを超えない
        available = capacity - current_students
        new_students = min(total_applicants, available)
        new_students = max(0, new_students)

        # 新入生を追加（中1 = grade 1）
        for _ in range(new_students):
            student = Student(grade=1)
            self.school.add_student(student)

        return new_students

    def run_promotion(self, promotion_type: str) -> bool:
        """
        宣伝活動を実行

        Args:
            promotion_type: 宣伝タイプ（'poster', 'newspaper', etc.）

        Returns:
            成功したかどうか
        """
        if promotion_type not in config.PROMOTION_OPTIONS:
            return False

        promo = config.PROMOTION_OPTIONS[promotion_type]
        cost = promo['cost']
        effect = promo['effect']

        if not self.school.can_afford(cost):
            return False

        self.school.spend(cost)

        # 効果は加算（ただし100が上限）
        self.school.promotion_effect = min(100, self.school.promotion_effect + effect)

        return True

    def process_monthly(self, satisfaction: float) -> EnrollmentReport:
        """
        月次処理をまとめて実行

        Returns:
            EnrollmentReport
        """
        dropouts = self.process_monthly_dropouts(satisfaction)
        self.decay_promotion_effect()

        return EnrollmentReport(dropouts=dropouts)

    def get_projected_applicants(self) -> int:
        """次年度の予想応募者数"""
        reputation = self.school.reputation
        promotion = self.school.promotion_effect

        base = config.BASE_APPLICANTS + reputation * config.APPLICANTS_PER_REPUTATION
        bonus = base * (promotion / 100) * config.PROMOTION_BONUS_RATE

        return int(base + bonus)
