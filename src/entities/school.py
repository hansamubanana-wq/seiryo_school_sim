"""
学校エンティティ - ゲームの中心となるクラス
"""
from dataclasses import dataclass, field
from typing import List, Optional
import random

import config
from src.entities.teacher import Teacher
from src.entities.student import Student


@dataclass
class School:
    """学校クラス - 全てのゲームデータを保持"""
    name: str = "青稜中学校・高等学校"
    money: int = config.INITIAL_MONEY
    reputation: float = config.INITIAL_REPUTATION
    capacity: int = config.INITIAL_CAPACITY

    teachers: List[Teacher] = field(default_factory=list)
    students: List[Student] = field(default_factory=list)

    # 宣伝効果（0-100）
    promotion_effect: float = 0.0

    # 統計用キャッシュ
    _cached_education: Optional[float] = field(default=None, repr=False)
    _cached_satisfaction: Optional[float] = field(default=None, repr=False)

    def invalidate_cache(self) -> None:
        """キャッシュを無効化"""
        self._cached_education = None
        self._cached_satisfaction = None

    @property
    def student_count(self) -> int:
        """生徒数"""
        return len(self.students)

    @property
    def teacher_count(self) -> int:
        """教師数"""
        return len(self.teachers)

    @property
    def education_quality(self) -> float:
        """教育力を計算 (0-100)"""
        if self._cached_education is not None:
            return self._cached_education

        if not self.teachers:
            self._cached_education = 10.0
            return self._cached_education

        # 教師の平均スキル
        teacher_skill_avg = sum(t.skill for t in self.teachers) / len(self.teachers)

        # 教師比率効果（適正1:20）
        student_count = max(self.student_count, 1)
        teacher_ratio = len(self.teachers) / student_count * config.OPTIMAL_STUDENT_TEACHER_RATIO
        teacher_ratio = min(teacher_ratio, config.EDUCATION_RATIO_CAP)

        # 施設ボーナス（現状は0、Phase 6で実装）
        facility_bonus = 0

        # 教育力計算
        education = (teacher_skill_avg * teacher_ratio * config.EDUCATION_TEACHER_WEIGHT +
                     facility_bonus * config.EDUCATION_FACILITY_WEIGHT)

        self._cached_education = max(0, min(100, education))
        return self._cached_education

    @property
    def satisfaction(self) -> float:
        """満足度を計算 (0-100)"""
        if self._cached_satisfaction is not None:
            return self._cached_satisfaction

        education = self.education_quality
        student_count = self.student_count
        capacity = max(self.capacity, 1)

        # 密度ペナルティ
        density = student_count / capacity
        if density <= config.DENSITY_THRESHOLD_LOW:
            density_factor = 1.0
        elif density <= config.DENSITY_THRESHOLD_HIGH:
            # 80-100%: 緩やかに低下
            density_factor = 1.0 - (density - config.DENSITY_THRESHOLD_LOW) * 1.5
        else:
            # 100%超: 急激に低下
            density_factor = max(0.1, 0.7 - (density - config.DENSITY_THRESHOLD_HIGH) * 2.0)

        # 施設満足度（現状は0、Phase 6で実装）
        facility_satisfaction = 0

        # 満足度計算
        satisfaction = ((education * config.SATISFACTION_EDUCATION_WEIGHT +
                        facility_satisfaction * config.SATISFACTION_FACILITY_WEIGHT) *
                       density_factor + config.SATISFACTION_BASE)

        self._cached_satisfaction = max(0, min(100, satisfaction))
        return self._cached_satisfaction

    @property
    def monthly_income(self) -> int:
        """月間収入を計算"""
        student_count = self.student_count
        reputation = self.reputation
        education = self.education_quality

        # 基本月謝収入
        tuition = student_count * config.BASE_TUITION * (1 + config.REPUTATION_BONUS_RATE * reputation / 100)

        # 教育補助金
        subsidy = student_count * config.SUBSIDY_PER_STUDENT * education / 100

        return int(tuition + subsidy)

    @property
    def monthly_expense(self) -> int:
        """月間支出を計算"""
        # 教師給与
        teacher_salary = sum(t.salary for t in self.teachers)

        # 施設維持費
        facility_maintenance = self.capacity * config.CAPACITY_MAINTENANCE_RATE

        # 教材費
        material_cost = self.student_count * config.MATERIAL_COST_PER_STUDENT

        # 固定費
        fixed_cost = config.FIXED_MONTHLY_COST

        return teacher_salary + facility_maintenance + material_cost + fixed_cost

    @property
    def monthly_balance(self) -> int:
        """月間収支"""
        return self.monthly_income - self.monthly_expense

    def hire_teacher(self, teacher: Teacher) -> bool:
        """教師を雇用"""
        self.teachers.append(teacher)
        self.invalidate_cache()
        return True

    def fire_teacher(self, teacher: Teacher) -> bool:
        """教師を解雇"""
        if teacher in self.teachers:
            self.teachers.remove(teacher)
            self.invalidate_cache()
            return True
        return False

    def add_student(self, student: Student) -> bool:
        """生徒を追加"""
        if self.student_count < self.capacity:
            self.students.append(student)
            self.invalidate_cache()
            return True
        return False

    def remove_student(self, student: Student) -> bool:
        """生徒を削除（退学・卒業）"""
        if student in self.students:
            self.students.remove(student)
            self.invalidate_cache()
            return True
        return False

    def can_afford(self, cost: int) -> bool:
        """支払い可能かチェック"""
        return self.money >= cost

    def spend(self, amount: int) -> bool:
        """支出処理"""
        if self.can_afford(amount):
            self.money -= amount
            return True
        return False

    def receive(self, amount: int) -> None:
        """収入処理"""
        self.money += amount

    def is_bankrupt(self) -> bool:
        """破産判定"""
        return self.money <= config.BANKRUPTCY_THRESHOLD
