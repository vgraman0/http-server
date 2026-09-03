from enum import Enum


class Status(Enum):
    OK = 200, "OK"
    NOT_FOUND = 404, "Not Found"

    @property
    def code(self):
        return self.value[0]

    @property
    def text(self):
        return self.value[1]

    def __str__(self) -> str:
        return f"{self.code} {self.text}"
