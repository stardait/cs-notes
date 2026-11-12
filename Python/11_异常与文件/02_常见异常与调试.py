"""
================================================================================
第 11 章 · 异常与文件
文件 02：常见异常与调试
================================================================================

【学习目标】
    1. 认清 5 个最高频的异常：ValueError / TypeError / KeyError / IndexError /
       ZeroDivisionError，知道它们各自在什么情况下出现
    2. 学会「从下往上」读 Traceback，几秒定位报错行
    3. 掌握 assert 断言，并知道它为什么不能用来校验用户输入
    4. 会用 traceback 模块把完整错误信息写进日志

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 报错信息不用背，混个脸熟就行，见到能认出来
    - 「输出」块是运行后的实际结果
    - 直接运行：python 02_常见异常与调试.py

【前置知识】
    - 文件 01：try / except / else / finally 的用法
================================================================================
"""

import traceback                       # 标准库：格式化 Traceback（知识点 7 用）

# ==============================================================================
# 知识点 1：五大常见异常速查
# ==============================================================================
#
# 【讲解】新手 90% 的报错都落在这几个里，先把它们的样子认熟：
#
#   异常类型             典型触发场景              一句话记忆
#   ------------------   -----------------------   ------------------------
#   ValueError           int("abc")                类型对，但值不对
#   TypeError            "abc" + 1                 类型根本不对
#   KeyError             {"a": 1}["b"]             字典里没这个键
#   IndexError           [1, 2, 3][10]             列表没这个位置
#   ZeroDivisionError    10 / 0                    除以零
#   AttributeError       None.upper()              这个对象没这个属性
#
# 【类比】TypeError 是「让收银员称重，你递过去一张身份证」—— 东西不对；
#   ValueError 是「你递过去一袋苹果，但秤上只收硬币」—— 类别对、内容不对。
#
# 【重点】这张表不用背：看到报错先看最后一行，回来对一下就知道大概是什么问题。

print("=== 1. 五大常见异常速查 ===")

# 把「会出错的一行」包成 lambda 放进列表，统一点火观察（lambda 见第 7 章）
cases = [
    ("int('abc')", lambda: int("abc")),           # 想转整数，但内容是字母
    ("'abc' + 1", lambda: "abc" + 1),             # 字符串和整数相加
    ("{'a': 1}['b']", lambda: {"a": 1}["b"]),     # 取一个不存在的键
    ("[1, 2, 3][10]", lambda: [1, 2, 3][10]),     # 下标 10 超出范围
    ("10 / 0", lambda: 10 / 0),                   # 除数为零
    ("None.upper()", lambda: None.upper()),       # None 没有 upper 方法
]

for expr, action in cases:                        # 逐个执行，把异常信息收集起来
    try:
        action()                                  # 点火
    except Exception as e:                        # 这里只是演示，所以统一兜住
        print(f"  {expr}  →  {type(e).__name__}: {e}")

# 输出：
# === 1. 五大常见异常速查 ===
#   int('abc')  →  ValueError: invalid literal for int() with base 10: 'abc'
#   'abc' + 1  →  TypeError: can only concatenate str (not "int") to str
#   {'a': 1}['b']  →  KeyError: 'b'
#   [1, 2, 3][10]  →  IndexError: list index out of range
#   10 / 0  →  ZeroDivisionError: division by zero
#   None.upper()  →  AttributeError: 'NoneType' object has no attribute 'upper'
#
# 【注意】这里用 `except Exception` 是「演示专用」写法。真实项目要抓具体类型，否则你分不清到底出了哪种错（01 号文件讲过原因）。


# ==============================================================================
# 知识点 2：ValueError 与 TypeError —— 最容易混的一对
# ==============================================================================
#
# 【讲解】TypeError 是「种类」就不对（字符串拿去和数字相加）；ValueError 是
#   「种类对了、内容不合法」（int() 要字符串，你给了 "abc"）。
#
# 【重点】int("12.5") 会抛 ValueError，不会帮你截断成 12；要小数请用 float()。
# 【重点】TypeError 几乎总是「代码写错了」：用户输入永远是字符串，如果 TypeError
#   出现在输入路径上，说明你少做了一次类型转换 —— 该修代码，不是用 except 藏起来。
#
# 【处理思路】要么「先检查再转」（text.isdigit()），要么「请求原谅」（直接转，
#   出错再 except）。后者在 Python 圈更常见，叫 EAFP：先干，出问题再补救。

print("\n--- 2. ValueError 与 TypeError ---")

try:
    int("12.5")                        # 想转整数，但带了小数点
except ValueError as e:
    print("  int('12.5') 报错：", e)

for expr, action in [
    ("'abc' + 1", lambda: "abc" + 1),  # 字符串不能和整数相加
    ("len(123)", lambda: len(123)),    # 整数没有长度
    ("'a' - 'b'", lambda: "a" - "b"),  # 字符串不支持减法
]:
    try:
        action()                       # 逐个点火
    except TypeError as e:
        print(f"  {expr}  →  {e}")

# 输出：
# --- 2. ValueError 与 TypeError ---
#   int('12.5') 报错： invalid literal for int() with base 10: '12.5'
#   'abc' + 1  →  can only concatenate str (not "int") to str
#   len(123)  →  object of type 'int' has no len()
#   'a' - 'b'  →  unsupported operand type(s) for -: 'str' and 'str'
#
# 【补充】isinstance(True, int) 的结果是 True —— 因为 bool 是 int 的子类。
#   所以判断类型别写 type(x) == int，用 isinstance(x, int) 更稳。


# ==============================================================================
# 知识点 3：KeyError 与 IndexError —— 一对「找不到」兄弟
# ==============================================================================
#
# 【讲解】KeyError：d[key] 的键不存在；IndexError：lst[i] 的下标越界。
#   它俩共同的父类是 LookupError，都是「按名字/位置找东西，没找到」。
#
# 【KeyError 的三个安全写法】d.get(key) 返回 None；d.get(key, 默认值) 最常用；
#   if key in d: 先问一句「有没有」。
#
# 【IndexError 的细节】合法下标是 0 ~ len-1，负数从后往前数（-1 是最后一个，
#   -4 就越界了，不是循环取）；切片越界不报错，只给到末尾为止 —— 因为切片的
#   意思是「要一段」，给多少算多少，而 lst[100] 的意思是「就要第 100 个」。
#
# 【注意】KeyError 的消息带引号：KeyError: 'b'，因为它把「键的 repr」当消息。

print("\n--- 3. KeyError 与 IndexError ---")

scores = {"Alice": 90, "Bob": 85}

try:
    print("  直接取 Carol 的成绩：", scores["Carol"])   # 键不存在 → KeyError
except KeyError as e:
    print("  KeyError：", e, " ← 注意引号，这是键的 repr")

print("  get('Carol')      =", scores.get("Carol"), " ← 返回 None")
print("  get('Carol', 0)   =", scores.get("Carol", 0), " ← 返回默认值 0")
print("  'Carol' in scores =", "Carol" in scores, " ← 先判断就不会崩")

names = ["Alice", "Bob", "Carol"]
try:
    print("  names[10] =", names[10])          # 只有 3 个元素，下标 10 越界
except IndexError as e:
    print("  names[10] 报错：", e)

print("  names[-1] =", names[-1], " ← 负数从后往前数，-1 是最后一个")
print("  names[1:100] =", names[1:100], " ← 切片越界不报错，取到末尾为止")

# 输出：
# --- 3. KeyError 与 IndexError ---
#   KeyError： 'Carol'  ← 注意引号，这是键的 repr
#   get('Carol')      = None  ← 返回 None
#   get('Carol', 0)   = 0  ← 返回默认值 0
#   'Carol' in scores = False  ← 先判断就不会崩
#   names[10] 报错： list index out of range
#   names[-1] = Carol  ← 负数从后往前数，-1 是最后一个
#   names[1:100] = ['Bob', 'Carol']  ← 切片越界不报错，取到末尾为止


# ==============================================================================
# 知识点 4：ZeroDivisionError 与 AttributeError
# ==============================================================================
#
# 【ZeroDivisionError】10 / 0、10 // 0、10 % 0 全都会抛；连 10.0 / 0 也一样。
#   它不会给你 inf 或 nan —— 这点和 C / JavaScript 不同（那边 1/0 得 Infinity）。
#
# 【AttributeError】用 .xxx 访问对象上不存在的东西时抛出。新手重灾区是在 None
#   上调用方法：data = get_data() 没拿到东西，data.upper() 立刻炸。根因十有八九
#   是某个函数「忘了 return」—— 函数不写 return 时默认返回 None。排查口诀：看到
#   'NoneType' object has no attribute ... 别急着改这一行，往上查变量为什么是 None。
#
# 【类比】除零是「叫你把披萨分给 0 个人」，逻辑上没法做；AttributeError 是
#   「让一只猫去拉小提琴」—— 它没这个能力。

print("\n--- 4. ZeroDivisionError 与 AttributeError ---")

for expr, action in [
    ("10 / 0", lambda: 10 / 0),
    ("10 // 0", lambda: 10 // 0),
    ("10 % 0", lambda: 10 % 0),
    ("10.0 / 0", lambda: 10.0 / 0),
]:
    try:
        action()
    except ZeroDivisionError as e:
        print(f"  {expr}  →  {type(e).__name__}: {e}")


def safe_average(total, count):
    """求平均分；count 为 0 时返回 0，避免除零。"""
    if count == 0:                      # 提前判断，比 try 更直白
        print("  没有任何数据，平均分记为 0")
        return 0
    return total / count


print("  safe_average(270, 3) =", safe_average(270, 3))
print("  safe_average(0, 0)   =", safe_average(0, 0))


def find_name(key):
    """查名字：查不到就什么都不返回（也就是返回 None）。"""
    return {"a": "Alice"}.get(key)      # 查不到返回 None


result = find_name("b")                 # 得到 None
print("  find_name('b') 的结果：", result)
try:
    print(result.upper())               # ❌ 在 None 上调用 upper()
except AttributeError as e:
    print("  报错：", e)

# 输出：
# --- 4. ZeroDivisionError 与 AttributeError ---
#   10 / 0  →  ZeroDivisionError: division by zero
#   10 // 0  →  ZeroDivisionError: division by zero
#   10 % 0  →  ZeroDivisionError: division by zero
#   10.0 / 0  →  ZeroDivisionError: division by zero
#   safe_average(270, 3) = 90.0
#   没有任何数据，平均分记为 0
#   safe_average(0, 0)   = 0
#   find_name('b') 的结果： None
#   报错： 'NoneType' object has no attribute 'upper'


# ==============================================================================
# 知识点 5：学会读 Traceback —— 从下往上读
# ==============================================================================
#
# 【讲解】报错时屏幕上的那一大坨叫 Traceback，读它的顺序是「从下往上」：
#
#   Traceback (most recent call last):          ← 下面是调用链的开头
#     File "app.py", line 30, in <module>       ← 最外层：你直接写的那一句
#       main()
#     File "app.py", line 12, in main           ← 中间层
#       load()
#     File "app.py", line 8, in load            ← 最内层：真正出事的位置
#       int("abc")
#   ValueError: invalid literal for int() ...   ← 最后一行：什么错、为什么错
#
#   ✔ 最后一行   = 错误类型 + 错误消息（先看这行）
#   ✔ 倒数第二段 = 真正出错的那一行代码
#   ✔ 中间那些   = 调用链（谁调了谁），行号能点进编辑器跳转
#
# 【常见错误】只盯着最后一行去搜「invalid literal」，却不知道该改哪个文件哪一行。
#
# 下面用代码把「调用链」和「出错的那一行」提取出来：

print("\n--- 5. 读 Traceback ---")


def parse_port(text):
    return int(text)


def read_config():
    return parse_port("abc")            # 这里调用 parse_port


try:
    read_config()                       # 从最外层点火
except ValueError as e:
    frames = traceback.extract_tb(e.__traceback__)    # 取出调用栈的每一帧
    print("  调用链（从外到内）：", " → ".join(f.name for f in frames))
    print("  出错位置：", f"{frames[-1].name}() 里的 `{frames[-1].line}`")
    print("  错误类型：", type(e).__name__)
    print("  错误信息：", e)

# 输出：
# --- 5. 读 Traceback ---
#   调用链（从外到内）： <module> → read_config → parse_port
#   出错位置： parse_port() 里的 `return int(text)`
#   错误类型： ValueError
#   错误信息： invalid literal for int() with base 10: 'abc'
#
# 【看点】<module> 表示「模块顶层」，也就是你直接写在文件里的那几句。调用链告诉你：
#   main 流程 → read_config → parse_port，真正炸的是 int("abc")。


# ==============================================================================
# 知识点 6：assert 断言 —— 给「理论上不可能」加个保险
# ==============================================================================
#
# 【讲解】assert 是「我坚决认为这里一定成立」的声明：
#       assert 条件, "条件不成立时显示的消息"
#   条件为真：什么都不做；条件为假：抛 AssertionError，消息就是你写的那句话。
#   用途是开发期自检：检查「不该发生的事」有没有发生，帮你早点发现 bug。
#
# 【重点】assert 不是「错误处理」，是「调试工具」：用 `python -O 文件名.py`
#   运行时 Python 会把所有 assert 全部删掉！所以绝对不能用它校验用户输入 ——
#   用户加个 -O 就绕过了检查。判断法则：用户输入 → if + raise；内部逻辑 → assert。

print("\n--- 6. assert 断言 ---")


def average(numbers):
    assert isinstance(numbers, list), "参数必须是 list"     # 内部约定，用断言守
    assert len(numbers) > 0, "列表不能为空"                # 不让空列表漏进来
    return sum(numbers) / len(numbers)


print("  average([1, 2, 3]) =", average([1, 2, 3]))

try:
    average([])                         # 违反第二条断言
except AssertionError as e:
    print("  空列表触发断言：", e)

try:
    average((1, 2, 3))                  # 元组不是 list，违反第一条断言
except AssertionError as e:
    print("  传元组触发断言：", e)

# 输出：
# --- 6. assert 断言 ---
#   average([1, 2, 3]) = 2.0
#   空列表触发断言： 列表不能为空
#   传元组触发断言： 参数必须是 list
#
# 【常见错误】写成 assert (条件, "消息") —— 加了括号就变成「判断一个元组」，非空
#   元组永远为真，断言彻底失效。正确写法是逗号，不要括号：assert 条件, "消息"


# ==============================================================================
# 知识点 7：traceback 模块 —— 把完整错误信息留下来
# ==============================================================================
#
# 【讲解】`print(e)` 只有一句「invalid literal...」，看不到哪一行出错。要看全就用
#   traceback 模块：format_exc() 把完整 Traceback 变成字符串（写日志），print_exc()
#   直接打印到屏幕（默认 stderr）。
#
# 【重点】format_exc() 必须在 except 块里调用，因为它从「当前正在处理的异常」取信息。

print("\n--- 7. traceback 模块 ---")

try:
    int("abc")
except ValueError as e:
    text = traceback.format_exc()       # 拿到完整错误文本（字符串）
    lines = text.strip().splitlines()   # 按行切开方便观察
    print("  第一行：", lines[0])
    print("  最后一行：", lines[-1])
    only = traceback.format_exception_only(type(e), e)   # 只要「类型: 消息」那段
    print("  只要错误那行：", only[0].strip())
    print("  完整文本长度：", len(text), "个字符（真实项目里直接写进日志文件）")

# 输出：
# --- 7. traceback 模块 ---
#   第一行： Traceback (most recent call last):
#   最后一行： ValueError: invalid literal for int() with base 10: 'abc'
#   只要错误那行： ValueError: invalid literal for int() with base 10: 'abc'
#   完整文本长度： 212 个字符（真实项目里直接写进日志文件）
#
# 【注意】长度 212 和文件路径、行号有关，换台电脑就会变，不用纠结这个数字。
#   重点是：format_exc() 把「文件名 + 行号 + 代码 + 错误」全装进去了，
#   比 print(e) 有用得多 —— 写日志、上报错误都用它。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 五大高频异常：ValueError（值不对）/ TypeError（类型不对）/ KeyError（没这个键）
#    / IndexError（没这个位置）/ ZeroDivisionError（除以零）
# 2. ValueError 是「类别对、内容错」，TypeError 是「类别就错」；后者该修代码
# 3. int("12.5") 抛 ValueError，不会截断；要小数用 float()
# 4. 字典用 get(key, 默认值)，列表取值前用 len() 判断，能挡掉大半 Key/IndexError
# 5. 切片越界不报错，按下标取值才报 IndexError；负数下标在 -len 以内才合法
# 6. 浮点数除以 0 也抛 ZeroDivisionError，和 C/JS 的 Infinity 不一样
# 7. 'NoneType' object has no attribute → 往上查「谁返回了 None」
# 8. Traceback 从下往上读：最后一行是类型+消息，倒数第二段是出错代码
# 9. assert 是调试工具，`python -O` 会删掉它，不能用来校验用户输入
# 10. traceback.format_exc() 能拿到完整错误文本，写日志就用它


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写 to_int(text, default=0)，转换失败返回 default，分别测试
#         "42"、"abc"、"3.14"、"" 四个输入。
#
# 练习 2：写 get_score(scores, name)，用 get() 避免 KeyError，查不到返回「查无此人」。
#
# 练习 3：故意写一个三层函数调用（a 调 b，b 调 c，c 里除以零），运行后阅读
#         Traceback，指出「最后一行」和「真正出错的那一行」分别是哪句。
#
# 练习 4：用 traceback.format_exc() 捕获一个 KeyError，把完整文本存到变量里，
#         然后只打印其中「含有 File 字样的行」，看看能定位到什么信息。
#
# 【下一步】03_自定义异常.py
# ==============================================================================
