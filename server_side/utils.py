from json import dumps, loads


class Request:
    def __new__(cls, payload: bytes) -> dict:
        return loads(payload.decode(encoding="utf-8"))


class Response:
    def __new__(cls, payload) -> bytes:
        return dumps(payload).encode(encoding="utf-8")
