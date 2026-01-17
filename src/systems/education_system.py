"""
教育システム - 教育力・満足度の計算と評判更新
"""
from typing import TYPE_CHECKING

import config

if TYPE_CHECKING:
    from src.entities.school import School


class EducationSystem:
    """教育品質管理システム"""

    def __init__(self, school: 'School'):
        self.school = school

    def get_education_quality(self) -> float:
        """現在の教育力を取得"""
        return self.school.education_quality

    def get_satisfaction(self) -> float:
        """現在の満足度を取得"""
        return self.school.satisfaction

    def update_reputation(self, dt: float = 1.0) -> float:
        """
        評判を更新（慣性あり）

        Args:
            dt: 経過時間（月単位、通常1.0）

        Returns:
            更新後の評判
        """
        education = self.school.education_quality
        satisfaction = self.school.satisfaction
        promotion = self.school.promotion_effect

        # 目標評判
        target_reputation = (
            education * config.REPUTATION_EDUCATION_WEIGHT +
            satisfaction * config.REPUTATION_SATISFACTION_WEIGHT +
            promotion * config.REPUTATION_PROMOTION_WEIGHT
        )

        current = self.school.reputation

        # 慣性係数（上昇は遅く、下降はやや速い）
        if target_reputation > current:
            inertia = config.REPUTATION_INERTIA_UP
        else:
            inertia = config.REPUTATION_INERTIA_DOWN

        # 評判更新
        new_reputation = current + (target_reputation - current) * inertia * dt

        # 範囲制限
        self.school.reputation = max(0, min(100, new_reputation))
        self.school.invalidate_cache()

        return self.school.reputation

    def update_teachers_monthly(self) -> None:
        """教師の月次更新"""
        for teacher in self.school.teachers:
            teacher.update_monthly()
        self.school.invalidate_cache()

    def get_teacher_student_ratio(self) -> float:
        """教師一人あたりの生徒数"""
        if not self.school.teachers:
            return float('inf')
        return self.school.student_count / len(self.school.teachers)

    def is_understaffed(self) -> bool:
        """教師不足かどうか"""
        ratio = self.get_teacher_student_ratio()
        return ratio > config.OPTIMAL_STUDENT_TEACHER_RATIO * 1.5
