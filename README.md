# nets

[![CI](https://github.com/eastyou/nets/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/nets/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

立体图形展开图：长方体、正方体的表面积、体积与可打印折叠图。

## 特性

- 标准十字展开图：四个侧面排成一排，上、下两面分别位于前后
- 每个面标注名称与两条边长，方便裁剪与折叠时核对
- 计算表面积与体积，练习题自动随机出题并去重
- 答案页附展开图，可直接打印成手工课材料
- 支持自定义每厘米的绘制比例与页面标题
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
nets net 5 4 3 -o cuboid.html
nets info 5 4 3
nets sheet --count 8 --seed 3 --answers -o sheet.html
nets sheet --count 6 --seed 5 --low 2 --high 6 -o easy.html
```

`net` 与 `info` 的参数顺序为「长 高 宽」，单位厘米。

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--count` | 题目数量 | 8 |
| `--low` | 最小尺寸 | 2 |
| `--high` | 最大尺寸 | 8 |
| `--seed` | 随机种子 | 无 |
| `--answers` | 追加答案页与展开图 | 关闭 |
| `--mm-per-cm` | 每厘米绘制多少毫米 | 8 |
| `--title` | 页面标题 | 自动 |

## 展开图布局

以长 `w`、高 `h`、宽 `d` 为例：

```
        ┌─────┐
        │ 上  │
┌─────┬─┴─────┴─┬─────┐
│ 前  │   右    │ 后  │ 左 │
└─────┴─────────┴─────┴────┘
        │ 下  │
        └─────┘
```

展开图总宽为 `2w + 2d`，总高为 `2h + d`，六个面的面积之和恰好等于表面积。

## 示例

- [examples/nets.html](examples/nets.html)：8 道表面积 / 体积练习，带答案页
- [examples/cuboid-net.html](examples/cuboid-net.html)：长 5、高 4、宽 3 的单个展开图

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
