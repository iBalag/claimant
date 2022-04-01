import requests
import xml.etree.ElementTree as ET


def get_key_rate() -> float:
    endpoint = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <MainInfoXML xmlns="http://web.cbr.ru/" />
  </soap:Body>
</soap:Envelope>
"""

    body = body.encode("utf-8")
    session = requests.session()
    session.headers = {"Content-Type": "text/xml", "Content-Length": str(len(body))}
    response = session.post(url=endpoint, data=body, verify=False)
    if response.status_code != 200:
        # TODO: make sense to get it from cache?
        return -1

    main_info_xml_raw: str = response.content.decode()
    root = ET.fromstring(main_info_xml_raw)
    key_rate = root.findall(".//keyRate")
    if key_rate is not None and len(key_rate) == 1:
        return float(key_rate[0].text)
    else:
        return -1
