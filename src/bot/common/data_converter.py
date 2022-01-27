from datetime import datetime, timedelta
from typing import List, Optional

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

from common import calc_oof_profit
from repository import Repository


def convert_to_doc(data: dict) -> Document:
    claim_doc: Document = Document()

    # common doc settings
    section = claim_doc.sections[-1]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(1)
    section.right_margin = Inches(0.6)

    # header
    header: Paragraph = claim_doc.add_paragraph()
    header.text = get_head_text(data["claim_data"]["head"])
    header.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    # theme
    theme: Paragraph = claim_doc.add_paragraph()
    theme.text = f"\nИсковое заявление\n{data['claim_theme']}"
    theme.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # story
    story_parts: List[str] = get_story_parts(data["claim_data"])
    for story_part in story_parts:
        story_paragraph: Paragraph = claim_doc.add_paragraph()
        story_paragraph.text = story_part
        story_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        story_paragraph.paragraph_format.first_line_indent = Inches(0.5)

    # essence
    essence: Paragraph = claim_doc.add_paragraph()
    essence.add_run("Считаю, что мои права нарушены, поскольку: ")
    essence_options: List[str] = data["claim_data"]["essence"]["chosen_options"]
    essence_options[0] = essence_options[0][0].lower() + essence_options[0][1:]
    essence.add_run(", ".join(essence_options))
    essence.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    essence.paragraph_format.first_line_indent = Inches(0.5)

    # proofs
    proofs: Paragraph = claim_doc.add_paragraph()
    proofs_data: List[str] = data["claim_data"]["proofs"]["chosen_options"]
    proofs.text = "Доводы, указанные в исковом заявлении подтверждаются следующими " + \
                  f"доказательствами: {', '.join(proofs_data)}."
    proofs.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    proofs.paragraph_format.first_line_indent = Inches(0.5)

    # law
    law: Paragraph = claim_doc.add_paragraph()
    law.text = get_law_text(data["claim_theme"])
    law.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    law.paragraph_format.first_line_indent = Inches(0.5)

    # claims
    pre_claims: Paragraph = claim_doc.add_paragraph()
    pre_claims.text = "Прошу"
    pre_claims.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # don't use style="List Number" due to issue https://github.com/python-openxml/python-docx/issues/25
    claims: Paragraph = claim_doc.add_paragraph()
    for i, claim_data in enumerate(data["claim_data"]["claims"]["claims"], start=1):
        claims.add_run(f"{i}. {claim_data}\n")

    # additions
    pre_additions: Paragraph = claim_doc.add_paragraph()
    pre_additions.text = "Приложение"
    pre_additions.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    additions: Paragraph = claim_doc.add_paragraph()
    for i, addition_data in enumerate(data["claim_data"]["additions"]["chosen_options"], start=1):
        additions.add_run(f"{i}. {addition_data}\n")

    # footer
    footer: Paragraph = claim_doc.add_paragraph()
    short_user_name: str = get_short_user_name(data['claim_data']['head']['user_name'])
    claim_date: datetime = datetime.now()
    footer.text = f"{claim_date.strftime('%d.%m.%Y'): <50}{short_user_name}"
    footer.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

    return claim_doc


def get_head_text(head_data: dict) -> str:
    lines = [
        f"В {head_data['chosen_court'][0]}",
        f"Адрес: {head_data['chosen_court'][1]}",
        "",
        f"Истец: {head_data['user_name']}",
        f"Адрес: {head_data['user_post_code']}, г. {head_data['chosen_city']}, "
        f"ул. {head_data['chosen_street']}, д. {head_data['house_chosen']}"
        f"{', кв. ' + head_data['apartment_chosen'] if head_data['apartment_chosen'] != '' else ''}",
        "",
        f"Ответчик: {head_data['chosen_employer_name']}" +
        f" (ИНН {head_data['inn']})" if head_data.get("inn") is not None else '',
        f"Адрес: {head_data['chosen_employer_address']}"
    ]

    return '\n'.join(lines)


def get_story_parts(data: dict) -> List[str]:
    full_employer_name: str = data["head"]["chosen_employer_name"] + \
        f" (ИНН {data['head']['inn']})" if data["head"].get("inn") is not None else ""
    lines = [
        f"Я, {data['head']['user_name']}, работал {data['story']['user_position']} в {full_employer_name} "
        f"с {data['story']['start_work_date'].strftime('%d.%m.%Y')} на основании трудового договора, "
        f"в соответствии с которым был принят на работу к ответчику на должность {data['story']['user_position']} "
        f"с окладом {data['story']['user_salary']} рублей.",
        data["story"]["story_conflict"]
    ]

    if data["story"]["user_employer_discussion"] != "":
        lines.append(data["story"]["user_employer_discussion"])
    return lines


def get_law_text(claim_theme: str) -> str:
    repository: Repository = Repository()
    law_data: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, "law")
    if law_data is None:
        return ""

    return f"На основании изложенного, руководствуясь {', '.join(law_data)}."


def get_short_user_name(user_name: str) -> str:
    soname, name, second_name = tuple(user_name.split(" "))
    return f"{name[0].upper()}.{second_name[0].upper()}. {soname}"


def get_oof_profit_calculation(claim_data: dict) -> Document:
    end_work_date: datetime = claim_data["story"]["end_work_date"]
    start_oof_date: datetime = end_work_date + timedelta(days=1)
    avr_salary = claim_data["story"]["avr_salary"]
    oof_profit, oof_days, months_diff, first_month_days_off = calc_oof_profit(start_oof_date, datetime.now(),
                                                                              avr_salary)

    calc_doc: Document = Document()

    # common doc settings
    section = calc_doc.sections[-1]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(1)
    section.right_margin = Inches(0.6)

    theme: Paragraph = calc_doc.add_paragraph()
    theme_font = theme.add_run("Расчет задолженности по заработной плате за время вынужденного прогула").font

    theme.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    theme_font.size = Pt(14)
    theme_font.bold = True

    calc: Paragraph = calc_doc.add_paragraph()
    calc_text: str = f"""
Средняя заработная плата за предыдущий период
Среднее число рабочих дней в месяце: 20
Cредняя заработная плата в месяц: {avr_salary}
Средний заработок за день: {avr_salary} / 20 = {avr_salary/20}

Время вынужденного прогула
Дата увольнения: {end_work_date.strftime('%d.%m.%Y')}
Дата начала вынужденного прогула: {start_oof_date.strftime('%d.%m.%Y')}
Дата подачи искового заявления: {datetime.now().strftime('%d.%m.%Y')}
Число рабочих дней за время первого месяца вынужденного прогула: {first_month_days_off}
Число месяцев за время вынужденного прогула: {months_diff}
Число рабочих дней за время вынужденного прогула: {months_diff} * 20 + {first_month_days_off} = {oof_days}

Сумма задолженности за время вынужденного прогула:
{{средний заработок за день}} * {{Число рабочих дней за время вынужденного прогула}} =
{oof_days} * {avr_salary/20} = {oof_profit}
    """
    calc_font = calc.add_run(calc_text).font
    calc_font.size = Pt(12)

    return calc_doc
