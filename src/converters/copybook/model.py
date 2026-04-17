# decorder.py - Data model for representing COBOL copybook fields and structures
from dataclasses import dataclass, field as dc_field
from typing import List, Optional

@dataclass
class Field:
    level: int
    name: str
    pic: Optional[str] = None
    length: int = 0
    occurs: int = 1
    redefines: Optional[str] = None
    usage: Optional[str] = None
    digits: int = 0
    scale: int = 0

    children: List["Field"] = dc_field(default_factory=list)
    offset: int = 0

    # ---------- TYPE FLAGS ----------
    @property
    def is_group(self) -> bool:
        return bool(self.children)

    @property
    def is_comp3(self) -> bool:
        return self.usage == "COMP-3"

    @property
    def is_comp(self) -> bool:
        return self.usage == "COMP"

    # ---------- LENGTH CALC ----------
    def total_length(self) -> int:
        if not self.children:
            return self.length * self.occurs

        child_total = sum(
            child.total_length()
            for child in self.children
            if not child.redefines
        )
        return child_total * self.occurs
