"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import Cuboid, NetError, build_worksheet, build_net, format_number
from .render import render_net_page, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nets",
        description="立体图形展开图：长方体、正方体的表面积、体积与可打印展开图",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    net_parser = subparsers.add_parser("net", help="生成单个展开图页面")
    net_parser.add_argument("width", type=float, help="长（厘米）")
    net_parser.add_argument("height", type=float, help="高（厘米）")
    net_parser.add_argument("depth", type=float, help="宽（厘米）")
    net_parser.add_argument("--mm-per-cm", type=float, default=8.0, help="每厘米画多少毫米，默认 8")
    net_parser.add_argument("--title", default="", help="页面标题")
    net_parser.add_argument("-o", "--output", default=None, help="输出文件")

    info_parser = subparsers.add_parser("info", help="查看表面积与体积")
    info_parser.add_argument("width", type=float)
    info_parser.add_argument("height", type=float)
    info_parser.add_argument("depth", type=float)

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet_parser.add_argument("--low", type=int, default=2, help="最小尺寸，默认 2")
    sheet_parser.add_argument("--high", type=int, default=8, help="最大尺寸，默认 8")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument("--title", default="长方体与正方体练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加答案与展开图")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "net":
            shape = Cuboid(args.width, args.height, args.depth)
            _write_output(
                render_net_page(shape, args.title, args.mm_per_cm), args.output
            )
            return 0
        if args.command == "info":
            shape = Cuboid(args.width, args.height, args.depth)
            net = build_net(shape)
            print("形状：%s" % shape.name)
            print("尺寸：%s" % shape.dimensions_text)
            print("表面积：%s cm²" % format_number(shape.surface_area))
            print("体积：%s cm³" % format_number(shape.volume))
            print(
                "展开图尺寸：%s × %s cm"
                % (format_number(net.width), format_number(net.height))
            )
            return 0
        items = build_worksheet(args.count, args.seed, args.low, args.high)
        _write_output(
            render_worksheet(items, args.title, include_answers=args.answers),
            args.output,
        )
        return 0
    except NetError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
