from app.schemas.favorite import FavoriteList, FavoriteRead


favorites_store: dict[str, set[str]] = {}


def add_favorite(user_id: str, property_id: str) -> FavoriteRead:
    raise NotImplementedError


def remove_favorite(user_id: str, property_id: str) -> None:
    raise NotImplementedError


def get_user_favorites(user_id: str, page: int, page_size: int) -> FavoriteList:
    raise NotImplementedError
