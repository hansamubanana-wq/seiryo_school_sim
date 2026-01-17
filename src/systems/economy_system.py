"""
経済システム - 収入・支出の計算と処理
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.school import School


@dataclass
class MonthlyReport:
    """月次経済レポート"""
    income: int
    expense: int
    balance: int
    total_money: int

    teacher_salary: int = 0
    facility_maintenance: int = 0
    material_cost: int = 0
    fixed_cost: int = 0

    tuition_income: int = 0
    subsidy_income: int = 0


class EconomySystem:
    """経済・財務管理システム"""

    def __init__(self, school: 'School'):
        self.school = school
        self.monthly_reports: List[MonthlyReport] = []

    def process_monthly(self) -> MonthlyReport:
        """月次経済処理を実行し、レポートを返す"""
        import config

        # 収入計算
        student_count = self.school.student_count
        reputation = self.school.reputation
        education = self.school.education_quality

        tuition = int(student_count * config.BASE_TUITION *
                      (1 + config.REPUTATION_BONUS_RATE * reputation / 100))
        subsidy = int(student_count * config.SUBSIDY_PER_STUDENT * education / 100)
        income = tuition + subsidy

        # 支出計算
        teacher_salary = sum(t.salary for t in self.school.teachers)
        facility_maintenance = self.school.capacity * config.CAPACITY_MAINTENANCE_RATE
        material_cost = student_count * config.MATERIAL_COST_PER_STUDENT
        fixed_cost = config.FIXED_MONTHLY_COST
        expense = teacher_salary + facility_maintenance + material_cost + fixed_cost

        # 収支を反映
        balance = income - expense
        self.school.money += balance

        # レポート作成
        report = MonthlyReport(
            income=income,
            expense=expense,
            balance=balance,
            total_money=self.school.money,
            teacher_salary=teacher_salary,
            facility_maintenance=facility_maintenance,
            material_cost=material_cost,
            fixed_cost=fixed_cost,
            tuition_income=tuition,
            subsidy_income=subsidy,
        )

        self.monthly_reports.append(report)

        # 履歴は最大24ヶ月分保持
        if len(self.monthly_reports) > 24:
            self.monthly_reports.pop(0)

        return report

    def get_average_balance(self, months: int = 6) -> float:
        """直近N ヶ月の平均収支"""
        if not self.monthly_reports:
            return 0.0
        recent = self.monthly_reports[-months:]
        return sum(r.balance for r in recent) / len(recent)

    def can_afford(self, cost: int) -> bool:
        """支払い可能かチェック"""
        return self.school.can_afford(cost)

    def spend(self, amount: int, description: str = "") -> bool:
        """支出処理"""
        return self.school.spend(amount)
