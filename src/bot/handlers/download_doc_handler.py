from io import BytesIO
from typing import Optional

from aiogram import Dispatcher, types
from aiogram.dispatcher import filters
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from common.data_converter import convert_to_doc
from keyboards import emojis
from keyboards.claim_parts import PART_NAMES, get_claim_parts_kb
from repository import Repository
from docx.document import Document


async def download_doc(message: types.Message):
    repository: Repository = Repository()
    claim_data: dict = repository.get_claim_data(message.from_user.id)
    if not any([part_name in claim_data["claim_data"].keys() for part_name in PART_NAMES]):
        claim_parts_kb: ReplyKeyboardMarkup = get_claim_parts_kb(message.from_user.id)
        await message.reply("Пожалуйста, сперва заполните все разделы.", reply_markup=claim_parts_kb)
        return

    claim_doc: Document = convert_to_doc(claim_data)
    with BytesIO() as claim_doc_file:
        claim_doc.save(claim_doc_file)
        claim_doc_file.seek(0)
        claim_doc_file.name = "заявление.docx"
        await message.answer_document(document=claim_doc_file,
                                      disable_content_type_detection=True,
                                      reply_markup=ReplyKeyboardRemove())

    # remove data from db
    previous_claim_data: Optional[dict] = repository.get_claim_data(message.from_user.id, claim_data["claim_theme"])
    if previous_claim_data is not None:
        repository.remove_item("claim-data", previous_claim_data["_id"])


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(download_doc, filters.Regexp(f"^{emojis.inbox_tray} получить"))
