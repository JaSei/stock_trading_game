from pydantic import BaseModel

class Player(BaseModel):
    name: str

    def __hash__(self) -> int:
        return hash(self.name)
