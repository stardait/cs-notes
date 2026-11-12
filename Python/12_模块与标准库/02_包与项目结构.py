"""
================================================================================
第 12 章 · 模块与标准库
文件 02：包与项目结构
================================================================================

【学习目标】
    1. 理解「包」是什么：装了多个模块的文件夹
    2. 搞懂 __init__.py 的三个作用（标识包、初始化、控制 import *）
    3. 分清绝对导入和相对导入，知道各自什么时候用
    4. 理解「直接运行包内模块会报错」的原因，学会用 python -m 解决
    5. 认识标准的 Python 项目目录布局

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 本文件会在临时目录里动态创建演示用的包，运行完自动清理
    - 直接运行：python 02_包与项目结构.py

【前置知识】
    - 本文件 01_模块导入.py（模块、__name__、sys.path 都会用到）
================================================================================
"""

import os                           # os：拼路径、建目录
import sys                          # sys：改 sys.path、取解释器路径
import subprocess                   # subprocess：在别的目录里跑 python
import tempfile                     # tempfile：建临时目录
import shutil                       # shutil：删目录


# ==============================================================================
# 知识点 1：包是什么？—— 装了多个模块的文件夹
# ==============================================================================
#
# 【讲解】模块是「盒子」，包就是「装盒子的抽屉」。工具一多，一个文件装不下，
#   就新建文件夹把相关模块放进去——这个带 __init__.py 的文件夹就叫包。
#       shop/                 ← 文件夹名 = 包名
#           __init__.py       ← 这个文件让 shop 成为「包」
#           cart.py           ← 导入路径是 shop.cart
#           pricing.py        ← 导入路径是 shop.pricing
# 【重点】包的磁盘路径和导入路径用点号对应：shop/cart.py → import shop.cart
# 【为什么】一个 .py 是抽屉，一个包是柜子，一个项目是房间。

demo_root = tempfile.mkdtemp(prefix="shopdemo_")        # 临时根目录（相当于项目根）
pkg_dir = os.path.join(demo_root, "shop")               # 包目录名就是包名
os.makedirs(pkg_dir)                                    # 建出 shop/ 文件夹

print("--- 包是什么 ---")
print(f"包目录名：{os.path.basename(pkg_dir)}")
print(f"包目录存在吗：{os.path.isdir(pkg_dir)}")

# 输出：
# --- 包是什么 ---
# 包目录名：shop
# 包目录存在吗：True


# ==============================================================================
# 知识点 2：__init__.py —— 包自己的「开场白」
# ==============================================================================
#
# 【讲解】__init__.py 是包的身份证 + 前台接待员，它有三个作用：
#   作用 1：标识这是一个包。老版本必须写，现在没有也能导入（命名空间包），
#           但仍【强烈建议】写上，因为 pytest、打包工具都靠它识别包。
#   作用 2：包被导入时自动执行（初始化），适合放版本号、对外接口。
#   作用 3：用 __all__ 控制 from 包 import * 能导出什么。
# 【重点】这里绝对不要写耗时操作（读大文件、连数据库），因为任何人 import
#   这个包都会被迫执行它，拖慢整个程序启动。
init_source = '''"""shop 包：一个卖东西的小商店。"""
__version__ = "1.0.0"                       # 包级常量：版本号
__all__ = ["cart", "pricing"]               # 星号导入时导出这两个子模块

print("[__init__.py 执行] shop 包初始化完成")
'''

pricing_source = '''"""价格计算模块。"""
TAX_RATE = 1.1


def total(prices):
    """把价格列表加总并含税，保留 2 位小数。"""
    return round(sum(prices) * TAX_RATE, 2)
'''

cart_source = '''"""购物车模块。"""
from .pricing import total          # 相对导入：. 表示「我所在的这个包」


def summary(prices):
    """返回一句话描述。"""
    return f"{len(prices)} 件商品，合计 {total(prices)} 元"


if __name__ == "__main__":
    print(summary([10, 20, 30]))
'''

# 把三个文件写进包目录（写文件都指定 utf-8，否则 Windows 中文会出问题）
for filename, source in [("__init__.py", init_source), ("pricing.py", pricing_source),
                         ("cart.py", cart_source)]:
    with open(os.path.join(pkg_dir, filename), "w", encoding="utf-8") as f:
        f.write(source)

print("\n--- __init__.py 的作用 ---")
print(f"包里有几个 .py 文件：{len(os.listdir(pkg_dir))}")
print(f"其中包含 __init__.py 吗：{'__init__.py' in os.listdir(pkg_dir)}")
sys.path.insert(0, demo_root)      # 把项目根目录塞进搜索路径，才能 import shop
import shop                        # 第一次导入包：会执行 __init__.py

print(f"包的版本号 shop.__version__：{shop.__version__}")
print(f"包的 __all__：{shop.__all__}")
print(f"包的文件名：{os.path.basename(shop.__file__)}")

# 输出：
# --- __init__.py 的作用 ---
# 包里有几个 .py 文件：3
# 其中包含 __init__.py 吗：True
# [__init__.py 执行] shop 包初始化完成
# 包的版本号 shop.__version__：1.0.0
# 包的 __all__：['cart', 'pricing']
# 包的文件名：__init__.py
#
# 【重点】"[__init__.py 执行] ..." 是在 `import shop` 那一刻打印的，证明包的
#   初始化代码真被执行了（和「模块只加载一次」同一个道理）。
# 【重点】`shop.__file__` 指向 __init__.py——「包」本身就用这个文件代表自己。


# ==============================================================================
# 知识点 3：包里的东西怎么导入？—— 三种写法
# ==============================================================================
#
# 【讲解】包里的模块有三种导入姿势：
#   写法 A：import shop.cart                  然后 shop.cart.summary(...)
#   写法 B：from shop import cart             然后 cart.summary(...)
#   写法 C：from shop.cart import summary     直接用 summary(...)
# 【重点】越往下越短，但来源越模糊。推荐：跨包用 A/B，包内部用 C。
#   包不会自动导入子模块，必须自己写 import。
print("\n--- 三种导入写法 ---")

import shop.pricing                            # 写法 A：导整个子模块
from shop import cart                          # 写法 B：从包里拿子模块
from shop.cart import summary                  # 写法 C：直接拿函数

print(f"写法A  shop.pricing.total([10, 20]) = {shop.pricing.total([10, 20])}")
print(f"写法B  cart.summary([10, 20, 30])    = {cart.summary([10, 20, 30])}")
print(f"写法C  summary([100])                = {summary([100])}")
print(f"写法B 拿到的 cart 和 shop.cart 是同一个吗：{cart is shop.cart}")

from shop import *                             # 星号导入：只导出 __all__ 里列的

print(f"星号导入拿到：{cart.__name__} 和 {pricing.__name__}")

# 输出：
# --- 三种导入写法 ---
# 写法A  shop.pricing.total([10, 20]) = 33.0
# 写法B  cart.summary([10, 20, 30])    = 3 件商品，合计 66.0 元
# 写法C  summary([100])                = 1 件商品，合计 110.0 元
# 写法B 拿到的 cart 和 shop.cart 是同一个吗：True
# 星号导入拿到：shop.cart 和 shop.pricing
#
# 【重点】三种写法拿到的是同一个模块对象（is 为 True），因为 sys.modules
#         里只有一份（第 01 个文件讲的缓存机制）。
# 【常见错误】`from shop import *` 只导出 __all__ 里写的名字。若 __init__.py
#   没写 __all__，星号导入只拿到它自己定义的名字（如 __version__）。


# ==============================================================================
# 知识点 4：绝对导入 vs 相对导入
# ==============================================================================
#
# 【讲解】包内部互相引用有两种写法：
#   绝对导入：from shop.pricing import total
#       → 像寄快递写「省-市-区」全地址，从哪儿读都清楚
#   相对导入：from .pricing import total     # .  = 当前包（同目录）
#             from ..utils import helper     # .. = 上一级包（父目录）
#       → 像说「我隔壁那间」，只在包内部才说得通
# 【重点】规则：一个点 = 当前包，两个点 = 父包，依此类推。
# 【重点】相对导入【只能用在包里】。直接 python cart.py 跑它，因为此时它不属于
#   任何包，点号无处可依，会直接报 ImportError（下个知识点演示）。
# 【为什么用相对导入】包改名时包内部不用动；缺点是难读、容易数错点号。
print("\n--- 绝对导入 vs 相对导入 ---")
print(f"绝对导入拿到 total：{shop.pricing.total([10, 20])}")
print(f"相对导入（cart.summary 内部用了它）：{cart.summary([10, 20])}")
print("两者算法一致，说明相对导入指向的就是同一份 pricing 模块")

# 输出：
# --- 绝对导入 vs 相对导入 ---
# 绝对导入拿到 total：33.0
# 相对导入（cart.summary 内部用了它）：2 件商品，合计 33.0 元
# 两者算法一致，说明相对导入指向的就是同一份 pricing 模块
#
# 【常见错误】相对导入写成 `from pricing import total`（少了点号）：这会被当成
#   「从 sys.path 里找顶层模块 pricing」，而不是同包兄弟，包内通常直接
#   ModuleNotFoundError。【记法】同一个包内互相引用，一定要写点号。

# ==============================================================================
# 知识点 5：为什么直接运行包内模块会报错？—— python -m 的救场
# ==============================================================================
#
# 【讲解】新手最抓狂的报错之一。直接运行 shop/cart.py 会报：
#       ImportError: attempted relative import with no known parent package
#   （意思：你用了相对导入，但我不知道你的父包是谁）
# 【为什么】`python 文件路径` 是把文件当成「孤零零的脚本」来跑，它的 __name__
#   是 "__main__"，不属于任何包。而 cart.py 里写着 `from .pricing import ...`，
#   点号需要知道「我属于哪个包」才能解析，孤立脚本没有包信息，于是崩了。
# 【重点】当脚本跑（python 文件）和当模块跑（python -m 包.模块）是两种完全
#   不同的方式！后者才会带上包上下文。

print("\n--- 直接运行 vs python -m ---")

cart_path = os.path.join(pkg_dir, "cart.py")

# 方式 1：直接运行文件（错误示范）
bad = subprocess.run([sys.executable, cart_path], capture_output=True,
                     text=True, encoding="utf-8")     # 抓回输出、文本模式、防乱码
last_line = bad.stderr.strip().splitlines()[-1]       # 只取报错的最后一行
print(f"直接运行 cart.py 的退出码：{bad.returncode}")
print(f"直接运行 cart.py 的报错：{last_line}")

# 方式 2：用 -m 当模块运行（正确示范）
good = subprocess.run([sys.executable, "-m", "shop.cart"], cwd=demo_root,
                      capture_output=True, text=True, encoding="utf-8")
print(f"python -m shop.cart 的退出码：{good.returncode}")
print("python -m shop.cart 的输出：")
print(good.stdout.strip())

# 输出：
# --- 直接运行 vs python -m ---
# 直接运行 cart.py 的退出码：1
# 直接运行 cart.py 的报错：ImportError: attempted relative import with no known parent package
# python -m shop.cart 的退出码：0
# python -m shop.cart 的输出：
# [__init__.py 执行] shop 包初始化完成
# 3 件商品，合计 66.0 元
#
# 【重点】同一个文件换一种运行方式就活了：直接跑路径退出码 1，
#   python -m 退出码 0（正常）。-m 的第一行是 __init__.py 的输出，
#   因为 -m shop.cart 会先导入 shop 包（执行 __init__.py），再运行 cart。# 【常见错误】用 python -m 必须站在「包的父目录」下。若在 shop/ 目录里敲
#   `python -m shop.cart`，会报 ModuleNotFoundError: No module named 'shop'。

# ==============================================================================
# 知识点 6：__main__.py —— 让整个包可以被 python -m 包名 执行
# ==============================================================================
#
# 【讲解】你有没有好奇过 `python -m http.server` 是怎么做到的？
#   答案就是那个包里有一个 __main__.py。
# 【重点】规则：执行 `python -m 包名` 时，Python 会去找包里的 __main__.py 并运行。
#   没有它就报：No module named shop.__main__; 'shop' is a package and cannot
#   be directly executed。它相当于 C 的 main 函数，是「这个包的总开关」。
print("\n--- __main__.py：包的入口 ---")

# 先演示「没有 __main__.py」时的报错
no_entry = subprocess.run([sys.executable, "-m", "shop"], cwd=demo_root,
                          capture_output=True, text=True, encoding="utf-8")
print(f"没有 __main__.py 时，python -m shop 的退出码：{no_entry.returncode}")
print(f"报错里提到 __main__ 吗：{'__main__' in no_entry.stderr}")

# 补上 __main__.py，再试一次
main_source = '''"""包的入口：python -m shop 时执行这个文件。"""
from .cart import summary

print("包入口启动了：" + summary([10, 20]))
'''
with open(os.path.join(pkg_dir, "__main__.py"), "w", encoding="utf-8") as f:
    f.write(main_source)

has_entry = subprocess.run([sys.executable, "-m", "shop"], cwd=demo_root,
                           capture_output=True, text=True, encoding="utf-8")
print(f"有了 __main__.py 后，退出码：{has_entry.returncode}")
print("输出：")
print(has_entry.stdout.strip())

# 输出：
# --- __main__.py：包的入口 ---
# 没有 __main__.py 时，python -m shop 的退出码：1
# 报错里提到 __main__ 吗：True
# 有了 __main__.py 后，退出码：0
# 输出：
# [__init__.py 执行] shop 包初始化完成
# 包入口启动了：2 件商品，合计 33.0 元
#
# 【重点】`python -m shop` 的顺序：先导入 shop 包 → 执行 __init__.py
#   （所以第一行是初始化输出），再找到并执行 shop/__main__.py。
# 【常见错误】__main__.py 里的相对导入（from .cart import summary）只在 -m
#   执行包时有效；直接 `python shop/__main__.py` 也会报
#   attempted relative import with no known parent package，原因同知识点 5。


# ==============================================================================
# 知识点 7：标准项目结构布局 —— 真实项目长什么样
# ==============================================================================
#
# 【讲解】真实项目的目录通常长这样（以「待办清单」为例）。下面用代码打印布局，
#   每一行都标了职责，你可以在自己的项目里照抄：

print("\n--- 标准项目结构 ---")

layout = [
    (0, "my_todo/", "项目根目录"), (1, "README.md", "说明文档：怎么装、怎么用"),
    (1, "pyproject.toml", "项目元信息 + 依赖声明"), (1, ".gitignore", "不提交 git"),
    (1, "requirements.txt", "依赖清单"), (1, "src/", "源码目录（推荐布局）"),
    (2, "my_todo/", "真正的包"), (3, "__init__.py", "包的身份证 + 版本号"),
    (3, "__main__.py", "命令行入口"), (3, "storage.py", "读写数据文件"),
    (1, "tests/", "测试目录，和源码分开"), (2, "test_cli.py", "测试命令行"),
]
for depth, name, note in layout:
    print(f"{'    ' * depth}{name:<16} # {note}")     # 缩进表示层级，补齐对齐

print(f"\n这个布局里一共列了 {len(layout)} 个条目")
print(f"其中 Python 文件有 {sum(1 for _, n, _ in layout if n.endswith('.py'))} 个")

# 输出：
# --- 标准项目结构 ---
# my_todo/         # 项目根目录
#     README.md        # 说明文档：怎么装、怎么用
#     pyproject.toml   # 项目元信息 + 依赖声明
#     .gitignore       # 不提交 git
#     requirements.txt # 依赖清单
#     src/             # 源码目录（推荐布局）
#         my_todo/         # 真正的包
#             __init__.py      # 包的身份证 + 版本号
#             __main__.py      # 命令行入口
#             storage.py       # 读写数据文件
#     tests/           # 测试目录，和源码分开
#         test_cli.py      # 测试命令行
#
# 这个布局里一共列了 12 个条目
# 其中 Python 文件有 4 个
#
# 【重点】三条布局铁律：
#   1. 源码、测试、文档分开放（别全堆根目录）
#   2. 包名用小写 + 下划线，别用中文、空格、连字符（连字符根本没法 import）
#   3. 环境相关的东西（venv/、__pycache__/）不要提交到 git
# 【为什么用 src/ 布局】若包直接放根目录，你在根目录跑测试时 Python 会优先导入
#   「当前目录下的源码」而不是已安装版本，于是「本地能跑、装完就崩」。
# 【常见错误】包名用连字符 my-todo/ → import my-todo 是语法错误（连字符是减号）；
#   仓库名爱叫什么都行，但包名必须是合法的 Python 标识符。


# ==============================================================================
# 知识点 8：清理现场
# ==============================================================================
#
# 【讲解】演示结束，删掉临时包目录，并从 sys.path 和 sys.modules 里清理 shop，
#   避免影响同一进程里的后续代码。真实项目不需要这样清理，纯属教学卫生。

print("\n--- 清理 ---")

if demo_root in sys.path:
    sys.path.remove(demo_root)                 # 移除临时根目录

# 清掉包里所有已加载的模块（shop、shop.pricing、shop.cart）
removed = [name for name in list(sys.modules) if name == "shop" or name.startswith("shop.")]
for name in removed:
    del sys.modules[name]

shutil.rmtree(demo_root, ignore_errors=True)   # 连 __pycache__ 一起删掉

print(f"从 sys.modules 清掉了 {len(removed)} 个模块")
print(f"临时目录还存在吗：{os.path.exists(demo_root)}")

# 输出：
# --- 清理 ---
# 从 sys.modules 清掉了 3 个模块
# 临时目录还存在吗：False
#
# 【注意】这里清掉 3 个：shop、shop.pricing、shop.cart；shop.__main__
#   只在子进程里被导入过，不在本进程的 sys.modules 里。
# 【重点】子进程（subprocess）有自己独立的解释器和模块表，不会污染本进程。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 包 = 带 __init__.py 的文件夹；shop/cart.py 对应导入路径 shop.cart
# 2. __init__.py 三大作用：标识包、导入包时自动初始化、用 __all__ 控制星号导入
# 3. __init__.py 里别写耗时操作，因为任何 import 都会触发它
# 4. 三种导入写法：import 包.模块 / from 包 import 模块 / from 包.模块 import 名字
# 5. 绝对导入从项目根写起（清楚）；相对导入用点号（. 当前包，.. 父包）
# 6. 相对导入只能用于包内部；直接用 python 运行包内模块会报 ImportError
# 7. python -m 包.模块 会带着包上下文运行，是运行包内模块的正确方式
# 8. __main__.py 让整个包能被 python -m 包名 执行（如 python -m http.server）
# 9. 标准布局：源码 / 测试 / 文档分开放；包名必须是小写的合法标识符
# 10. __pycache__ 和虚拟环境目录要写进 .gitignore，永远不提交


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：新建一个 animal 包，写 __init__.py、dog.py、cat.py，两个模块各有
#         一个 speak() 函数，在 __init__.py 里写好 __version__。
# 练习 2：在 dog.py 里用相对导入引用 cat.py 的 speak；然后分别
#         用 `python dog.py` 和 `python -m animal.dog` 运行，对比结果。
# 练习 3：给 animal 包加上 __main__.py，让它能用 `python -m animal` 运行，
#         输出「狗：汪汪 / 猫：喵喵」两行。
#
# 【下一步】03_常用标准库.py
# ==============================================================================
