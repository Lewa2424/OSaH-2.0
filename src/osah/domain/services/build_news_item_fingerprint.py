import hashlib


# ###### ПОБУДОВА ВІДБИТКА НОВИННОГО МАТЕРІАЛУ / ПОСТРОЕНИЕ ОТПЕЧАТКА НОВОСТНОГО МАТЕРИАЛА ######
def build_news_item_fingerprint(title_text: str, link_url: str) -> str:
    """Будує стабільний відбиток матеріалу для дедуплікації.
    Строит стабильный отпечаток материала для дедупликации.
    """

    return hashlib.sha256(f"{title_text.strip()}|{link_url.strip()}".encode("utf-8")).hexdigest()
