"""
================================================================================
第 7 章 · 高阶函数
文件 06：装饰器入门
================================================================================

【学习目标】
    1. 理解装饰器的原理：用「函数 + 闭包」包住另一个函数
    2. 看懂 @ 语法糖，知道它在什么时候执行
    3. 写出能接收任意参数、正确返回结果的装饰器
    4. 学会用 functools.wraps 保留原函数的身份信息
    5. 掌握带参数的装饰器（三层函数）
    6. 避开装饰器最常见的几个坑

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 06_装饰器入门.py

【前置知识】
    - 文件 01：函数作为参数、函数作为返回值
    - 文件 05：闭包、nonlocal
    - 第 3 章：*args / **kwargs
================================================================================
"""

# ==============================================================================
# 知识点 1：装饰器的原理 —— 给函数套一层「包装纸」
# ==============================================================================
#
# 需求：不修改 say_hello 的代码，在它执行前后各打印一行日志。
#
# 直觉做法是复制粘贴，但这样每加一个函数就要改一次。
# 更好的办法：写一个函数，接收原函数，返回一个「加强版」。
#
# 【类比】装饰器像给手机套保护壳：
#   手机还是那部手机（原函数没变），
#   但外壳多了防摔、支架等功能（额外的行为）。
#
# 【重点】装饰器本质上就是：
#   接收函数作为参数 + 在内部定义 wrapper + 返回 wrapper
#   这正是文件 01 和文件 05 学过的两件事的组合。

def logger(func):
    def wrapper():
        print(f"[日志] 开始执行 {func.__name__}")
        func()                          # 原函数在这里被调用
        print(f"[日志] {func.__name__} 执行结束")
    return wrapper                      # 返回加强版，不是调用结果


def say_hello():
    print("你好！")


logged_hello = logger(say_hello)
logged_hello()

# 输出：
# [日志] 开始执行 say_hello
# 你好！
# [日志] say_hello 执行结束
#
# 【重点】say_hello 本身没有被修改；logger 返回的是新的 wrapper 函数。
#   wrapper 之所以能调用 func，是因为它是个闭包，记住了传进来的 say_hello。


# ==============================================================================
# 知识点 2：@ 语法糖 —— 少写一行赋值
# ==============================================================================
#
# 每次都写 `f = logger(f)` 太啰嗦，Python 提供了 @ 语法：
#
#     @logger
#     def say_goodbye():
#         ...
#
# 完全等价于：
#
#     def say_goodbye():
#         ...
#     say_goodbye = logger(say_goodbye)
#
# 【重点】@ 不是「运行时自动帮你调用」，
#   它是在「定义函数的那一刻」把函数替换成 wrapper。

@logger
def say_goodbye():
    print("再见！")


say_goodbye()

# 输出：
# [日志] 开始执行 say_goodbye
# 再见！
# [日志] say_goodbye 执行结束

# 看清执行时机：装饰发生在定义时，wrapper 在调用时才运行
def trace(func):
    print(f"[定义时] 正在装饰 {func.__name__}")

    def wrapper():
        print(f"[调用时] 开始 {func.__name__}")
        func()
        print(f"[调用时] 结束 {func.__name__}")

    return wrapper


@trace
def work():
    print("  工作中...")


print("--- 装饰已完成，下面才开始调用 ---")
work()

# 输出：
# [定义时] 正在装饰 work
# --- 装饰已完成，下面才开始调用 ---
# [调用时] 开始 work
#   工作中...
# [调用时] 结束 work
#
# 【注意】「[定义时]」那行出现在最前面，因为 Python 执行到 @trace 时，
#   就已经调用 trace(work) 了；wrapper 内部的日志要等 work() 才打印。
#
# 【常见误区】以为 @ 会在每次调用时重新装饰。
#   实际上装饰只发生一次，之后 say_goodbye 这个名字一直指向 wrapper。


# ==============================================================================
# 知识点 3：让装饰器支持参数和返回值
# ==============================================================================
#
# 上面的 wrapper() 不接收参数，只能包装「无参数、无返回值」的函数。
# 真实函数往往有参数、有返回值，wrapper 必须原样转发：
#
#     def wrapper(*args, **kwargs):       接收任意参数
#         result = func(*args, **kwargs)  原样传给原函数
#         return result                   把结果原样返回
#
# 【重点】*args 和 **kwargs 是「万能接收器」，
#   wrapper 不需要知道原函数到底要几个参数，交给 func 去匹配。

def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}：args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"返回：{result}")
        return result
    return wrapper


@log_calls
def add(a, b): # type: ignore
    return a + b


print("最终结果：", add(3, 5))

# 输出：
# 调用 add：args=(3, 5), kwargs={}
# 返回：8
# 最终结果： 8

@log_calls
def introduce(name, age):
    return f"{name} 今年 {age} 岁"


print(introduce("小明", age=20))

# 输出：
# 调用 introduce：args=('小明',), kwargs={'age': 20}
# 返回：小明 今年 20 岁
# 小明 今年 20 岁
#
# 【重点】如果 wrapper 忘了写 return result，装饰后的函数就会返回 None。
#   这是装饰器最常见的 bug 之一，后面还会专门演示。


# ==============================================================================
# 知识点 4：functools.wraps —— 别把原函数的身份弄丢
# ==============================================================================
#
# 装饰之后，say_goodbye 这个名字其实指向 wrapper。
# 于是原函数的 __name__、__doc__ 都被 wrapper 覆盖了，调试时很误导。

from ast import arg
import functools
from unittest import result

from pymupdf import b


def plain_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@plain_decorator
def download():
    """下载文件。"""
    return "文件内容"


print("没加 wraps 的名字：", download.__name__)
print("没加 wraps 的文档：", download.__doc__)

# 输出：
# 没加 wraps 的名字： wrapper
# 没加 wraps 的文档： None
#
# 【为什么】download 已经被替换成 wrapper，
#   而 wrapper 没有文档字符串，名字也叫 wrapper。

# 正确做法：在 wrapper 上加 @functools.wraps(func)
def good_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@good_decorator
def upload():
    """上传文件。"""
    return "上传成功"


print("加了 wraps 的名字：", upload.__name__)
print("加了 wraps 的文档：", upload.__doc__)

# 输出：
# 加了 wraps 的名字： upload
# 加了 wraps 的文档： 上传文件。
#
# 【重点】functools.wraps 会把原函数的 __name__、__doc__ 等复制到 wrapper 上。
#   写装饰器时请默认加上它，否则日志、帮助文档、调试信息都会显示 wrapper。


# ==============================================================================
# 知识点 5：带参数的装饰器 —— 再套一层函数
# ==============================================================================
#
# 普通装饰器是「两层」：
#   logger(函数) → wrapper
#
# 带参数的装饰器需要「三层」：
#   repeat(参数) → decorator(函数) → wrapper
#
# 【类比】普通装饰器像买一个现成的手机壳；
#   带参数的装饰器像定制手机壳：先选颜色、刻字（参数），
#   工厂再按你的要求生产出那个壳（decorator），最后套到手机上。
#
# 【重点】@repeat(3) 的执行顺序是：
#   1. 先调用 repeat(3)，得到 decorator
#   2. 再用 decorator 装饰 cheer
#   3. 等价于 cheer = repeat(3)(cheer)

def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator


@repeat(3)
def cheer(name):
    return f"加油，{name}！"


print(cheer("小明"))

# 输出：
# ['加油，小明！', '加油，小明！', '加油，小明！']
#
# 【注意】三层缺一不可：
#   - repeat 负责接收「装饰器参数」
#   - decorator 负责接收「被装饰的函数」
#   - wrapper 负责「每次调用时真正执行的逻辑」


# ==============================================================================
# 知识点 6：常见错误
# ==============================================================================
#
# 【常见错误 1】忘了 return wrapper
#   这样 logger 返回 None，函数名会被替换成 None，调用时报 not callable。

def broken(func):
    def wrapper():
        return func()
    # 这里忘了写 return wrapper


def base():
    return 1


print("返回值：", broken(base))

# 输出：
# 返回值： None
#
# 【修正】在 broken 末尾补上 `return wrapper`。

# 【常见错误 2】wrapper 里忘了 return 原函数的结果
def silent(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)       # 调用了，但没接住返回值
    return wrapper


@silent
def get_price():
    return 99


print("价格：", get_price())

# 输出：
# 价格： None
#
# 【修正】写成 `return func(*args, **kwargs)`，或者先存 result 再 return。

# 【常见错误 3】wrapper 没有接收参数
def no_args(func):
    def wrapper():
        return func()
    return wrapper


@no_args
def add2(a, b):
    return a + b


try:
    add2(1, 2)
except TypeError as e:
    print("错误类型：", type(e).__name__)

# 输出：
# 错误类型： TypeError
#
# 【为什么】add2 已经是 wrapper，而 wrapper 不接收参数；
#   调用 add2(1, 2) 相当于给一个零参数函数传了两个参数。
#
# 【修正】wrapper 写成 `def wrapper(*args, **kwargs):`，
#   并调用 `func(*args, **kwargs)`。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 装饰器 = 接收函数 + 返回增强版函数，核心是闭包
# 2. @decorator 等价于 f = decorator(f)，在定义时执行一次
# 3. wrapper 要用 *args / **kwargs 转发参数，并 return 原函数的结果
# 4. functools.wraps 保留原函数的 __name__ 和 __doc__
# 5. 带参数的装饰器是三层：参数 → 函数 → wrapper
# 6. 忘记 return wrapper、忘记 return 结果、忘记接收参数，是最常见的三个坑
# 7. 装饰器适合加日志、计时、权限校验、重试等「横切关注点」


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写一个 timer 装饰器，在函数执行前后打印「开始 / 结束」
#         并用它装饰一个求和函数
def tst(func):
    def wrapper(*args, **kwargs):
        print("开始")
        result = func(*args, **kwargs)
        print(result)
        print("结束")
    return wrapper

def add(a, b):
    return a + b

star_1 = tst(add)
star_1(2, 3)
#
# 练习 2：写一个 ensure_positive 装饰器，如果函数返回负数就改成 0
#         提示：在 wrapper 里判断 result
#
# 练习 3：写一个带参数的装饰器 repeat(n)，让被装饰的函数连续执行 n 次，
#         返回所有结果组成的列表（参考知识点 5，但试着自己写一遍）
#
# 练习 4：给练习 1 的 timer 加上 functools.wraps，
#         比较加之前和加之后被装饰函数的 __name__
#
# 【下一步】第 8 章 · 递归：01_递归基础.py
# ==============================================================================
