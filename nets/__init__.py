"""nets：立体图形展开图。"""

from .model import (
    FACE_LABELS,
    Cuboid,
    Net,
    NetError,
    NetFace,
    WorksheetItem,
    build_net,
    build_worksheet,
    check_answer,
    check_dimension,
    format_number,
    parse_measurement,
)
from .render import net_svg, render_net_page, render_worksheet

__all__ = [
    "FACE_LABELS",
    "Cuboid",
    "Net",
    "NetError",
    "NetFace",
    "WorksheetItem",
    "build_net",
    "build_worksheet",
    "check_answer",
    "check_dimension",
    "format_number",
    "net_svg",
    "parse_measurement",
    "render_net_page",
    "render_worksheet",
]

__version__ = "0.1.0"
