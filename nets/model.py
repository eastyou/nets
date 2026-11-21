"""长方体与正方体：表面积、体积、展开图布局与题目生成。"""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

FACE_LABELS = ("前", "右", "后", "左", "上", "下")
_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?")


class NetError(ValueError):
    """尺寸或题目参数不合法。"""


def check_dimension(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NetError("尺寸必须是数字")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise NetError("尺寸必须是正数")
    if number > 100:
        raise NetError("尺寸不能超过 100 厘米")
    return number


@dataclass(frozen=True)
class Cuboid:
    """长、宽、高，单位厘米。"""

    width: float
    height: float
    depth: float

    def __post_init__(self) -> None:
        check_dimension(self.width)
        check_dimension(self.height)
        check_dimension(self.depth)

    @property
    def surface_area(self) -> float:
        return 2 * (self.width * self.height + self.width * self.depth + self.height * self.depth)

    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

    @property
    def is_cube(self) -> bool:
        return self.width == self.height == self.depth

    @property
    def name(self) -> str:
        return "正方体" if self.is_cube else "长方体"

    @property
    def dimensions_text(self) -> str:
        return "长 %s cm、宽 %s cm、高 %s cm" % (
            format_number(self.width),
            format_number(self.depth),
            format_number(self.height),
        )


@dataclass(frozen=True)
class NetFace:
    label: str
    x: float
    y: float
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True)
class Net:
    shape: Cuboid
    faces: Tuple[NetFace, ...]
    width: float
    height: float

    @property
    def total_area(self) -> float:
        return sum(face.area for face in self.faces)


def build_net(shape: Cuboid) -> Net:
    """标准十字展开图：一排四个侧面，上下各一个面。"""
    w, h, d = shape.width, shape.height, shape.depth
    faces = (
        NetFace("前", 0.0, h, w, h),
        NetFace("右", w, h, d, h),
        NetFace("后", w + d, h, w, h),
        NetFace("左", 2 * w + d, h, d, h),
        NetFace("上", w, 0.0, w, d),
        NetFace("下", w, 2 * h, w, d),
    )
    return Net(shape, faces, 2 * w + 2 * d, 2 * h + d)


@dataclass(frozen=True)
class WorksheetItem:
    """一道求表面积或体积的题。"""

    shape: Cuboid
    kind: str

    def __post_init__(self) -> None:
        if self.kind not in ("area", "volume"):
            raise NetError("题型必须是 area 或 volume")

    @property
    def answer(self) -> float:
        return self.shape.surface_area if self.kind == "area" else self.shape.volume

    @property
    def unit(self) -> str:
        return "cm²" if self.kind == "area" else "cm³"

    @property
    def answer_text(self) -> str:
        return "%s %s" % (format_number(self.answer), self.unit)

    @property
    def question(self) -> str:
        what = "表面积" if self.kind == "area" else "体积"
        return "%s，它的%s是多少？" % (self.shape.dimensions_text, what)


def format_number(value: float) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NetError("数值必须是数字")
    number = float(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return ("%.2f" % number).rstrip("0").rstrip(".")


def build_worksheet(
    count: int,
    seed: Optional[int] = None,
    low: int = 2,
    high: int = 8,
) -> List[WorksheetItem]:
    """生成尺寸固定范围内的表面积 / 体积题。"""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise NetError("题目数量必须是正整数")
    if isinstance(low, bool) or isinstance(high, bool) or not isinstance(low, int) or not isinstance(high, int):
        raise NetError("尺寸范围必须是整数")
    if low < 1:
        raise NetError("最小尺寸不能小于 1")
    if high < low:
        raise NetError("最大尺寸不能小于最小尺寸")
    span = high - low + 1
    total = 2 * span ** 3
    if count > total:
        raise NetError("可用的不重复题目不足 %d 道" % count)
    rng = random.Random(seed)
    items: List[WorksheetItem] = []
    seen = set()
    attempts = 0
    limit = count * 100 + 100
    while len(items) < count and attempts < limit:
        attempts += 1
        width = rng.randint(low, high)
        height = rng.randint(low, high)
        depth = rng.randint(low, high)
        kind = rng.choice(("area", "volume"))
        key = (width, height, depth, kind)
        if key in seen:
            continue
        seen.add(key)
        items.append(WorksheetItem(Cuboid(width, height, depth), kind))
    if len(items) < count:
        raise NetError("可用的不重复题目不足 %d 道" % count)
    return items


def parse_measurement(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        raise NetError("答案不能为空")
    match = _NUMBER.match(text.strip())
    if not match:
        raise NetError("答案必须以数字开头")
    value = float(match.group(0))
    if not math.isfinite(value) or value <= 0:
        raise NetError("答案必须是正数")
    return value


def check_answer(item: WorksheetItem, text: str, tolerance: float = 1e-6) -> bool:
    try:
        value = parse_measurement(text)
    except NetError:
        return False
    expected = item.answer
    return abs(value - expected) <= max(1e-9, abs(expected) * tolerance)
