from datetime import datetime
from typing import List, Optional

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches
from docx.text.paragraph import Paragraph

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
    story_parts: List[str] = ["story_begin", "story_conflict", "user_employer_discussion", "story_details"]
    for story_part in story_parts:
        story_text: str = data["claim_data"]["story"][story_part]
        if story_text == "":
            continue
        story_paragraph: Paragraph = claim_doc.add_paragraph()
        story_paragraph.text = story_text
        story_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        story_paragraph.paragraph_format.first_line_indent = Inches(0.5)

    # essence
    essence: Paragraph = claim_doc.add_paragraph()
    essence.add_run("Считаю, что мои права нарушены, поскольку: ")
    essence.add_run(", ".join(data["claim_data"]["essence"]["chosen_options"]))
    essence.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    essence.paragraph_format.first_line_indent = Inches(0.5)

    # proofs
    proofs: Paragraph = claim_doc.add_paragraph()
    proofs_data: List[str] = data["claim_data"]["proofs"]["chosen_options"]
    proofs.text = f"В качестве доказательств нарушения своих прав я предоставляю: {', '.join(proofs_data)}"
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
        f"{', кв. ' + head_data['apartment_chosen'] if head_data.get('apartment_chosen') is not None else ''}",
        "",
        f"Ответчик: {head_data['chosen_employer_name']}",
        f"Адрес: {head_data['chosen_employer_address']}"
    ]

    return '\n'.join(lines)


def get_law_text(claim_theme: str) -> str:
    repository: Repository = Repository()
    law_data: Optional[List[str]] = repository.get_claim_tmp_options(claim_theme, "law")
    if law_data is None:
        return ""

    return f"Считаю, что работодателем нарушены следующий законы: {', '.join(law_data)}."


def get_short_user_name(user_name: str) -> str:
    soname, name, second_name = tuple(user_name.split(" "))
    return f"{name[0].upper()}.{second_name[0].upper()}. {soname}"
