from dataclasses import dataclass
from datetime import datetime

from jwt import decode, encode

try:
    from date import Date
    from encode import Encode
except ImportError:
    from layers.date import Date
    from layers.encode import Encode


@dataclass()
class Auth:
    _date: Date = Date()
    _encode: Encode = Encode()

    def get_payload_to_jwt(
        self, aud: str, ref: str = None, exp: datetime = None, seconds: int = 84600
    ) -> dict:
        return {
            "aud": aud,
            "iss": self.__class__.__name__,
            "ref": ref if ref else self._encode.get_id(),
            "exp": exp if exp else self._date.add_date(seconds=seconds),
        }

    @staticmethod
    def generate_access_token(
        payload: dict, secret: str, algorithm: str = "HS256"
    ) -> bytes:
        return encode(payload=payload, key=secret, algorithm=algorithm)

    @staticmethod
    def __get_schema_to_jwt_encode() -> dict:
        return {
            "type": "object",
            "properties": {
                "aud": {"type": "string"},
                "iss": {"type": "string"},
            },
            "required": ["aud", "iss"],
        }

    @staticmethod
    def decode_jwt(token: str, key: str) -> dict:
        data = decode(token, key)
        return data
