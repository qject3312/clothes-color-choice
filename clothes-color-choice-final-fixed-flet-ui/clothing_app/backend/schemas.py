from pydantic import BaseModel
from typing import Optional, List


class UserCreate(BaseModel):
    user_id: str
    password: str
    name: str
    gender: Optional[str] = "미입력"
    height: Optional[str] = "미입력"
    weight: Optional[str] = "미입력"
    body_type: Optional[str] = "미입력"
    skin_tone: Optional[str] = "미입력"
    personal_color: Optional[str] = "미입력"
    styles: Optional[List[str]] = ["미선택"]


class UserLogin(BaseModel):
    user_id: str
    password: str


class ClothingCreate(BaseModel):
    user_id: str = "guest"
    category: str
    detail: str
    feature: Optional[str] = ""
    color_name: str
    color_hex: str
    image_path: Optional[str] = ""


class OutfitEvaluateRequest(BaseModel):
    user_id: Optional[str] = "guest"
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


class ClothingUpdate(BaseModel):
    user_id: str = "guest"
    category: str
    detail: str
    feature: Optional[str] = ""
    color_name: str
    color_hex: str


class SavedOutfitCreate(BaseModel):
    user_id: str = "guest"
    outfit_data: dict
