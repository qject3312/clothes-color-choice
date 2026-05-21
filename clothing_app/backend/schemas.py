from pydantic import BaseModel
from typing import Optional

class ClothingCreate(BaseModel):
    category: str
    detail: str
    feature: Optional[str] = ""
    color_name: str
    color_hex: str
    image_path: Optional[str] = ""

class OutfitEvaluateRequest(BaseModel):
    top_color: str
    top_type: str
    bottom_color: str
    bottom_type: str
    outer_color: Optional[str] = ""
    outer_type: Optional[str] = ""
    shoes_color: Optional[str] = ""
    shoes_type: Optional[str] = ""
    season: Optional[str] = ""
    style_mood: Optional[str] = ""