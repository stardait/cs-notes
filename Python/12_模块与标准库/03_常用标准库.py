"""
================================================================================
第 12 章 · 模块与标准库
文件 03：常用标准库
================================================================================

【学习目标】
    1. 掌握 8 个最常用的标准库：os / sys / json / datetime / random / math
       / collections / itertools
    2. 知道每个库「解决什么问题」，遇到需求能想到它
    3. 记住它们的经典用法，能直接抄去用

【怎么用这个文件】
    - 每个知识点一个库，独立成节，可以跳着看
    - 标准库不用安装，import 就能用（这是 Python「自带电池」的意思）
    - 「输出」块是运行后的实际结果，注意 Windows 路径是反斜杠
    - 直接运行：python 03_常用标准库.py

【前置知识】
    - 第 05 章：字典与集合（Counter、defaultdict 都是字典的亲戚）
    - 第 10 章：迭代器与生成器（itertools 全是迭代器）
================================================================================
"""

import os                           # 路径、目录、环境变量
import sys                          # 解释器相关
import json                         # JSON 序列化 / 反序列化
import datetime as dt               # 日期时间（用别名省事）
import random                       # 随机数
import math                         # 数学函数
from collections import Counter, defaultdict, namedtuple, deque   # 容器类型
import itertools                    # 迭代器工具


# ==============================================================================
# 知识点 1：os —— 和操作系统打交道
# ==============================================================================
#
# 【讲解】os 是「你和操作系统之间的传话人」：拼路径、建目录、删文件、
#   读环境变量、跑命令……操作系统能干的事它基本都能干。
# 【重点】路径拼接永远用 os.path.join，不要自己写 "a" + "/" + "b"：
#   Windows 用 \、Linux/macOS 用 /，自己拼的代码换个系统就崩。
# 【注意】本文件在 Windows 上跑，分隔符显示为 \；Linux 上会看到 /。

print("--- os：操作系统传话人 ---")

path = os.path.join("data", "2026", "todos.json")     # 自动用当前系统的分隔符
print(f"拼出来的路径：{path}")
print(f"当前系统的路径分隔符：{os.sep!r}")
print(f"文件名部分：{os.path.basename(path)}，目录部分：{os.path.dirname(path)}")

# 拆扩展名（注意 .tar.gz 只拆最后一个点）
print(f"splitext('report.tar.gz')：{os.path.splitext('report.tar.gz')}")
print(f"这个文件存在吗：{os.path.exists('绝对不存在的文件_123.txt')}")

# 读环境变量（不存在时给默认值，否则返回 None）
print(f"不存在的环境变量：{os.environ.get('不存在的变量名', '默认值')}")
print(f"PATH 环境变量存在吗：{os.getenv('PATH') is not None}")

# 输出：
# --- os：操作系统传话人 ---
# 拼出来的路径：data\2026\todos.json
# 当前系统的路径分隔符：'\\'
# 文件名部分：todos.json，目录部分：data\2026
# splitext('report.tar.gz')：('report.tar', '.gz')
# 这个文件存在吗：False
# 不存在的环境变量：默认值
# PATH 环境变量存在吗：True
#
# 【注意】路径里的 \ 是 Windows 风格；在 Linux/macOS 上是 data/2026/todos.json。
# 【重点】os.path.join 只会拼字符串，不会检查目录是否存在！要建目录得用
#   os.makedirs("data/2026", exist_ok=True)。exist_ok=True 意为「已存在就别报错」，
#   加上它，程序就能反复运行。


# ==============================================================================
# 知识点 2：sys —— 和 Python 解释器打交道
# ==============================================================================
#
# 【讲解】os 管操作系统，sys 管「Python 自己」：版本号、模块搜索路径、
#   命令行参数、标准输入输出……都在这里。
# 【重点】sys.argv 是命令行参数列表，argv[0] 是脚本名，从 argv[1] 起才是你传的参数。

print("\n--- sys：解释器信息 ---")
print(f"Python 版本：{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print(f"操作系统平台：{sys.platform}，是 64 位吗：{sys.maxsize > 2**60}")
print(f"递归深度上限：{sys.getrecursionlimit()}")
print(f"标准库包含 os 吗：{'os' in sys.stdlib_module_names}，包含 requests 吗：{'requests' in sys.stdlib_module_names}")
print(f"argv[0] 是本文件吗：{sys.argv[0].endswith('03_常用标准库.py')}")

# 输出：
# --- sys：解释器信息 ---
# Python 版本：3.15.2
# 操作系统平台：win32，是 64 位吗：True
# 递归深度上限：1000
# 标准库包含 os 吗：True，包含 requests 吗：False
# argv[0] 是本文件吗：True
#
# 【注意】版本号、平台名都会随环境变化，这里是本机（Windows + Python 3.15.2）。
# 【重点】`'requests' in sys.stdlib_module_names` 是 False，说明 requests 不是
#   标准库、必须 pip 安装。这也是判断「某模块要不要装」的小技巧。


# ==============================================================================
# 知识点 3：json —— 数据的「通用语言」
# ==============================================================================
#
# 【讲解】json 是程序之间交换数据的通用格式，长得像 Python 的字典和列表。
#       json.dumps(对象)    → 把 Python 对象转成 JSON 字符串（d = dump 出字符串）
#       json.loads(字符串)  → 把 JSON 字符串转回 Python 对象（l = load 回来）
#       json.dump(对象, 文件) / json.load(文件)  → 同样的事，但直接读写文件
# 【重点】ensure_ascii=False 必加！否则中文会变成 \u5c0f\u660e 这种鬼样子。
# 【重点】indent=2 让输出带缩进，人看得懂；不写就是挤成一行的「机器版」。

print("\n--- json：数据通用语言 ---")

data = {"name": "小明", "age": 18, "tags": ["学生", "编程"], "active": True, "score": None}

print(json.dumps(data, ensure_ascii=False))                       # 紧凑版，中文正常显示
print(json.dumps(data, ensure_ascii=True)[:30] + " ...")          # 中文被转义成 \uXXXX
print(json.dumps(data, ensure_ascii=False, indent=2))             # 带缩进，人看得懂
print(f"sort_keys 排序后：{json.dumps({'b': 1, 'a': 2}, sort_keys=True)}")

# 反序列化：字符串 → Python 对象
back = json.loads('{"名字": "小红", "年龄": 20, "爱好": ["画画"]}')
print(f"转回 Python 后：{back}")
print(f"类型是：{type(back).__name__}，取名字：{back['名字']}")

# 输出：
# --- json：数据通用语言 ---
# {"name": "小明", "age": 18, "tags": ["学生", "编程"], "active": true, "score": null}
# {"name": "\u5c0f\u660e", "age" ...
# {
#   "name": "小明",
#   "age": 18,
#   "tags": [
#     "学生",
#     "编程"
#   ],
#   "active": true,
#   "score": null
# }
# sort_keys 排序后：{"a": 2, "b": 1}
# 转回 Python 后：{'名字': '小红', '年龄': 20, '爱好': ['画画']}
# 类型是：dict，取名字：小红
#
# 【重点】三个「语言差异」：Python 的 True/False/None 在 JSON 里是小写
#   true/false/null；Python 元组会变成列表；JSON 的 key 必须是双引号字符串。
# 【常见错误】手写 JSON 时用了单引号或末尾多逗号，json.loads 直接报错
#   （{'a': 1} 和 {"a": 1,} 都不合法）。正确做法：用 json.dumps 生成，别手写。


# ==============================================================================
# 知识点 4：datetime —— 日期和时间
# ==============================================================================
#
# 【讲解】datetime 模块有三个主角：date 只有日期、time 只有时间、datetime
#   是日期 + 时间。还有一个 timedelta，表示「一段时间」（3 天 2 小时），
#   专门用来算日期加减。
# 【重点】日期加减用 timedelta，永远不要自己算「这个月有几天」——
#   闰年、大小月、时区全是坑，datetime 都帮你处理好了。

print("\n--- datetime：日期时间 ---")

d = dt.date(2026, 11, 12)                      # 固定日期，保证输出可复现
print(f"日期：{d}，年/月/日：{d.year} / {d.month} / {d.day}")
print(f"星期几（0=周一）：{d.weekday()} → 星期{'一二三四五六日'[d.weekday()]}")
print(f"100 天后：{d + dt.timedelta(days=100)}，到 2027 元旦还有 {(dt.date(2027, 1, 1) - d).days} 天")

# 格式化输出：strftime = string format time
moment = dt.datetime(2026, 11, 12, 14, 30, 5)
print(f"格式化：{moment.strftime('%Y年%m月%d日 %H:%M:%S')}")
print(f"ISO 格式：{moment.isoformat()}")

# 解析字符串：strptime = string parse time（注意 p 和 f 别搞混）
print(f"解析字符串：{dt.datetime.strptime('2026-11-12 14:30', '%Y-%m-%d %H:%M')}")

# 输出：
# --- datetime：日期时间 ---
# 日期：2026-11-12，年/月/日：2026 / 11 / 12
# 星期几（0=周一）：3 → 星期四
# 100 天后：2027-02-20，到 2027 元旦还有 50 天
# 格式化：2026年11月12日 14:30:05
# ISO 格式：2026-11-12T14:30:05
# 解析字符串：2026-11-12 14:30:00
#
# 【常见错误】strftime 和 strptime 长得像、容易用反：
#   strftime：datetime 对象 → 字符串（f = format，格式化输出）
#   strptime：字符串 → datetime 对象（p = parse，解析输入）
# 【重点】获取「现在」用 dt.datetime.now()（本机时区）或 now(dt.timezone.utc)；
#   Python 3.12 起 utcnow() 已弃用，别再用它了。


# ==============================================================================
# 知识点 5：random —— 随机数
# ==============================================================================
#
# 【讲解】random 生成的是「伪随机数」：看起来随机，其实是按公式算出来的。
#   所以只要给它同一个「种子」（seed），结果就完全一样——这叫可复现。
# 【重点】random.seed(42) 是调试神器：固定种子就能重现随机序列，否则抓不到现场。
# 【重点】random 不能用来做密码、抽奖、加密！要用 secrets 模块（专门做安全随机）。

print("\n--- random：随机数 ---")

random.seed(42)                                     # 固定种子 → 输出可复现
print(f"5 个 1~100 的整数：{[random.randint(1, 100) for _ in range(5)]}")

random.seed(42)                                     # 重新播种，序列从头开始
print(f"从列表里抽 5 次：{[random.choice(['石头', '剪刀', '布']) for _ in range(5)]}")

random.seed(42)
numbers = list(range(1, 9))                         # [1..8]
random.shuffle(numbers)                             # 原地打乱（无返回值！）
print(f"打乱后的 1~8：{numbers}")

random.seed(42)
print(f"随机浮点 0~1：{random.random():.4f}，接着 1~10：{random.uniform(1, 10):.3f}")
random.seed(42)
print(f"不重复抽 5 个：{random.sample(range(1, 50), 5)}")
# 输出：
# --- random：随机数 ---
# 5 个 1~100 的整数：[82, 15, 4, 95, 36]
# 从列表里抽 5 次：['布', '石头', '石头', '布', '剪刀']
# 打乱后的 1~8：[4, 5, 7, 8, 3, 6, 1, 2]
# 随机浮点 0~1：0.6394，接着 1~10：1.225
# 不重复抽 5 个：[41, 8, 2, 48, 18]
#
# 【注意】同一行里两个随机数是「按顺序」从流里取的：random() 拿走第一个，
#   uniform 拿第二个，所以 1~10 那个是 1.225 而不是单独 seed 时的 6.755。
#   【重点】随机数是「有顺序的流」，多调一次就少一个，别指望可交换。
#
# 【注意】这些数字是 seed(42) + Python 3.15 的固定结果。
#   换 Python 版本结果可能不同；不固定种子则每次都不同。
# 【常见错误】`numbers = random.shuffle(numbers)` —— shuffle 是原地打乱、返回
#   None！这么写 numbers 就变成 None 了。正确写法是直接 random.shuffle(numbers)。


# ==============================================================================
# 知识点 6：math —— 数学函数
# ==============================================================================
#
# 【讲解】math 提供各种数学函数和常量。要玩「更高级的数学」（矩阵、向量）
#   得上 numpy（下一个文件讲），但日常够用了。
# 【重点】三个取整函数是新手必踩的坑：floor 向下（-∞），floor(-3.5) = -4；
#   ceil 向上（+∞），ceil(-3.5) = -3；trunc 向零截断，trunc(-3.5) = -3。
#   而 round() 是四舍五入，但它用的是「银行家舍入」：round(2.5) = 2。

print("\n--- math：数学函数 ---")

print(f"圆周率 pi = {math.pi:.10f}")
print(f"gcd(48, 18) = {math.gcd(48, 18)}，lcm(4, 6) = {math.lcm(4, 6)}")
print(f"5 的阶乘 = {math.factorial(5)}，sqrt(2) = {math.sqrt(2):.6f}")
print(f"floor(-3.5)={math.floor(-3.5)}  ceil(-3.5)={math.ceil(-3.5)}  trunc(-3.5)={math.trunc(-3.5)}")
print(f"round(2.5)={round(2.5)}  round(3.5)={round(3.5)}   ← 银行家舍入：偶数优先")
print(f"0.1+0.2 和 0.3 相等吗：{math.isclose(0.1 + 0.2, 0.3)}")
print(f"无穷大：{math.inf}，负无穷：{-math.inf}，nan 是 nan 吗：{math.isnan(math.nan)}")

# 输出：
# --- math：数学函数 ---
# 圆周率 pi = 3.1415926536
# gcd(48, 18) = 6，lcm(4, 6) = 12
# 5 的阶乘 = 120，sqrt(2) = 1.414214
# floor(-3.5)=-4  ceil(-3.5)=-3  trunc(-3.5)=-3
# round(2.5)=2  round(3.5)=4   ← 银行家舍入：偶数优先
# 0.1+0.2 和 0.3 相等吗：True
# 无穷大：inf，负无穷：-inf，nan 是 nan 吗：True
#
# 【重点】round(2.5) 得到 2 不是 3！这叫「银行家舍入」（四舍六入五取偶），
#   目的是让大量数据的误差相互抵消。想强制四舍五入要用 decimal 模块。
# 【常见错误】math.sqrt(-1) 会抛 ValueError: math domain error，不是返回 nan。
#   要判断能不能开方，先 `if x >= 0`，或者改用 cmath（复数版）。


# ==============================================================================
# 知识点 7：collections —— 加强版容器
# ==============================================================================
#
# 【讲解】collections 是「容器工具箱」，四个宝贝：
#   Counter 计数器（数次数）、defaultdict 带默认值的字典、namedtuple 带字段名的
#   元组、deque 双端队列（两头都能快速增删，而 list 头插很慢）。
# 【重点】Counter.most_common(3) 一行搞定「词频统计 Top 3」，数据分析最常用。

print("\n--- collections：加强版容器 ---")

# Counter：统计出现次数
counter = Counter("abracadabra")
print(f"每个字符出现几次：{dict(counter)}")
print(f"出现最多的 3 个：{counter.most_common(3)}")

# defaultdict：key 不存在时自动用 list() 当默认值
groups = defaultdict(list)
for kind, name in [("水果", "苹果"), ("蔬菜", "白菜"), ("水果", "香蕉")]:
    groups[kind].append(name)                      # 不怕 key 不存在，自动建空列表
print(f"分组结果：{dict(groups)}")

# namedtuple：给元组每个位置起名字
Point = namedtuple("Point", "x y")
p = Point(3, 4)
print(f"Point(3, 4) = {p}，x={p.x}，y={p.y}，下标也能用 p[0]={p[0]}")

# deque：限长双端队列，超长时自动踢掉另一头
recent = deque([1, 2, 3], maxlen=3)
recent.append(4)                                   # 右边进 4，左边挤掉 1
recent.appendleft(0)                               # 左边进 0，右边挤掉 4
print(f"deque(maxlen=3) 的当前内容：{list(recent)}")

# 输出：
# --- collections：加强版容器 ---
# 每个字符出现几次：{'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}
# 出现最多的 3 个：[('a', 5), ('b', 2), ('r', 2)]
# 分组结果：{'水果': ['苹果', '香蕉'], '蔬菜': ['白菜']}
# Point(3, 4) = Point(x=3, y=4)，x=3，y=4，下标也能用 p[0]=3
# deque(maxlen=3) 的当前内容：[0, 2, 3]
#
# 【重点】deque(maxlen=3) 是「只保留最近 N 条」的完美实现：超过长度自动从
#   另一头弹出，不用手动删。日志、历史记录都用它。
# 【常见错误】defaultdict(list) 不能写成 defaultdict(list())：前者传「类型」，
#   后者传「一个空列表实例」，会报 TypeError。【记法】传函数/类型，别传调用结果。


# ==============================================================================
# 知识点 8：itertools —— 迭代器工厂
# ==============================================================================
#
# 【讲解】itertools 里全是「生成迭代器的函数」，共同特点是【懒加载】：
#   不一次性把所有结果算出来，要一个给一个，所以再大的数据也不爆内存。
# 【重点】几个必备的：count(start, step) 无限计数器（必须配 islice 限量）；
#   chain 串接；combinations 组合；permutations 排列；product 笛卡尔积；
#   groupby 分组（必须先排序，否则同样的 key 会被分成两段！）。

print("\n--- itertools：迭代器工厂 ---")

# count 无限，islice 截取前 n 个（不加 islice 会无限打印，程序卡死）
print(f"1 开始步长 2 的前 4 个：{list(itertools.islice(itertools.count(1, 2), 4))}")
print(f"chain 串起来：{list(itertools.chain([1, 2], [3], [4, 5]))}")
print(f"组合 C(4,2)：{list(itertools.combinations([1, 2, 3, 4], 2))}")
print(f"排列 A(3,2)：{list(itertools.permutations('ABC', 2))}")

# 笛卡尔积：两个列表的所有搭配（做测试用例、做菜单组合特别有用）
print(f"笛卡尔积：{list(itertools.product('AB', repeat=2))}")

# groupby：把相邻的相同元素归组（注意：它只合并「相邻」的！）
for key, group in itertools.groupby("AAABBC"):
    print(f"  {key} → {len(list(group))} 个")

# accumulate：累积计算（默认累加，也能传函数）
print(f"累加：{list(itertools.accumulate([1, 2, 3, 4]))}")
print(f"累乘：{list(itertools.accumulate([1, 2, 3, 4], lambda a, b: a * b))}")

# 输出：
# --- itertools：迭代器工厂 ---
# 1 开始步长 2 的前 4 个：[1, 3, 5, 7]
# chain 串起来：[1, 2, 3, 4, 5]
# 组合 C(4,2)：[(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
# 排列 A(3,2)：[('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]
# 笛卡尔积：[('A', 'A'), ('A', 'B'), ('B', 'A'), ('B', 'B')]
#   A → 3 个
#   B → 2 个
#   C → 1 个
# 累加：[1, 3, 6, 10]
# 累乘：[1, 2, 6, 24]
#
# 【重点】groupby 只合并「相邻」的相同元素！数据 AABA 会分成 A(2)/B(1)/A(1)
#   三段，而不是 A(3)/B(1)。所以用之前必须先用 sorted(...) 排序。
# 【常见错误】itertools 的函数返回「迭代器」，只能遍历一次：list(gen) 拿完后
#   再 list(gen) 就是空的。需要多次使用就先转成 list 存起来。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. os：路径用 os.path.join 拼（跨系统安全），判断存在用 os.path.exists
# 2. sys：sys.argv 收命令行参数，sys.version_info 查版本，sys.platform 查系统
# 3. json：dumps/loads 处理字符串，dump/load 处理文件；ensure_ascii=False 保中文
# 4. json 与 Python 的类型差异：True→true，None→null，元组→列表，key 必须双引号
# 5. datetime：date / time / datetime 三兄弟 + timedelta 算日期加减
# 6. strftime 格式化输出（对象→字符串），strptime 解析输入（字符串→对象）
# 7. random：seed 固定种子可复现；shuffle 原地打乱返回 None；安全场景用 secrets
# 8. math：floor/ceil/trunc 三种取整不同；round 是银行家舍入；比较浮点用 isclose
# 9. collections：Counter 计数、defaultdict 免判空、namedtuple 起字段名、deque 限长
# 10. itertools：全部懒加载；count 要配 islice；groupby 前必须先排序
# 11. 判断一个模块是不是标准库：'名字' in sys.stdlib_module_names


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：用 os 列出当前目录下所有 .py 文件及其大小（os.listdir + os.path.getsize）。
# 练习 2：用 json 把一个字典列表存成 todos.json，再读回来打印，确认内容一致。
# 练习 3：用 datetime 计算「你的生日到今天过了多少天」，再算出「下一个生日是星期几」。
# 练习 4：用 random 写「猜数字」的核心逻辑（不用 input，让计算机自己随机猜
#         10 次并统计平均猜中次数）。
# 练习 5：用 Counter 统计一段英文里出现最多的 5 个单词（提示：先 split）。
# 练习 6：用 itertools.combinations 算出「5 个人里选 2 人」的所有组合。
#
# 【下一步】04_第三方库入门.py
# ==============================================================================
