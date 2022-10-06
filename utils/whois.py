import aiohttp

from .exceptions import WHOISError


WHOIS_URL = 'http://ip-api.com/json/'
WHOIS_FIELDS = '?fields=status,message,continent,country,city,isp,org,query'
WHOIS_URL_UNAVAILABLE = 'Адрес {url} недоступен'
WHOIS_QUERY_FAIL = (
    'Запрашиваемый домен {query}, полученный статус: {status}, '
    'диагностическое сообщение: {message}')
WHOIS_RESULT = (
    'IP: {ip}\n\nКонтинент: {continent}\nСтрана: {country}\nГород: {city}\n\n'
    'Провайдер: {isp}\nОрганизация: {organization}')


async def get_whois(domain: str) -> dict[str, str]:
    """
    Makes get request to get WHOIS information of given website.
    """
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(
                url=WHOIS_URL + domain + WHOIS_FIELDS
            )
        except aiohttp.ClientConnectionError:
            raise WHOISError(WHOIS_URL_UNAVAILABLE.format(url=WHOIS_URL))
    return await response.json()


async def parse_whois(domain: str) -> str:
    """
    Get domain and returns string with WHOIS data of website.
    """
    result = await get_whois(domain)
    if not result.get('status') == 'success':
        raise WHOISError(WHOIS_QUERY_FAIL.format(
            query=result.get('query'),
            status=result.get('status'),
            message=result.get('message')))
    return WHOIS_RESULT.format(
        ip=result.get('query'),
        continent=result.get('continent'),
        country=result.get('country'),
        city=result.get('city'),
        isp=result.get('isp'),
        organization=result.get('org')
    )
