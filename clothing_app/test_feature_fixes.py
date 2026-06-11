import unittest
from pathlib import Path

import flet as ft

from app_paths import resolve_existing_path
from logic.photo_analysis import infer_clothing_type
from logic.recommend_logic import extract_dominant_colors, recommend_outfits
from model.clothing import Clothing
import views.clothes_view as clothes_view
import views.recommend_view as recommend_view
from views.components import btn_primary
from views.recommend_view import (
    build_coordination,
    build_personal_recommend,
    build_recommend,
    build_today,
)
from views.register_view import build_register_photo


class FakePage:
    def __init__(self):
        self.overlay = []

    def update(self):
        pass

    def open(self, _control):
        pass

    def close(self, _control):
        pass


def walk_controls(control):
    if control is None:
        return
    yield control
    for attribute in ("content", "controls", "actions"):
        value = getattr(control, attribute, None)
        if isinstance(value, list):
            for child in value:
                yield from walk_controls(child)
        elif value is not None:
            yield from walk_controls(value)


def button_with_text(root, text):
    for control in walk_controls(root):
        if not isinstance(control, ft.ElevatedButton):
            continue
        values = [
            child.value
            for child in walk_controls(control)
            if isinstance(child, ft.Text)
        ]
        if any(text in value for value in values):
            return control
    raise AssertionError(f"button not found: {text}")


def clickable_with_text(root, text):
    for control in walk_controls(root):
        if not callable(getattr(control, "on_click", None)):
            continue
        values = [
            child.value
            for child in walk_controls(control)
            if isinstance(child, ft.Text)
        ]
        if text in values:
            return control
    raise AssertionError(f"clickable control not found: {text}")


class FeatureFixTests(unittest.TestCase):
    def test_primary_button_uses_full_card_width_by_default(self):
        full_width = btn_primary("전체 폭", lambda _event: None)
        compact = btn_primary("작은 버튼", lambda _event: None, expand=False)
        self.assertEqual(full_width.width, 9999)
        self.assertIsNone(compact.width)

    def test_korean_filename_inference(self):
        self.assertEqual(infer_clothing_type("\uccad\ubc14\uc9c0_01.jpg")["detail"], "\uccad\ubc14\uc9c0")
        self.assertEqual(infer_clothing_type("\ubc18\ud314.png")["detail"], "\ubc18\ud314")
        self.assertEqual(infer_clothing_type("\uac00\ubc29.jpeg")["detail"], "\uac00\ubc29")

    def test_jeans_photo_inference_and_color(self):
        path = Path("app_data/images/moon1234_1780675274348.jpg")
        guess = infer_clothing_type(str(path))
        self.assertEqual(guess["category"], "\ud558\uc758")
        self.assertEqual(guess["detail"], "\uccad\ubc14\uc9c0")
        colors = extract_dominant_colors(str(path), 3)
        self.assertTrue(colors)
        self.assertEqual(colors[0][0], "\ud30c\ub791")

    def test_windows_image_path_recovers_by_filename(self):
        resolved = resolve_existing_path(r"C:\old\machine\guest_1780638168866.png")
        self.assertTrue(Path(resolved).exists())

    def test_edit_and_photo_views_build(self):
        page = FakePage()
        cloth = Clothing(
            category="\uc0c1\uc758",
            detail="\ubc18\ud314",
            feature="\uae30\ubcf8",
            rgb=(255, 0, 0),
            hex_code="#ff0000",
            color_name="\ube68\uac15",
            clothing_id=1,
        )
        state = {"user": {"user_id": "tester"}, "clothes": [cloth], "edit_cloth": cloth}
        self.assertIsNotNone(clothes_view.build_clothes_edit(page, lambda _route: None, state))
        self.assertIsNotNone(build_register_photo(page, lambda _route: None, state))
        self.assertTrue(page.overlay)

    def test_wardrobe_edit_uses_app_state_and_real_user(self):
        page = FakePage()
        routes = []
        cloth = Clothing(
            category="\uc0c1\uc758",
            detail="\ubc18\ud314",
            feature="\uae30\ubcf8",
            rgb=(255, 0, 0),
            hex_code="#ff0000",
            color_name="\ube68\uac15",
            clothing_id=7,
        )
        state = {"user": {"user_id": "real-user"}, "clothes": [cloth]}
        wardrobe = clothes_view.build_clothes(page, routes.append, state)
        edit_button = next(
            control
            for control in walk_controls(wardrobe)
            if isinstance(control, ft.IconButton) and control.icon == ft.Icons.EDIT_OUTLINED
        )
        edit_button.on_click(None)
        self.assertIs(state["edit_cloth"], cloth)
        self.assertEqual(routes[-1], "/clothes_edit")

        called = {}
        original = clothes_view.update_clothing_backend
        clothes_view.update_clothing_backend = (
            lambda clothing_id, _item, user_id: called.update(id=clothing_id, user_id=user_id) or {"message": "ok"}
        )
        try:
            editor = clothes_view.build_clothes_edit(page, routes.append, state)
            button_with_text(editor, "\uc218\uc815 \uc800\uc7a5").on_click(None)
        finally:
            clothes_view.update_clothing_backend = original
        self.assertEqual(called, {"id": 7, "user_id": "real-user"})

    def test_recommend_again_advances_both_screens(self):
        page = FakePage()
        routes = []
        clothes = [
            Clothing("\uc0c1\uc758", "\ubc18\ud314", "\uce90\uc8fc\uc5bc", (255, 0, 0), "#ff0000", "\ube68\uac15", clothing_id=1),
            Clothing("\uc0c1\uc758", "\uc154\uce20", "\ubbf8\ub2c8\uba40", (255, 255, 255), "#ffffff", "\ud770\uc0c9", clothing_id=2),
            Clothing("\ud558\uc758", "\uccad\ubc14\uc9c0", "\uce90\uc8fc\uc5bc", (0, 0, 255), "#0000ff", "\ud30c\ub791", clothing_id=3),
            Clothing("\ud558\uc758", "\uc2ac\ub799\uc2a4", "\ubbf8\ub2c8\uba40", (0, 0, 0), "#000000", "\uac80\uc815", clothing_id=4),
        ]
        state = {
            "user": {
                "user_id": "tester",
                "name": "Tester",
                "styles": ["\uce90\uc8fc\uc5bc"],
                "body_type": "\ubcf4\ud1b5 \uccb4\ud615",
                "skin_tone": "\ubc1d\uc740 \ud53c\ubd80\ud1a4",
                "personal_color": "\ubd04 \uc6dc",
            },
            "clothes": clothes,
        }
        personal = build_personal_recommend(page, routes.append, state)
        self.assertEqual(button_with_text(personal, "다른 옷").width, 9999)
        self.assertEqual(button_with_text(personal, "이 코디 저장하기").width, 9999)
        button_with_text(personal, "\ub2e4\ub978 \uc637").on_click(None)
        today = build_today(page, routes.append, state)
        self.assertEqual(button_with_text(today, "다른 옷").width, 9999)
        self.assertEqual(button_with_text(today, "이 코디 저장하기").width, 9999)
        button_with_text(today, "\ub2e4\ub978 \uc637").on_click(None)
        self.assertEqual(state["_personal_recommend_round"], 1)
        self.assertEqual(state["_today_recommend_round"], 1)
        self.assertEqual(routes[-2:], ["/personal", "/today"])

    def test_custom_recommend_again_rotates_results(self):
        page = FakePage()
        clothes = [
            Clothing("상의", "반팔", "캐주얼", (255, 0, 0), "#ff0000", "빨강", clothing_id=1),
            Clothing("상의", "셔츠", "미니멀", (255, 255, 255), "#ffffff", "흰색", clothing_id=2),
            Clothing("하의", "청바지", "캐주얼", (0, 0, 255), "#0000ff", "파랑", clothing_id=3),
            Clothing("하의", "슬랙스", "미니멀", (0, 0, 0), "#000000", "검정", clothing_id=4),
        ]
        state = {"user": {"user_id": "tester"}, "clothes": clothes}
        first = recommend_outfits(state["user"], clothes, top_n=3, offset=0)
        second = recommend_outfits(state["user"], clothes, top_n=3, offset=3)
        self.assertNotEqual(first[0]["outfit"], second[0]["outfit"])

        screen = build_recommend(page, lambda _route: None, state)
        button_with_text(screen, "다시 추천").on_click(None)
        self.assertEqual(state["_recommend_round"], 1)

    def test_coordination_allows_multiple_accessories_and_saves_them(self):
        page = FakePage()
        clothes = [
            Clothing("상의", "반팔", "기본", (255, 255, 255), "#ffffff", "흰색", clothing_id=1),
            Clothing("하의", "청바지", "기본", (0, 0, 255), "#0000ff", "파랑", clothing_id=2),
            Clothing("악세서리", "가방", "기본", (0, 0, 0), "#000000", "검정", clothing_id=3),
            Clothing("악세서리", "모자", "기본", (255, 0, 0), "#ff0000", "빨강", clothing_id=4),
        ]
        state = {"user": {"user_id": "tester"}, "clothes": clothes}
        original = recommend_view.save_outfit_backend
        recommend_view.save_outfit_backend = lambda _outfit, _uid: {"id": 10}
        try:
            screen = build_coordination(page, lambda _route: None, state)
            for detail in ["반팔", "청바지", "가방", "모자"]:
                clickable_with_text(screen, detail).on_click(None)
            self.assertEqual(button_with_text(screen, "선택 완료 및 저장").width, 9999)
            self.assertEqual(button_with_text(screen, "나의 코디 확인").width, 9999)
            button_with_text(screen, "선택 완료 및 저장").on_click(None)
        finally:
            recommend_view.save_outfit_backend = original

        saved = state["saved_outfits"][0]
        self.assertEqual([item["detail"] for item in saved["accessories"]], ["가방", "모자"])
        self.assertEqual(saved["accessory"]["detail"], "가방")


if __name__ == "__main__":
    unittest.main()
