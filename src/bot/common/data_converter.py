from io import StringIO
from xml.etree.ElementTree import ElementTree, Element

from defusedxml.ElementTree import parse, tostring
from docx.document import Document
from docx.settings import Settings
from docx.shared import Inches
from htmldocx import HtmlToDocx


def convert_to_html(data: dict):
    with open("../../../resources/claim_tmp.html") as html_tmp_file:
        # html_tmp_raw: str = html_tmp_file.read()

        tree: ElementTree = parse(html_tmp_file)
        head_node: Element = tree.find(".//td[@id='head']/pre")
        head_data: str = get_head_data(data["claim_data"]["head"])
        head_node.text = head_data

        filled_claim: str = tostring(tree.getroot(), encoding="utf-8", method="xml")
        new_parser = HtmlToDocx()
        claim_docx: Document = new_parser.parse_html_string(filled_claim)
        section = claim_docx.sections[-1]
        section.top_margin = Inches(0.8)  # Верхний отступ
        section.bottom_margin = Inches(0.8)  # Нижний отступ
        section.left_margin = Inches(0.5)  # Отступ слева
        section.right_margin = Inches(0.5)  # Отступ справа
        claim_docx.save("1.docx")


def get_head_data(head_data: dict) -> str:
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
