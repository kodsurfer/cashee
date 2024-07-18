import aiohttp
import xml.etree.ElementTree as ET
import redis
import asyncio
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

async def fetch_currency_rates():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            xml_data = await response.text()
            return xml_data

def parse_xml(xml_data):
    root = ET.fromstring(xml_data)
    for valute in root.findall('Valute'):
        code = valute.find('CharCode').text
        rate = valute.find('Value').text.replace(',', '.')
        redis_client.set(code, rate)

async def update_rates():
    while True:
        xml_data = await fetch_currency_rates()
        parse_xml(xml_data)
        await asyncio.sleep(86400)  # 24 hours

if __name__ == "__main__":
    asyncio.run(update_rates())
