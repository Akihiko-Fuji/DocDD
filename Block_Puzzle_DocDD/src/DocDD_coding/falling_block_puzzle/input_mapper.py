"""Input mapper based on DOC-SPC-022."""

KEY_BINDINGS = {
    "left": "left",
    "right": "right",
    "down": "down",
    "a": "a",
    "b": "b",
    "start": "start",
    "select": "select",
    "back": "back",
}


def map_pressed(keys: dict[str, bool]) -> set[str]:
    """物理入力状態(dict)から論理入力セットへ変換する。"""
    return {KEY_BINDINGS[k] for k, v in keys.items() if v and k in KEY_BINDINGS}
