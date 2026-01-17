"""
教師生成用データ
"""
import random
from typing import Tuple

import config
from src.entities.teacher import Teacher


# 教師の名前リスト（姓）
TEACHER_SURNAMES = [
    "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
    "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水",
    "山崎", "森", "池田", "橋本", "阿部", "石川", "山下", "中島", "石井", "小川",
    "前田", "岡田", "長谷川", "藤田", "後藤", "近藤", "村上", "遠藤", "青木", "坂本",
]

# 教師の名前リスト（名）
TEACHER_FIRST_NAMES = [
    "太郎", "一郎", "健太", "翔太", "大輔", "拓也", "達也", "和也", "直樹", "誠",
    "花子", "美咲", "さくら", "陽子", "裕子", "恵子", "真理", "由美", "明美", "智子",
]

# 担当教科
SUBJECTS = [
    "国語", "数学", "英語", "理科", "社会",
    "体育", "音楽", "美術", "技術家庭", "情報"
]

# 名前のリスト（互換性のため）
TEACHER_NAMES = TEACHER_SURNAMES


def generate_random_name() -> str:
    """ランダムな教師名を生成"""
    surname = random.choice(TEACHER_SURNAMES)
    first_name = random.choice(TEACHER_FIRST_NAMES)
    return f"{surname} {first_name}"


def generate_skill_and_salary() -> Tuple[int, int]:
    """スキルと給与を生成（相関あり）"""
    # スキル分布に従ってスキルを決定
    rand = random.random()
    cumulative = 0.0

    for tier_data in config.TEACHER_SKILL_DISTRIBUTION.values():
        cumulative += tier_data['probability']
        if rand < cumulative:
            skill_min, skill_max = tier_data['range']
            skill = random.randint(skill_min, skill_max)
            break
    else:
        # フォールバック
        skill = random.randint(40, 60)

    # スキルに応じた給与（スキル高いほど高給）
    base_salary = config.TEACHER_SALARY_MIN
    skill_bonus = (skill / 100) * (config.TEACHER_SALARY_MAX - config.TEACHER_SALARY_MIN)
    # 少しランダム性を加える
    variation = random.randint(-20000, 20000)
    salary = int(base_salary + skill_bonus + variation)
    salary = max(config.TEACHER_SALARY_MIN, min(config.TEACHER_SALARY_MAX, salary))

    return skill, salary


def generate_random_teacher() -> Teacher:
    """ランダムな教師を生成"""
    name = generate_random_name()
    skill, salary = generate_skill_and_salary()
    subject = random.choice(SUBJECTS)

    return Teacher(
        name=name,
        skill=skill,
        salary=salary,
        subject=subject
    )


def generate_teacher_candidates(count: int = 3) -> list:
    """雇用候補の教師リストを生成"""
    return [generate_random_teacher() for _ in range(count)]
