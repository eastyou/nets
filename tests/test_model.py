"""模型层测试：尺寸校验、展开图布局、题目生成与答案解析。"""

import unittest

from nets.model import (
    FACE_LABELS,
    Cuboid,
    NetError,
    WorksheetItem,
    build_net,
    build_worksheet,
    check_answer,
    check_dimension,
    format_number,
    parse_measurement,
)


class CheckDimensionTest(unittest.TestCase):
    def test_accepts_int(self):
        self.assertEqual(check_dimension(6), 6.0)

    def test_accepts_float(self):
        self.assertAlmostEqual(check_dimension(2.5), 2.5)

    def test_returns_float(self):
        self.assertIsInstance(check_dimension(3), float)

    def test_rejects_zero(self):
        with self.assertRaises(NetError):
            check_dimension(0)

    def test_rejects_negative(self):
        with self.assertRaises(NetError):
            check_dimension(-4)

    def test_rejects_bool(self):
        with self.assertRaises(NetError):
            check_dimension(True)

    def test_rejects_string(self):
        with self.assertRaises(NetError):
            check_dimension("5")

    def test_rejects_none(self):
        with self.assertRaises(NetError):
            check_dimension(None)

    def test_rejects_nan(self):
        with self.assertRaises(NetError):
            check_dimension(float("nan"))

    def test_rejects_infinity(self):
        with self.assertRaises(NetError):
            check_dimension(float("inf"))

    def test_rejects_too_large(self):
        with self.assertRaises(NetError):
            check_dimension(101)


class CuboidTest(unittest.TestCase):
    def setUp(self):
        self.shape = Cuboid(5, 4, 3)

    def test_surface_area(self):
        self.assertAlmostEqual(self.shape.surface_area, 94.0)

    def test_volume(self):
        self.assertAlmostEqual(self.shape.volume, 60.0)

    def test_is_not_cube(self):
        self.assertFalse(self.shape.is_cube)

    def test_name_cuboid(self):
        self.assertEqual(self.shape.name, "长方体")

    def test_cube_surface_area(self):
        cube = Cuboid(3, 3, 3)
        self.assertAlmostEqual(cube.surface_area, 54.0)

    def test_cube_volume(self):
        cube = Cuboid(3, 3, 3)
        self.assertAlmostEqual(cube.volume, 27.0)

    def test_is_cube(self):
        self.assertTrue(Cuboid(2, 2, 2).is_cube)

    def test_cube_name(self):
        self.assertEqual(Cuboid(2, 2, 2).name, "正方体")

    def test_dimensions_text(self):
        self.assertEqual(self.shape.dimensions_text, "长 5 cm、宽 3 cm、高 4 cm")

    def test_dimensions_text_decimal(self):
        shape = Cuboid(2.5, 1.5, 3)
        self.assertEqual(shape.dimensions_text, "长 2.5 cm、宽 3 cm、高 1.5 cm")

    def test_invalid_dimension_raises(self):
        with self.assertRaises(NetError):
            Cuboid(0, 2, 3)

    def test_invalid_depth_raises(self):
        with self.assertRaises(NetError):
            Cuboid(2, 3, -1)

    def test_frozen(self):
        with self.assertRaises(AttributeError):
            self.shape.width = 9  # type: ignore[misc]


class NetLayoutTest(unittest.TestCase):
    def setUp(self):
        self.shape = Cuboid(5, 4, 3)
        self.net = build_net(self.shape)

    def test_six_faces(self):
        self.assertEqual(len(self.net.faces), 6)

    def test_face_labels(self):
        self.assertEqual(tuple(face.label for face in self.net.faces), FACE_LABELS)

    def test_total_area_matches_surface(self):
        self.assertAlmostEqual(self.net.total_area, self.shape.surface_area)

    def test_net_width(self):
        self.assertAlmostEqual(self.net.width, 16.0)

    def test_net_height(self):
        self.assertAlmostEqual(self.net.height, 11.0)

    def _face(self, label):
        for face in self.net.faces:
            if face.label == label:
                return face
        raise AssertionError("缺少面：%s" % label)

    def test_front_position(self):
        face = self._face("前")
        self.assertEqual((face.x, face.y, face.width, face.height), (0.0, 4.0, 5.0, 4.0))

    def test_right_position(self):
        face = self._face("右")
        self.assertEqual((face.x, face.y, face.width, face.height), (5.0, 4.0, 3.0, 4.0))

    def test_back_position(self):
        face = self._face("后")
        self.assertEqual((face.x, face.y, face.width, face.height), (8.0, 4.0, 5.0, 4.0))

    def test_left_position(self):
        face = self._face("左")
        self.assertEqual((face.x, face.y, face.width, face.height), (13.0, 4.0, 3.0, 4.0))

    def test_top_position(self):
        face = self._face("上")
        self.assertEqual((face.x, face.y, face.width, face.height), (5.0, 0.0, 5.0, 3.0))

    def test_bottom_position(self):
        face = self._face("下")
        self.assertEqual((face.x, face.y, face.width, face.height), (5.0, 8.0, 5.0, 3.0))

    def test_face_areas(self):
        areas = sorted(face.area for face in self.net.faces)
        self.assertEqual(areas, [12.0, 12.0, 15.0, 15.0, 20.0, 20.0])

    def test_faces_fit_inside_net(self):
        for face in self.net.faces:
            self.assertGreaterEqual(face.x, 0)
            self.assertGreaterEqual(face.y, 0)
            self.assertLessEqual(face.x + face.width, self.net.width)
            self.assertLessEqual(face.y + face.height, self.net.height)

    def test_cube_net_square(self):
        net = build_net(Cuboid(2, 2, 2))
        self.assertAlmostEqual(net.width, 8.0)
        self.assertAlmostEqual(net.height, 6.0)


class WorksheetItemTest(unittest.TestCase):
    def test_rejects_unknown_kind(self):
        with self.assertRaises(NetError):
            WorksheetItem(Cuboid(2, 2, 2), "perimeter")

    def test_area_answer(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "area")
        self.assertAlmostEqual(item.answer, 94.0)

    def test_volume_answer(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "volume")
        self.assertAlmostEqual(item.answer, 60.0)

    def test_area_unit(self):
        self.assertEqual(WorksheetItem(Cuboid(2, 3, 4), "area").unit, "cm²")

    def test_volume_unit(self):
        self.assertEqual(WorksheetItem(Cuboid(2, 3, 4), "volume").unit, "cm³")

    def test_area_answer_text(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "area")
        self.assertEqual(item.answer_text, "94 cm²")

    def test_volume_answer_text(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "volume")
        self.assertEqual(item.answer_text, "60 cm³")

    def test_area_question(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "area")
        self.assertEqual(item.question, "长 5 cm、宽 3 cm、高 4 cm，它的表面积是多少？")

    def test_volume_question(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "volume")
        self.assertIn("体积", item.question)

    def test_cube_item(self):
        item = WorksheetItem(Cuboid(2, 2, 2), "area")
        self.assertEqual(item.answer_text, "24 cm²")


class FormatNumberTest(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(format_number(60.0), "60")

    def test_integer_value(self):
        self.assertEqual(format_number(7), "7")

    def test_half(self):
        self.assertEqual(format_number(2.5), "2.5")

    def test_trailing_zero(self):
        self.assertEqual(format_number(2.50), "2.5")

    def test_rounding(self):
        self.assertEqual(format_number(2.345), "2.35")

    def test_negative(self):
        self.assertEqual(format_number(-3.5), "-3.5")

    def test_near_integer(self):
        self.assertEqual(format_number(3.0000000001), "3")

    def test_rejects_bool(self):
        with self.assertRaises(NetError):
            format_number(True)

    def test_rejects_string(self):
        with self.assertRaises(NetError):
            format_number("12")


class BuildWorksheetTest(unittest.TestCase):
    def test_count(self):
        items = build_worksheet(12, seed=1)
        self.assertEqual(len(items), 12)

    def test_deterministic(self):
        first = build_worksheet(15, seed=42)
        second = build_worksheet(15, seed=42)
        self.assertEqual(first, second)

    def test_unique(self):
        items = build_worksheet(20, seed=7)
        keys = {(item.shape.width, item.shape.height, item.shape.depth, item.kind) for item in items}
        self.assertEqual(len(keys), len(items))

    def test_kinds_allowed(self):
        for item in build_worksheet(10, seed=3):
            self.assertIn(item.kind, ("area", "volume"))

    def test_default_range(self):
        for item in build_worksheet(10, seed=5):
            for value in (item.shape.width, item.shape.height, item.shape.depth):
                self.assertGreaterEqual(value, 2)
                self.assertLessEqual(value, 8)

    def test_custom_range(self):
        for item in build_worksheet(6, seed=5, low=10, high=12):
            for value in (item.shape.width, item.shape.height, item.shape.depth):
                self.assertGreaterEqual(value, 10)
                self.assertLessEqual(value, 12)

    def test_rejects_zero_count(self):
        with self.assertRaises(NetError):
            build_worksheet(0)

    def test_rejects_negative_count(self):
        with self.assertRaises(NetError):
            build_worksheet(-2)

    def test_rejects_bool_count(self):
        with self.assertRaises(NetError):
            build_worksheet(True)

    def test_rejects_float_count(self):
        with self.assertRaises(NetError):
            build_worksheet(2.5)

    def test_rejects_low_below_one(self):
        with self.assertRaises(NetError):
            build_worksheet(2, low=0)

    def test_rejects_reversed_range(self):
        with self.assertRaises(NetError):
            build_worksheet(2, low=8, high=3)

    def test_rejects_non_int_low(self):
        with self.assertRaises(NetError):
            build_worksheet(2, low=2.5)

    def test_rejects_bool_high(self):
        with self.assertRaises(NetError):
            build_worksheet(2, high=True)

    def test_rejects_oversized_request(self):
        with self.assertRaises(NetError):
            build_worksheet(3, low=2, high=2)

    def test_smallest_range(self):
        items = build_worksheet(2, low=2, high=2, seed=1)
        self.assertEqual(len(items), 2)
        self.assertEqual({item.kind for item in items}, {"area", "volume"})

    def test_answers_are_positive(self):
        for item in build_worksheet(10, seed=9):
            self.assertGreater(item.answer, 0)


class ParseMeasurementTest(unittest.TestCase):
    def test_plain_number(self):
        self.assertAlmostEqual(parse_measurement("94"), 94.0)

    def test_with_unit(self):
        self.assertAlmostEqual(parse_measurement("94 cm²"), 94.0)

    def test_decimal(self):
        self.assertAlmostEqual(parse_measurement("2.5"), 2.5)

    def test_surrounding_space(self):
        self.assertAlmostEqual(parse_measurement("  60  "), 60.0)

    def test_rejects_empty(self):
        with self.assertRaises(NetError):
            parse_measurement("")

    def test_rejects_spaces(self):
        with self.assertRaises(NetError):
            parse_measurement("   ")

    def test_rejects_none(self):
        with self.assertRaises(NetError):
            parse_measurement(None)

    def test_rejects_text(self):
        with self.assertRaises(NetError):
            parse_measurement("abc")

    def test_rejects_zero(self):
        with self.assertRaises(NetError):
            parse_measurement("0")

    def test_rejects_negative(self):
        with self.assertRaises(NetError):
            parse_measurement("-3")


class CheckAnswerTest(unittest.TestCase):
    def setUp(self):
        self.item = WorksheetItem(Cuboid(5, 4, 3), "area")

    def test_correct(self):
        self.assertTrue(check_answer(self.item, "94"))

    def test_correct_with_unit(self):
        self.assertTrue(check_answer(self.item, "94 cm²"))

    def test_wrong(self):
        self.assertFalse(check_answer(self.item, "93"))

    def test_invalid(self):
        self.assertFalse(check_answer(self.item, "不知道"))

    def test_empty(self):
        self.assertFalse(check_answer(self.item, ""))

    def test_within_tolerance(self):
        self.assertTrue(check_answer(self.item, "94.0000001"))

    def test_outside_tolerance(self):
        self.assertFalse(check_answer(self.item, "94.1"))

    def test_custom_tolerance(self):
        self.assertTrue(check_answer(self.item, "94.1", tolerance=1e-2))

    def test_volume_item(self):
        item = WorksheetItem(Cuboid(5, 4, 3), "volume")
        self.assertTrue(check_answer(item, "60"))


class ModuleConstantsTest(unittest.TestCase):
    def test_face_labels_count(self):
        self.assertEqual(len(FACE_LABELS), 6)

    def test_face_labels_unique(self):
        self.assertEqual(len(set(FACE_LABELS)), 6)


if __name__ == "__main__":
    unittest.main()
