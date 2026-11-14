"""
================================================================================
第 7 章 · 高阶函数
文件 01：函数作为参数
================================================================================

【学习目标】
    1. 理解「函数也是对象」，可以像数字、字符串一样被传递
    2. 学会把函数作为参数传给另一个函数
    3. 理解回调模式：先约定好「事情做完之后调用谁」
    4. 学会让函数返回另一个函数
    5. 能看懂 map / filter / sorted 等内置函数为什么要接收函数

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 01_函数作为参数.py

【前置知识】
    - 第 3 章：def 定义函数、参数、返回值
    - 第 4 章：列表、元组的基本操作
================================================================================
"""

# ==============================================================================
# 知识点 1：函数也是对象
# ==============================================================================
#
# 在很多语言里，「函数」和「数据」是两种东西。
# 但在 Python 里，函数是「一等公民」（first-class citizen）：
#
#   它可以被赋值给变量、放进列表、当成参数传、当成返回值返回。
#
# 【类比】函数就像一张「菜谱」：
#   - 菜谱本身不是菜，但它是一样实实在在的东西，可以递给别人
#   - 你可以把菜谱放进抽屉（列表），也可以把菜谱交给厨师（传参）
#   - 只有「照着菜谱做菜」时，才会真正产生一道菜（调用函数）

def greet(name):
    return f"你好，{name}！"


# 注意：这里写 greet，不带括号。带括号是「调用」，不带括号才是「函数本身」
print("greet 的类型：", type(greet))
print("greet 的名字：", greet.__name__)
print("调用 greet('小明')：", greet("小明"))

# 把函数赋值给另一个变量：两个名字指向同一个函数对象
alias = greet
print("通过别名调用：", alias("小红"))
print("alias 和 greet 是同一个对象吗？", alias is greet)

# 输出：
# greet 的类型： <class 'function'>
# greet 的名字： greet
# 调用 greet('小明')： 你好，小明！
# 通过别名调用： 你好，小红！
# alias 和 greet 是同一个对象吗？ True
#
# 【重点】greet 是函数对象本身，greet() 才是执行它并拿到返回值。
#         后面所有「把函数当参数传」的写法，传的都是不带括号的函数对象。

# 函数还可以放进列表、元组、字典里，像普通数据一样管理
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


# 列表里存的是「操作名 + 函数对象」的组合
operations = [("加法", add), ("减法", subtract), ("乘法", multiply)]

for name, operation in operations:
    # operation 是函数对象，operation(10, 3) 才是调用
    print(f"10 {name} 3 = {operation(10, 3)}")

# 输出：
# 10 加法 3 = 13
# 10 减法 3 = 7
# 10 乘法 3 = 30
#
# 【为什么】列表可以装任何对象，函数对象也不例外。
#         这就是「插件式」设计的雏形：主流程不变，具体操作可以换。


# ==============================================================================
# 知识点 2：什么是高阶函数
# ==============================================================================
#
# 【定义】满足下面任意一条的函数，就叫「高阶函数」：
#   1. 接收一个或多个函数作为参数
#   2. 返回一个函数作为结果
#
# 【类比】高阶函数像「洗衣机」：
#   你放进衣服（数据），还要选择「洗涤模式」（函数）。
#   机器本身不变，但换个模式，处理结果就完全不同。
#
# 先看一个最小的例子：把同一个操作连续做两次。

def apply_twice(func, value):
    """把 func 连续作用两次：先算 func(value)，再对结果算一次。"""
    return func(func(value))


def add_one(x):
    return x + 1


def double(x):
    return x * 2


print("对 5 连续加 1 两次：", apply_twice(add_one, 5))
print("对 5 连续乘 2 两次：", apply_twice(double, 5))

# 输出：
# 对 5 连续加 1 两次： 7
# 对 5 连续乘 2 两次： 20
#
# 【重点】apply_twice 自己并不知道「加一」或「乘二」怎么做。
#         它只负责「做两次」这个流程，具体做什么由传进来的函数决定。
#         这就是「把变化的部分抽出去」——流程复用，行为可配置。

# 再看一个更实用的版本：对列表里的每个元素做同一种变换

def transform_all(items, func):
    """遍历 items，对每个元素调用 func，收集结果。"""
    result = []
    for item in items:
        result.append(func(item))     # func 是一个「加工机」
    return result


def square(x):
    return x * x


def negate(x):
    return -x


numbers = [1, 2, 3, 4, 5]
print("平方：", transform_all(numbers, square))
print("取负：", transform_all(numbers, negate))

# 输出：
# 平方： [1, 4, 9, 16, 25]
# 取负： [-1, -2, -3, -4, -5]
#
# 【注意】这里没有写两遍循环，只写了一遍 transform_all。
#         文件 03 的 map() 其实就是这个函数的内置版本。


# ==============================================================================
# 知识点 3：回调模式 —— 「做完之后记得叫我」
# ==============================================================================
#
# 【回调】callback：把「将来要被调用的函数」提前交给别人，
#   等某件事发生时，再由别人来调用它。
#
# 【类比】你在餐厅点完餐，留给服务员一个手机号（回调函数）。
#   你不需要站在厨房门口等；餐做好了，服务员会打给你。
#
#   do_homework(任务, 完成后的通知方式)
#   主流程只知道「完成后要调用 on_finish」，至于通知谁、怎么通知，由调用者决定。

def do_homework(task, on_finish):
    print(f"开始：{task}")
    result = f"{task}完成"
    on_finish(result)         # 事情做完了，调用传进来的回调


def send_notification(message):
    print(f"  [通知] {message}")


def write_log(message):
    print(f"  [日志] {message}")


do_homework("数学作业", send_notification)
do_homework("数学作业", write_log)

# 输出：
# 开始：数学作业
#   [通知] 数学作业完成
# 开始：数学作业
#   [日志] 数学作业完成
#
# 【重点】同一个 do_homework，换上不同的回调，就得到不同的后续行为。
#         主流程不需要知道「通知」和「日志」的区别，耦合度更低。

# 回调在图形界面里非常常见：按钮被点击时，执行哪个函数？
# 下面用 print 模拟一个按钮点击系统

def on_click(button_name, callback):
    print(f"[系统] 用户点击了「{button_name}」")
    callback(button_name)     # 把按钮名字回传给处理函数


def play_music(button):
    print(f"  → 播放音乐（来自「{button}」按钮）")


def open_settings(button):
    print(f"  → 打开设置（来自「{button}」按钮）")


on_click("播放", play_music)
on_click("设置", open_settings)

# 输出：
# [系统] 用户点击了「播放」
#   → 播放音乐（来自「播放」按钮）
# [系统] 用户点击了「设置」
#   → 打开设置（来自「设置」按钮）
#
# 【类比】按钮本身不知道点下去该干什么，它只负责「被点击」这个事件；
#         具体做什么，是创建按钮的人通过 callback 交给它的。

# ==============================================================================
# 知识点 4：函数作为返回值 —— 生产函数的「工厂」
# ==============================================================================
#
# 既然函数是对象，它当然也能被 return 出去。
# 这种「返回函数」的函数，可以理解成一个「函数工厂」：
# 你给它一些配置，它还给你一个已经配好的专用函数。
#
# 【类比】make_multiplier(3) 就像在工厂里定制一台「三倍放大器」：
#   工厂参数 factor=3 被记住了，以后这台机器见到任何数都乘以 3。

def make_multiplier(factor):
    def multiply(x):
        return x * factor        # factor 来自外层，被内层记住了
    return multiply              # 注意：返回的是函数本身，不是调用结果


triple = make_multiplier(3)
ten_times = make_multiplier(10)

print("3 倍：", triple(7))
print("10 倍：", ten_times(7))
print("triple 的类型：", type(triple))

# 输出：
# 3 倍： 21
# 10 倍： 70
# triple 的类型： <class 'function'>
#
# 【重点】triple 和 ten_times 是两个不同的函数，各自记住了不同的 factor。
#         这种「记住外层变量」的能力，就是文件 05 要讲的闭包。

# 再做一个问候语工厂：把「问候词」提前存进返回的函数里
def make_greeting(greeting):
    def say(name):
        return f"{greeting}，{name}！"
    return say


hello = make_greeting("你好")
morning = make_greeting("早上好")

print(hello("小明"))
print(morning("小红"))

# 输出：
# 你好，小明！
# 早上好，小红！
#
# 【重点】greeting 不是全局变量，但返回的 say 仍然能读到它。
#         这正是高阶函数和闭包配合的威力：行为 = 代码 + 被记住的配置。


# ==============================================================================
# 知识点 5：综合实战 —— 换一个格式化函数，就换一种报表
# ==============================================================================
#
# 需求：同一份学生数据，既要打印「成绩表」，也要打印「鼓励语」。
# 如果写两个函数，循环逻辑会重复；把「格式化」抽成参数，就能复用主流程。

def show_report(title, data, formatter):
    print(f"===== {title} =====")
    for item in data:
        print(formatter(item))    # 每一行长什么样，由 formatter 决定


def format_score(student):
    name, score = student
    return f"{name}：{score} 分"


def format_praise(student):
    name, score = student
    if score >= 90:
        return f"{name} 太棒了！"
    return f"{name} 继续加油！"


students = [("小明", 85), ("小红", 92)]

show_report("成绩表", students, format_score)
show_report("鼓励语", students, format_praise)

# 输出：
# ===== 成绩表 =====
# 小明：85 分
# 小红：92 分
# ===== 鼓励语 =====
# 小明 继续加油！
# 小红 太棒了！
#
# 【重点】show_report 负责「循环 + 标题」这些不变的部分，
#         formatter 负责「每一行怎么显示」这些会变的部分。
#         这就是很多框架里「模板方法」「插件」思想的朴素版本。


# ==============================================================================
# 知识点 6：常见错误 —— 传函数还是传函数的结果？
# ==============================================================================
#
# 【常见错误】把函数名后面的括号忘了 / 多加了。
#
#   正确：apply_twice(add_one, 5)     传的是「加一这个动作」
#   错误：apply_twice(add_one(1), 5)  传的是「加一之后的结果 2」
#
# 第二种写法里，apply_twice 拿到的是整数 2，却把它当函数调用，必然报错。

try:
    apply_twice(add_one(1), 5)
except TypeError as e:
    print("错误信息：", e)

# 输出：
# 错误信息： 'int' object is not callable
#
# 【注意】报错说「int 对象不可调用」，意思是「你让我调用一个整数」。
#         看到 not callable，先检查是不是把函数调用结果传进去了。

# 另一个高频错误：回调函数的参数个数对不上
def simple_callback():
    print("  [回调] 完成")


try:
    do_homework("语文作业", simple_callback)
except TypeError as e:
    print("错误信息：", e)

# 输出：
# 开始：语文作业
# 错误信息： simple_callback() takes 0 positional arguments but 1 was given
#
# 【为什么】do_homework 内部写的是 on_finish(result)，会传一个参数；
#         但 simple_callback 定义时没有参数，接不住。
#         写回调前要先看清楚：调用方会传几个参数、是什么含义。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. Python 的函数是对象：可以赋值、放进容器、当参数、当返回值
# 2. 函数名不带括号是「函数本身」，带括号才是「调用」
# 3. 高阶函数 = 接收函数作为参数，或返回一个函数
# 4. 回调模式：主流程在关键时刻调用预先传入的函数，实现行为可替换
# 5. 函数工厂：外层函数保存配置，返回一个已经「配好」的内层函数
# 6. map / filter / sorted 的 key 参数，都是「函数作为参数」的应用
# 7. 看到 not callable，先检查是不是把函数调用结果当函数传了


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写 apply_n(func, value, n)，把 func 连续作用 n 次
#         例如 apply_n(add_one, 0, 3) 应该得到 3
def apply_n(func,value,n):
    for i in range(n):
        func = func(func(value))
    return func
#
# 练习 2：写 make_discount(rate)，返回一个「打 rate 折」的函数
#         例如 eight_off = make_discount(0.8)，eight_off(100) 得到 80.0
def make_discount(rate):
    def discount(price):
        return price * rate
    return discount
half_off = make_discount(0.5)
print(half_off(200))  # 100.0
#
# 练习 3：写一个 check_score(score, rule) 函数，rule 是判断是否及格的函数；
#         分别传入「60 分及格」和「90 分优秀」两种规则，观察结果
#
# 练习 4：解释下面两行代码的区别（先自己想，再运行验证）：
#         print(greet)
#         print(greet("小明"))
#
# 【下一步】02_lambda表达式.py
# ==============================================================================
