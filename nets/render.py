"""展开图 SVG 与练习纸渲染。"""

from __future__ import annotations

import html
from typing import Sequence

from .model import Cuboid, NetError, WorksheetItem, build_net, format_number

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1b2430;
  font-size: 11pt;
  line-height: 1.5;
}
h1 { font-size: 20pt; margin: 0 0 2mm; }
.sub { color: #6b7280; font-size: 10pt; margin: 0 0 5mm; }
ol.items { margin: 0; padding-left: 7mm; }
li.item { margin-bottom: 5.5mm; page-break-inside: avoid; }
.q { font-size: 11.5pt; margin-bottom: 1mm; }
.blank { display: inline-block; min-width: 30mm; border-bottom: 0.8pt solid #1b2430; height: 1.1em; }
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers li { margin-bottom: 6mm; page-break-inside: avoid; }
.answers .ans { font-family: "SFMono-Regular", Consolas, monospace; color: #0f4c81; }
svg { display: block; margin: 1mm auto; }
.note { color: #6b7280; font-size: 9.5pt; }
table.info { border-collapse: collapse; margin-top: 3mm; font-size: 10pt; }
table.info th, table.info td { border: 0.4pt solid #d7dee6; padding: 1.6mm 3mm; text-align: left; }
table.info th { background: #f1f5f9; }
.face-label { font-size: 3.4px; }
@media print { li.item, .answers li { break-inside: avoid; } }
"""

_COLORS = {
    "前": "#eff6ff",
    "后": "#f0fdf4",
    "左": "#fef9c3",
    "右": "#fce7f3",
    "上": "#e0f2fe",
    "下": "#fef3c7",
}


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def net_svg(shape: Cuboid, mm_per_cm: float = 8.0) -> str:
    """把展开图画成 SVG，单位毫米。"""
    if isinstance(mm_per_cm, bool) or not isinstance(mm_per_cm, (int, float)):
        raise NetError("比例必须是数字")
    if mm_per_cm <= 0:
        raise NetError("比例必须大于 0")
    net = build_net(shape)
    width_mm = net.width * mm_per_cm
    height_mm = net.height * mm_per_cm
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" '
        'viewBox="0 0 %.2f %.2f" role="img" aria-label="%s的展开图">'
        % (width_mm, height_mm, width_mm, height_mm, _escape(shape.name))
    ]
    for face in net.faces:
        x = face.x * mm_per_cm
        y = face.y * mm_per_cm
        w = face.width * mm_per_cm
        h = face.height * mm_per_cm
        parts.append(
            '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" '
            'stroke="#1f2933" stroke-width="0.5"/>'
            % (x, y, w, h, _COLORS.get(face.label, "#ffffff"))
        )
        parts.append(
            '<text x="%.2f" y="%.2f" text-anchor="middle" font-size="4" fill="#1f2933">%s</text>'
            % (x + w / 2.0, y + h / 2.0 - 1.0, _escape(face.label))
        )
        parts.append(
            '<text x="%.2f" y="%.2f" text-anchor="middle" font-size="3.2" fill="#52606d">%s×%s</text>'
            % (x + w / 2.0, y + h / 2.0 + 4.0, format_number(face.width), format_number(face.height))
        )
    parts.append("</svg>")
    return "".join(parts)


def render_net_page(shape: Cuboid, title: str = "", mm_per_cm: float = 8.0) -> str:
    """单张展开图制作页。"""
    heading = title or "%s展开图" % shape.name
    net = build_net(shape)
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % _escape(heading),
            "<style>%s</style>" % STYLE,
            "</head>",
            "<body>",
            "<h1>%s</h1>" % _escape(heading),
            '<p class="sub">沿实线裁剪，沿相邻边折叠，就能拼成一个%s。</p>' % _escape(shape.name),
            net_svg(shape, mm_per_cm),
            '<table class="info">'
            "<tr><th>长</th><td>%s cm</td><th>宽</th><td>%s cm</td><th>高</th><td>%s cm</td></tr>"
            "<tr><th>表面积</th><td>%s cm²</td><th>体积</th><td>%s cm³</td>"
            "<th>展开图尺寸</th><td>%s × %s cm</td></tr>"
            "</table>"
            % (
                format_number(shape.width),
                format_number(shape.depth),
                format_number(shape.height),
                format_number(shape.surface_area),
                format_number(shape.volume),
                format_number(net.width),
                format_number(net.height),
            ),
            '<p class="note">展开图中每个面上标注了该面的两条边长，可用来核对裁剪尺寸。</p>',
            "</body>",
            "</html>",
        ]
    )


def render_worksheet(
    items: Sequence[WorksheetItem],
    title: str = "长方体与正方体练习",
    include_answers: bool = False,
) -> str:
    """生成计算练习纸；答案页附展开图。"""
    safe_title = _escape(title)
    blocks = []
    for index, item in enumerate(items, start=1):
        blocks.append(
            '<li class="item"><div class="q">%d. %s</div>'
            '<div>答：<span class="blank"></span></div></li>'
            % (index, _escape(item.question))
        )
    body = "".join(blocks) or '<p class="note">暂无题目。</p>'
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % safe_title,
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % safe_title,
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<ol class="items">%s</ol>' % body,
    ]
    if include_answers:
        answers = []
        for index, item in enumerate(items, start=1):
            answers.append(
                "<li><div>%d. <span class=\"ans\">%s</span></div>%s</li>"
                % (index, _escape(item.answer_text), net_svg(item.shape, 5.0))
            )
        parts.extend(
            [
                '<section class="answers">',
                "<h2>参考答案与展开图</h2>",
                "<ol>%s</ol>" % "".join(answers),
                "</section>",
            ]
        )
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)
