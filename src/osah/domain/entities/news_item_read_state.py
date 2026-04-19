from enum import StrEnum


class NewsItemReadState(StrEnum):
    """Стани прочитання кешованого матеріалу.
    Состояния прочтения кэшированного материала.
    """

    NEW = "new"
    READ = "read"
