from flask import render_template
from se_models import Curriculum, Thesis, Staff
from sqlalchemy.sql.expression import func
from dataclasses import dataclass


@dataclass
class Score:
    pass_rate: int
    budget_count: int
    contract_count: int
    cost_year: str
    min_score_computer_science: int
    min_score_math: int
    min_score_russian_language: int


@dataclass
class BachelorInfo:
    score_url: str
    cost_url: str
    min_score_and_count_url: str
    year: int
    se: Score
    tp: Score


bachelor_score_info = BachelorInfo(
    score_url="https://abiturient.spbu.ru/upload/medialibrary/3c0/kcumiyzfm0hqey258970uohhdt75qnr8/priem_bac_spec_2024.pdf",
    cost_url="https://abiturient.spbu.ru/medialibrary/ru/2025/bac/cost_bac_spec_2025.pdf",
    min_score_and_count_url="https://abiturient.spbu.ru/medialibrary/ru/2025/bac/bak_spec_prog_VI_2025.pdf",
    year=2024,
    se=Score(
        pass_rate=283,
        budget_count=45,
        contract_count=12,
        cost_year="396 500 ₽",
        min_score_computer_science=55,
        min_score_math=55,
        min_score_russian_language=50,
    ),
    tp=Score(
        pass_rate=262,
        budget_count=55,
        contract_count=6,
        cost_year="457 300 ₽",
        min_score_computer_science=55,
        min_score_math=55,
        min_score_russian_language=50,
    ),
)


def bachelor_application():
    return render_template("bachelor_application.html")


def bachelor_programming_technology():
    curricula1 = (
        Curriculum.query.filter(Curriculum.course_id == 1)
        .filter(Curriculum.study_year == 1)
        .order_by(Curriculum.type)
        .all()
    )
    curricula2 = (
        Curriculum.query.filter(Curriculum.course_id == 1)
        .filter(Curriculum.study_year == 2)
        .order_by(Curriculum.type)
        .all()
    )
    curricula3 = (
        Curriculum.query.filter(Curriculum.course_id == 1)
        .filter(Curriculum.study_year == 3)
        .order_by(Curriculum.type)
        .all()
    )
    curricula4 = (
        Curriculum.query.filter(Curriculum.course_id == 1)
        .filter(Curriculum.study_year == 4)
        .order_by(Curriculum.type)
        .all()
    )

    return render_template(
        "bachelor_programming-technology.html",
        curricula1=curricula1,
        curricula2=curricula2,
        curricula3=curricula3,
        curricula4=curricula4,
        score_info=bachelor_score_info,
    )


def bachelor_software_engineering():
    curricula1 = (
        Curriculum.query.filter(Curriculum.course_id == 2)
        .filter(Curriculum.study_year == 1)
        .order_by(Curriculum.type)
        .all()
    )
    curricula2 = (
        Curriculum.query.filter(Curriculum.course_id == 2)
        .filter(Curriculum.study_year == 2)
        .order_by(Curriculum.type)
        .all()
    )
    curricula3 = (
        Curriculum.query.filter(Curriculum.course_id == 2)
        .filter(Curriculum.study_year == 3)
        .order_by(Curriculum.type)
        .all()
    )
    curricula4 = (
        Curriculum.query.filter(Curriculum.course_id == 2)
        .filter(Curriculum.study_year == 4)
        .order_by(Curriculum.type)
        .all()
    )

    return render_template(
        "bachelor_software-engineering.html",
        curricula1=curricula1,
        curricula2=curricula2,
        curricula3=curricula3,
        curricula4=curricula4,
        score_info=bachelor_score_info,
    )


def bachelor_admission():
    students = []

    records = Thesis.query.filter_by(recomended=True)
    if records.count():
        theses = records.order_by(func.random()).limit(4).all()
    else:
        theses = []
    staff = Staff.query.filter_by(still_working=True).limit(6).all()
    return render_template(
        "bachelor_admission.html",
        students=students,
        theses=theses,
        staff=staff,
        info=bachelor_score_info,
        score_info=bachelor_score_info,
    )
