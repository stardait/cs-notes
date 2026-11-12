"""
================================================================================
第 12 章 · 模块与标准库
文件 01：模块导入
================================================================================

【学习目标】
    1. 理解「模块」是什么，为什么要把代码拆成多个文件
    2. 掌握 4 种导入写法：import / from-import / as 别名 / 通配导入
    3. 理解 __name__ 和 if __name__ == "__main__" 到底在防什么
    4. 搞懂模块搜索路径 sys.path，知道 Python 去哪找模块
    5. 明白「模块只加载一次」和 sys.modules 缓存

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 01_模块导入.py

【前置知识】
    - 第 3 章：函数（模块里装的主要就是函数和类）
    - 第 11 章：异常与文件（会用到 with open 写临时文件）
================================================================================
"""

import sys                          # sys：和 Python 解释器打交道的模块
import os                           # os：和操作系统打交道的模块
import math                         # math：数学模块，用来演示内置模块的特点
import tempfile                     # tempfile：创建临时目录
import shutil                       # shutil：删除整个目录
import subprocess                   # subprocess：启动子进程

# 上面这 6 行就是本文件自己的「导入区」。看一个文件依赖了什么，看开头就够了。


# ==============================================================================
# 知识点 1：模块是什么？—— 一个 .py 文件就是一个模块
# ==============================================================================
#
# 【讲解】写程序像搭积木：所有积木堆一个盒子里必然乱，所以要「分盒装」。
#   模块就是盒子：math.py 是数学工具盒，json.py 是数据转换盒。
# 【重点】模块和文件一一对应：一个 xxx.py = 一个名叫 xxx 的模块（区分大小写！）
# 【为什么】拆模块三大好处：复用（写一次到处用）、可读（一文件一职责）、隔离。

print("--- 模块是什么 ---")
print(f"当前解释器版本：{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print(f"os 模块有没有 __file__ 属性：{hasattr(os, '__file__')}")
print(f"math 模块有没有 __file__ 属性：{hasattr(math, '__file__')}")
print(f"sys 模块是不是内置模块：{'sys' in sys.builtin_module_names}")

# 输出：
# --- 模块是什么 ---
# 当前解释器版本：3.15.2
# os 模块有没有 __file__ 属性：True
# math 模块有没有 __file__ 属性：False
# sys 模块是不是内置模块：True
#
# 【注意】版本号随你的 Python 版本变化，这里是本机的 3.15.2。
# 【重点】模块分三类：
#   1. 内置模块 builtin：sys、math、itertools…… 编译进 python.exe，没有 __file__
#   2. 标准库 stdlib：os、json、datetime…… 随 Python 安装，有真的 .py 文件
#   3. 第三方库：requests、numpy…… 要用 pip 另装（第 04 个文件讲）


# ==============================================================================
# 知识点 2：import 的四种写法
# ==============================================================================
#
# 【讲解】导入像点外卖的四种方式：
#   写法 1：import math              整盒搬回家，吃时说「math.sqrt」
#   写法 2：from math import sqrt    只拿一根吸管，直接说「sqrt」
#   写法 3：import math as m         整盒搬回家，起个外号「m」
#   写法 4：from math import *       把盒子倒桌上全摊开（危险！）
# 【重点】写法 1 最推荐：来源清晰，永远不会和你的变量重名。

print("\n--- 四种导入写法 ---")

from math import floor, ceil                # 写法 2：只导入指定的名字
import datetime as dt                       # 写法 3：起别名
from os.path import join as path_join       # 写法 3 的实战用途：避免重名
# 写法 4（from math import *）本文件故意不用，原因见下面的【常见错误】

print(f"写法1  math.sqrt(16)   = {math.sqrt(16)}   ← 要用 模块名.属性")
print(f"写法2  floor(3.7)      = {floor(3.7)}       ← 直接用，不写 math.")
print(f"写法3  dt.date(2026,11,12) = {dt.date(2026, 11, 12)}   ← 原名太长了")
print(f"写法3  path_join('a','b') = {path_join('a', 'b')}   ← as 也能防重名")

# 输出：
# --- 四种导入写法 ---
# 写法1  math.sqrt(16)   = 4.0   ← 要用 模块名.属性
# 写法2  floor(3.7)      = 3       ← 直接用，不写 math.
# 写法3  dt.date(2026,11,12) = 2026-11-12   ← 原名太长了
# 写法3  path_join('a','b') = a\b   ← as 也能防重名
#
# 【注意】`path_join('a','b')` 在 Windows 上显示 a\b，Linux/macOS 上是 a/b，
#         因为 os.path.join 用的是当前系统的路径分隔符。
# 【重点】as 别名两个用途：① 名字太长（datetime as dt、numpy as np）
#         ② 避免重名（from A import x as x1 和 from B import x as x2）；
#         `import numpy as np` 这种缩写是「行规」，全世界都这么写。
#
# 【常见错误】from math import * 的三个坑
#
#   坑 1：不知道名字从哪来。from math import * 再 from random import *，
#       这时 random() 到底是谁的？天知道。
#   坑 2：悄悄覆盖你已有的变量（最致命）
#       pi = 3                # 你定义的 pi
#       from math import *    # 导进来一个 pi
#       print(pi)             # 3.141592653589793 —— 你的 3 被干掉了，还不报错！
#   坑 3：污染命名空间，一个模块导进来 50 个名字，
#       后面你自己定义同名函数时怎么死的都不知道。
#
# 【结论】永远写 `import 模块` 或 `from 模块 import 具体名字`；
#         `import *` 只留给交互式命令行里临时玩。


# ==============================================================================
# 知识点 3：模块只加载一次 —— sys.modules 这张「已买清单」
# ==============================================================================
#
# 【讲解】去超市买东西，小票上记着已买了什么，再拿同样的东西直接从购物袋掏。
#   sys.modules 就是 Python 的购物小票。
# 【重点】同一个模块不管 import 多少次，模块代码只执行一次！后面的 import
#   只是从缓存里把「已加载的模块对象」取出来。
# 【为什么】模块顶层可能有副作用（打印、读配置、开连接），重复执行既慢又重复。

print("\n--- 模块只加载一次 ---")
print(f"导入前，'json' 在 sys.modules 里吗：{'json' in sys.modules}")

import json                     # 第一次导入：真去执行 json/__init__.py 的代码
print(f"第一次导入后，在 sys.modules 里吗：{'json' in sys.modules}")

import json                     # 第二次导入：什么都不做，直接拿缓存
import json                     # 第三次也一样
json_again = __import__("json")  # 用函数方式再导一次，还是同一个对象

print(f"json 模块名：{json.__name__}")
print(f"重复导入拿到的是同一个对象吗：{json_again is json}")
print(f"已加载模块数超过 50 个吗：{len(sys.modules) > 50}")

# 输出：
# --- 模块只加载一次 ---
# 导入前，'json' 在 sys.modules 里吗：False
# 第一次导入后，在 sys.modules 里吗：True
# json 模块名：json
# 重复导入拿到的是同一个对象吗：True
# 已加载模块数超过 50 个吗：True
#
# 【重点】记住这个公式：模块第一次 import → 执行模块代码 → 结果存进
#         sys.modules；之后每次 import 直接从 sys.modules 取，一行都不执行。
# 【注意】没有直接打印 len(sys.modules)，因为那数字每次运行都不一样。


# ==============================================================================
# 知识点 4：__name__ 与 if __name__ == "__main__" —— 全 Python 最重要的套路
# ==============================================================================
#
# 【讲解】这是新手最难理解、但工作中天天见到的一段代码：
#
#       if __name__ == "__main__":
#           main()
#
# 【重点】每个模块都有 __name__ 变量：文件被「直接运行」时值是 "__main__"，
#       被「import 导入」时值是「模块名」。
#   打个比方：直接运行 = 你自己开车（身份是「司机」__main__）；
#   被导入 = 你坐副驾当导航（身份是「导航员」= 模块名）。
# 【为什么需要它】模块被导入时通常不想让它自动跑主流程，只有直接运行才跑。

print("\n--- 本文件自己的 __name__ ---")
print(f"本文件是直接运行的吗：{__name__ == '__main__'}")
print(f"本文件的 __name__ 值： {__name__}")

if __name__ == "__main__":
    # 只有直接运行本文件时，这里的代码才会执行
    print("[main 块] 本文件被直接运行，主流程启动了")
else:
    print("[main 块] 本文件被导入，主流程已跳过")

# 输出：
# --- 本文件自己的 __name__ ---
# 本文件是直接运行的吗：True
# 本文件的 __name__ 值： __main__
# [main 块] 本文件被直接运行，主流程启动了
#
# 【重点】因为我们是 `python 01_模块导入.py` 直接跑的，所以 __name__ 是
#         "__main__"。如果用 import 导入本文件，会打印 False 和 "01_模块导入"。
# 【常见错误】很多新手把主流程写在文件顶层（不放进 if 里），
#   结果别人一 import 他的模块，主流程就自动跑：
#   轻则莫名输出一堆东西，重则开了个 web 服务卡死整个导入方。
# 【记法】模块 = 工具箱：工具（函数/类）永远可以拿，但「演示工具怎么用」
#   （主流程）只在你自己打开工具箱时才做。


# ==============================================================================
# 知识点 5：模块搜索路径 sys.path —— Python 去哪找模块？
# ==============================================================================
#
# 【讲解】写 `import json` 时，Python 按顺序去 sys.path 这个「地址簿」里
#   一个个目录翻，找到就用。sys.path 的构成（优先级从高到低）：
#       1. 脚本所在目录（直接运行时的 sys.path[0]）
#       2. 环境变量 PYTHONPATH 里的目录
#       3. 标准库目录
#       4. 第三方库目录 site-packages（pip 装的东西在这）
#   【重点】规则是「从上往下找，找到就停」，不是「挑最好的」。

print("\n--- sys.path：Python 的地址簿 ---")
print(f"第一个搜索位置就是本文件所在目录吗：{sys.path[0] == os.path.dirname(os.path.abspath(__file__))}")
print(f"路径数量超过 3 条吗：{len(sys.path) > 3}")
print(f"标准库里包含 'os' 吗：{'os' in sys.stdlib_module_names}")
print(f"本文件所在目录名：{os.path.basename(os.path.dirname(os.path.abspath(__file__)))}")

# 输出：
# --- sys.path：Python 的地址簿 ---
# 第一个搜索位置就是本文件所在目录吗：True
# 路径数量超过 3 条吗：True
# 标准库里包含 'os' 吗：True
# 本文件所在目录名：12_模块与标准库
#
# 【注意】没有直接打印 sys.path 全文，因为每台机器都不一样。你可以自己加
#         一行 `for p in sys.path: print(p)` 看看你的机器。
# 【重点】sys.path 可以手动改！往最前面塞一个目录，就能优先从那里导入。

demo_dir = tempfile.mkdtemp(prefix="pydemo_")     # 建个临时目录，当「模块仓库」
print(f"\n临时目录名以 pydemo_ 开头：{os.path.basename(demo_dir).startswith('pydemo_')}")
print(f"加入前，它在 sys.path 里吗：{demo_dir in sys.path}")

sys.path.insert(0, demo_dir)                       # insert(0) = 插队，优先级最高
print(f"加入后，它在 sys.path 里吗：{demo_dir in sys.path}")

# 输出：
# 临时目录名以 pydemo_ 开头：True
# 加入前，它在 sys.path 里吗：False
# 加入后，它在 sys.path 里吗：True
# 【重点】insert(0, 路径) 是插队，append(路径) 是排最后；插队意味着它能覆盖
#         标准库模块——这就是知识点 7 的坑。


# ==============================================================================
# 知识点 6：亲手写一个模块并导入它，验证 __name__ 的两种身份
# ==============================================================================
#
# 【讲解】光 import 标准库没意思，真刀真枪写一个：在临时目录里创建
#   greet.py，再 import 它，观察 __name__ 到底变成了什么。
# 【注意】写文件必须指定 encoding="utf-8"，否则 Windows 中文可能报编码错误。

greet_source = '''"""一个演示用的问候模块。"""
print(f"[模块顶层代码执行] 我的 __name__ = {__name__}")

VERSION = "1.0.0"                       # 模块级常量


def hello(name):
    """返回一句问候语。"""
    return f"你好，{name}！"


if __name__ == "__main__":
    print("这句只在直接运行 greet.py 时出现")
'''

greet_path = os.path.join(demo_dir, "greet.py")        # 拼出完整路径
with open(greet_path, "w", encoding="utf-8") as f:     # 写文件，指定 utf-8
    f.write(greet_source)

print("\n--- 导入自己写的模块 ---")
import greet                                           # 这一步会执行 greet 顶层代码！

print(f"greet.VERSION        = {greet.VERSION}")
print(f"greet.hello('小明')  = {greet.hello('小明')}")
print(f"greet 的 __name__    = {greet.__name__}")
print(f"greet 对应的文件名   = {os.path.basename(greet.__file__)}")

from greet import hello as greet_hello                 # 只导入里面的函数，也能用

print(f"单独导入的 hello('小红') = {greet_hello('小红')}")

# 输出：
# --- 导入自己写的模块 ---
# [模块顶层代码执行] 我的 __name__ = greet
# greet.VERSION        = 1.0.0
# greet.hello('小明')  = 你好，小明！
# greet 的 __name__    = greet
# greet 对应的文件名   = greet.py
# 单独导入的 hello('小红') = 你好，小红！
#
# 【重点】看第一行：被导入时 __name__ 是 "greet"（模块名），不是 "__main__"，
#         所以 greet.py 里 `if __name__ == "__main__"` 内的 print 没执行。
# 【重点】后面的 from greet import hello 没有再打印 "[模块顶层代码执行]"，
#         因为 greet 已在 sys.modules 里了（知识点 3）。
# 【注意】如果 import 那行报 ModuleNotFoundError，说明 demo_dir 没进 sys.path。


# ==============================================================================
# 知识点 7：模块名千万别和标准库重名！—— 命名遮蔽
# ==============================================================================
#
# 【讲解】如果你在项目里建了个 random.py，那 `import random` 会先找到
#   「你的 random.py」而不是标准库的。这叫「命名遮蔽（shadowing）」：
#   标准库突然失灵，报错还离奇。
# 【为什么】sys.path 从上往下找、找到就停，而 sys.path[0] 永远是你的脚本
#   目录、优先级最高。下面用子进程真实验证（不污染本文件的环境）。

print("\n--- 与标准库重名的危险 ---")
shadow_dir = tempfile.mkdtemp(prefix="shadow_")                 # 另一个临时目录
shadow_file = os.path.join(shadow_dir, "random.py")             # 故意叫 random.py
with open(shadow_file, "w", encoding="utf-8") as f:             # 写一个冒牌 random
    f.write('print("我是本地的 random.py，把标准库 random 顶掉了！")\n')

demo_code = "import random, os; print('实际导入的文件：' + os.path.basename(random.__file__))"
result = subprocess.run(
    [sys.executable, "-c", demo_code],   # -c：直接执行一段代码字符串
    cwd=shadow_dir,                      # 关键：工作目录设为放着冒牌 random.py 的地方
    capture_output=True,                 # 把输出抓回来，而不是打到屏幕上
    text=True,                           # 按文本返回（不是 bytes）
    encoding="utf-8",                    # 指定编码，避免 Windows 中文乱码
)

print("子进程的输出：")
print(result.stdout.strip())
print(f"标准库里有 random 吗：{'random' in sys.stdlib_module_names}")
print(f"标准库里有 my_tool 吗：{'my_tool' in sys.stdlib_module_names}")

# 输出：
# --- 与标准库重名的危险 ---
# 子进程的输出：
# 我是本地的 random.py，把标准库 random 顶掉了！
# 实际导入的文件：random.py
# 标准库里有 random 吗：True
# 标准库里有 my_tool 吗：False
#
# 【重点】`实际导入的文件：random.py` 说明导入的是假货，此时代码里调
#         random.randint() 会直接 AttributeError 崩掉。
# 【常见错误】新手常起的危险文件名：random.py  json.py  math.py  time.py
#       string.py  types.py  email.py  urllib.py  test.py（会干扰 pytest 收集）
#   【记法】起名前先查 '名字' in sys.stdlib_module_names，True 就换名字。


# ==============================================================================
# 知识点 8：清理现场 —— 从 sys.modules 卸载、删除临时目录
# ==============================================================================
#
# 【讲解】教学代码要有始有终：临时目录用完要删，sys.modules 里塞的假模块
#   也要清掉，否则会影响后续代码。真实项目很少手动清 sys.modules，
#   这里只为教学干净，但「用完临时文件要删」必须养成习惯。
#
# 【重点】`sys.modules.pop("greet", None)` 是安全写法：不给默认值时会抛 KeyError。

print("\n--- 清理 ---")
print(f"清理前，'greet' 在 sys.modules 里吗：{'greet' in sys.modules}")

sys.modules.pop("greet", None)      # 第二个参数是默认值：不存在也不报错
print(f"清理后，'greet' 在 sys.modules 里吗：{'greet' in sys.modules}")

if demo_dir in sys.path:
    sys.path.remove(demo_dir)       # 移除刚才插队的目录
print(f"临时目录还在 sys.path 里吗：{demo_dir in sys.path}")

# ignore_errors=True：删不掉也不报错（防 Windows 文件被占用导致报错）
shutil.rmtree(demo_dir, ignore_errors=True)
shutil.rmtree(shadow_dir, ignore_errors=True)
print(f"临时目录还存在吗：{os.path.exists(demo_dir)}")

# 输出：
# --- 清理 ---
# 清理前，'greet' 在 sys.modules 里吗：True
# 清理后，'greet' 在 sys.modules 里吗：False
# 临时目录还在 sys.path 里吗：False
# 临时目录还存在吗：False


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 一个 .py 文件 = 一个模块；模块名 = 文件名去掉 .py（区分大小写）
# 2. 模块分三类：内置模块（无 __file__）、标准库、第三方库
# 3. 四种导入写法：import 模块 / from 模块 import 名字 / as 别名 / import *
#    → 推荐前两种；import * 会污染命名空间、悄悄覆盖变量
# 4. as 别名两个用途：名字太长（numpy as np）、避免重名冲突
# 5. 模块只加载一次，缓存存在 sys.modules；重复 import 不执行代码
# 6. 直接运行时 __name__ == "__main__"；被导入时 __name__ == 模块名，
#    if __name__ == "__main__": 让模块「既能被导入又能被直接运行」
# 7. sys.path 是模块搜索地址簿，顺序：脚本目录 → PYTHONPATH → 标准库 → 第三方库
# 8. sys.path.insert(0, 目录) 能插队，但也可能造成命名遮蔽
# 9. 千万别用标准库的名字给文件命名（random.py / json.py 是大坑）


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：新建 mymath.py，写 add / sub / mul / div 四个函数；
#         再新建 main.py，用 from mymath import add 调用它们。
#         并给 mymath.py 加上 if __name__ == "__main__": 块写自测代码，
#         然后分别「直接运行」和「被导入」，观察自测代码何时执行。
# 练习 2：写脚本打印 sys.path 每一项，并标注它是否存在（os.path.exists）。
# 练习 3：故意建一个空的 json.py，在同目录运行 import json; json.dumps({})，
#         抄下报错信息；再删掉重跑，体会命名遮蔽的破坏力。
#
# 【下一步】02_包与项目结构.py
# ==============================================================================
