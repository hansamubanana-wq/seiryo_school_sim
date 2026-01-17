"""
教師エンティティ
"""
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Teacher:
    """教師クラス"""
    name: str
    skill: int              # 教育能力 (0-100)
    salary: int             # 月給（円）
    subject: str            # 担当教科

    id: str = field(default_factory=lambda: uuid4().hex[:8])
    experience: int = 0     # 勤続月数
    morale: float = 50.0    # 士気 (0-100)

    def update_monthly(self) -> None:
        """月次更新（経験値上昇など）"""
        self.experience += 1
        # 1年ごとにスキル微増（最大100）
        if self.experience % 12 == 0 and self.experience > 0:
            self.skill = min(100, self.skill + 1)

    def __repr__(self) -> str:
        return f"Teacher({self.name}, {self.subject}, skill={self.skill})"
