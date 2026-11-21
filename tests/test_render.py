"""渲染层测试：展开图 SVG 与练习纸 HTML。"""

import unittest

from nets.model import Cuboid, NetError, WorksheetItem, build_worksheet
from nets.render import net_svg, render_net_page, render_worksheet


class NetSvgTest(unittest.TestCase):
    def setUp(self):
        self.svg = net_svg(Cuboid(5, 4, 3))

    def test_svg_root(self):
        self.assertTrue(self.svg.startswith("<svg"))
        self.assertTrue(self.svg.endswith("</svg>"))

    def test_six_rectangles(self):
        self.assertEqual(self.svg.count("<rect"), 6)

    def test_all_labels(self):
        for label in ("前", "后", "左", "右", "上", "下"):
            self.assertIn(">%s</text>" % label, self.svg)

    def test_dimension_annotations(self):
        self.assertIn("5×4", self.svg)
        self.assertIn("3×4", self.svg)
        self.assertIn("5×3", self.svg)

    def test_aria_label(self):
        self.assertIn('aria-label="长方体的展开图"', self.svg)

    def test_cube_aria_label(self):
        self.assertIn('aria-label="正方体的展开图"', net_svg(Cuboid(2, 2, 2)))

    def test_default_scale(self):
        self.assertIn('width="128.00mm"', self.svg)
        self.assertIn('height="88.00mm"', self.svg)

    def test_custom_scale(self):
        svg = net_svg(Cuboid(5, 4, 3), 10.0)
        self.assertIn('width="160.00mm"', svg)
        self.assertIn('height="110.00mm"', svg)

    def test_rejects_zero_scale(self):
        with self.assertRaises(NetError):
            net_svg(Cuboid(5, 4, 3), 0)

    def test_rejects_negative_scale(self):
        with self.assertRaises(NetError):
            net_svg(Cuboid(5, 4, 3), -2)

    def test_rejects_bool_scale(self):
        with self.assertRaises(NetError):
            net_svg(Cuboid(5, 4, 3), True)

    def test_rejects_text_scale(self):
        with self.assertRaises(NetError):
            net_svg(Cuboid(5, 4, 3), "8")


class RenderNetPageTest(unittest.TestCase):
    def test_doctype(self):
        page = render_net_page(Cuboid(5, 4, 3))
        self.assertIn("<!DOCTYPE html>", page)

    def test_default_title(self):
        page = render_net_page(Cuboid(5, 4, 3))
        self.assertIn("<h1>长方体展开图</h1>", page)

    def test_cube_default_title(self):
        page = render_net_page(Cuboid(2, 2, 2))
        self.assertIn("<h1>正方体展开图</h1>", page)

    def test_custom_title(self):
        page = render_net_page(Cuboid(5, 4, 3), "数学课材料")
        self.assertIn("<h1>数学课材料</h1>", page)

    def test_title_is_escaped(self):
        page = render_net_page(Cuboid(5, 4, 3), "A<B>")
        self.assertIn("A&lt;B&gt;", page)
        self.assertNotIn("<h1>A<B></h1>", page)

    def test_contains_net_svg(self):
        page = render_net_page(Cuboid(5, 4, 3))
        self.assertEqual(page.count("<rect"), 6)

    def test_contains_measurements(self):
        page = render_net_page(Cuboid(5, 4, 3))
        self.assertIn("94 cm²", page)
        self.assertIn("60 cm³", page)
        self.assertIn("16 × 11 cm", page)

    def test_contains_dimension_table(self):
        page = render_net_page(Cuboid(5, 4, 3))
        self.assertIn("<th>长</th>", page)
        self.assertIn("<th>宽</th>", page)
        self.assertIn("<th>高</th>", page)

    def test_contains_fold_note(self):
        page = render_net_page(Cuboid(5, 4, 3))
        self.assertIn("沿实线裁剪", page)


class RenderWorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = build_worksheet(4, seed=11)

    def test_doctype(self):
        page = render_worksheet(self.items)
        self.assertIn("<!DOCTYPE html>", page)

    def test_item_count(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="item"'), 4)

    def test_numbering(self):
        page = render_worksheet(self.items)
        self.assertIn("1. ", page)
        self.assertIn("4. ", page)

    def test_default_title(self):
        page = render_worksheet(self.items)
        self.assertIn("<h1>长方体与正方体练习</h1>", page)

    def test_custom_title(self):
        page = render_worksheet(self.items, "几何小测")
        self.assertIn("<h1>几何小测</h1>", page)

    def test_title_escaped(self):
        page = render_worksheet(self.items, "A & B")
        self.assertIn("A &amp; B", page)

    def test_answers_absent(self):
        page = render_worksheet(self.items)
        self.assertNotIn("参考答案", page)

    def test_answers_present(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn("参考答案与展开图", page)

    def test_answer_count(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertEqual(page.count('class="item"'), 4)
        self.assertEqual(page.count("<rect"), 24)

    def test_answer_text_present(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn(self.items[0].answer_text, page)

    def test_empty_items(self):
        page = render_worksheet([])
        self.assertIn("暂无题目", page)

    def test_empty_items_with_answers(self):
        page = render_worksheet([], include_answers=True)
        self.assertIn("参考答案与展开图", page)

    def test_question_text_present(self):
        page = render_worksheet(self.items)
        self.assertIn(self.items[0].question, page)

    def test_answer_line(self):
        page = render_worksheet(self.items)
        self.assertIn("答：", page)

    def test_answers_start_new_page(self):
        page = render_worksheet(self.items, include_answers=True)
        self.assertIn('class="answers"', page)

    def test_items_are_single_kind(self):
        area_item = WorksheetItem(Cuboid(2, 2, 2), "area")
        page = render_worksheet([area_item], include_answers=True)
        self.assertIn("24 cm²", page)


if __name__ == "__main__":
    unittest.main()
