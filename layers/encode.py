from dataclasses import dataclass
from uuid import UUID, uuid1, uuid3, uuid4, uuid5

from bcrypt import checkpw, gensalt, hashpw


@dataclass()
class Encode:
    def __post_init__(self):
        self._uuid_dict: dict = self.get_uuid_dict()

    @staticmethod
    def get_uuid_dict() -> dict:
        return {"1": uuid1, "3": uuid3, "4": uuid4, "5": uuid5}

    @staticmethod
    def get_salt(rounds: int = 6) -> bytes:
        return gensalt(rounds=rounds)

    @staticmethod
    def get_hash(string_encoded: bytes, salt: bytes = gensalt(rounds=6)) -> bytes:
        return hashpw(string_encoded, salt)

    def get_id(
        self, version: str = "4", namespace: UUID = uuid4(), name: str = ""
    ) -> str:
        if version in ["3", "5"]:
            return str(self.get_uuid_dict()[version](namespace, name))
        return str(self.get_uuid_dict()[version]())

    @staticmethod
    def encode_string(string: str, encoding: str = "utf-8") -> bytes:
        return string.encode(encoding=encoding)

    @staticmethod
    def check_password(password: bytes, password_to_comparison: bytes) -> bool:
        return checkpw(password, password_to_comparison)
