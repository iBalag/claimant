import logging
from collections import namedtuple
from io import StringIO
from typing import List
from urllib.parse import quote_plus

from aiohttp import ClientSession, ClientTimeout
from lxml import etree
from lxml.html import HtmlElement


CourtInfo = namedtuple("CourtAddress", ["name", "address", "note"])


def to_url(param: str) -> str:
    return quote_plus(param.lower().encode("cp1251"))


def parse_address(raw_data: List[str], city: str) -> List[str]:
    result: List[str] = []
    for row in raw_data:
        if city.lower() in row.lower():
            result.append(row)
    return result


def parse_court_data(raw_data: str, city: str) -> List[CourtInfo]:
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(raw_data), parser)

    names: List[HtmlElement] = tree.xpath("//table[@class='msSearchResultTbl msFullSearchResultTbl']/tr/td/a")
    names = [n.text for n in names]

    raw_addresses: List[str] = tree.xpath("//table[@class='msSearchResultTbl msFullSearchResultTbl']/tr/td/"
                                          "div[@class='courtInfoCont']/text()")
    addresses = parse_address(raw_addresses, city)

    notes: List[HtmlElement] = tree.xpath("//table[@class='msSearchResultTbl msFullSearchResultTbl']/"
                                          "tr[not(@class='firstRow')]/td[last()]")
    notes = [ai.text for ai in notes]

    result: List[CourtInfo] = []
    for name, address, note in zip(names, addresses, notes):
        result.append(CourtInfo(name, address, note))
    return result


async def resolve_court_address(city: str, court_subj: str, street: str) -> List[CourtInfo]:
    url: str = f"https://sudrf.ru/index.php?id=300&&act=go_search&searchtype=fs&court_type=RS&" \
               f"fs_city={to_url(city)}" \
               f"&fs_street={to_url(street)}" \
               f"&court_subj={court_subj}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/94.0.4606.81 Safari/537.36"
    }

    try:
        async with ClientSession() as session:
            # For better user experience setup request timeout to 15 seconds
            timeout = ClientTimeout(total=15)
            async with session.get(url, headers=headers, ssl=False, timeout=timeout) as resp:
                body: str = await resp.text()
                result = parse_court_data(body, city)
                return result
    except Exception:
        logger = logging.getLogger()
        logger.exception("Error occurred during court address resolving")
        return []
