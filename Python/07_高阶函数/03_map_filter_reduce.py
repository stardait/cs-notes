"""
================================================================================
第 7 章 · 高阶函数
文件 03：map、filter 与 reduce
================================================================================

【学习目标】
    1. 掌握 map：对每个元素做同一种变换
    2. 掌握 filter：按条件保留元素
    3. 理解 reduce：把一串值「压缩」成一个值
    4. 知道三者在 Python 3 里返回什么，为什么常常要 list()
    5. 能根据场景在 map/filter 和列表推导式之间做出选择

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 03_map_filter_reduce.py

【前置知识】
    - 文件 01：函数作为参数
    - 文件 02：lambda 表达式
    - 第 4 章：列表；第 5 章：字典
================================================================================
"""

# 先准备数据：一个数字列表，和一个「求平方」的函数
numbers = [1, 2, 3, 4, 5]


def square(x):
    return x * x


# ==============================================================================
# 知识点 1：map —— 对每个元素做变换
# ==============================================================================
#
# 需求：把列表里的每个数都平方。
# 不用 map 的话，要写「新建列表 → 遍历 → 调用 → 追加」四步模板：
#
#     squares = []
#     for n in numbers:
#         squares.append(square(n))
#
# 这个模式出现得太多，于是 Python 提供了 map：
#
#     语法：map(函数, 可迭代对象)
#
# 它会依次把每个元素传给函数，收集所有返回值。
#
# 【类比】map 像一条流水线：每个产品经过同一个工位，出来时都变了样。
#
# 【注意】Python 3 里 map 返回的是「迭代器」，不是列表！
#   迭代器是「懒」的：你不取，它就不算；而且只能取一次。

mapped = map(square, numbers)

print("map 的类型：", type(mapped))
print("转成列表：", list(mapped))

# 迭代器被取空之后，再取就是空列表
print("再取一次：", list(mapped))

# 输出：
# map 的类型： <class 'map'>
# 转成列表： [1, 4, 9, 16, 25]
# 再取一次： []
#
# 【重点】map 对象只能遍历一次。想看两次，就先存成列表：
#   squares = list(map(square, numbers))
#   之后随便用 squares。

# map + lambda：适合「只在这里用一次」的简单变换
names = ["alice", "bob", "carol"]
capitalized = list(map(lambda name: name.title(), names))
print("首字母大写：", capitalized)

# 如果已经有现成的函数，直接传函数名，比 lambda 更干净
print("用 str.title：", list(map(str.title, names)))

# 输出：
# 首字母大写： ['Alice', 'Bob', 'Carol']
# 用 str.title： ['Alice', 'Bob', 'Carol']
#
# 【为什么】str.title 是字符串类型上的方法，直接传它时，
#   map 会把每个字符串当成 self 传进去，效果和 name.title() 一样。

# map 可以同时处理多个可迭代对象：函数要接收对应个数的参数
prices = [10, 20, 30]
counts = [2, 3, 4]
subtotals = list(map(lambda price, count: price * count, prices, counts))
print("单价 × 数量：", subtotals)

# 长度不一致时，map 会在最短的那个耗尽时停止（不会报错！）
short = list(map(lambda a, b: a + b, [1, 2, 3], [10, 20]))
print("长度不一致：", short)

# 输出：
# 单价 × 数量： [20, 60, 120]
# 长度不一致： [11, 22]
#
# 【注意】长度不一致时不会报错，而是「悄悄截断」。
#   如果你以为会处理 3 个元素，结果只得到 2 个，这种 bug 很难发现。
#   需要严格配对时，先检查长度，或者用 zip(..., strict=True)（Python 3.10+）。

# map 也可以配合内置函数，代码短得几乎像一句英语
words = ["apple", "banana", "cherry"]
print("每个单词的长度：", list(map(len, words)))

# 输出：
# 每个单词的长度： [5, 6, 6]


# ==============================================================================
# 知识点 2：filter —— 按条件筛选
# ==============================================================================
#
# 语法：filter(判断函数, 可迭代对象)
#
# 判断函数（谓词）返回 True / False（或其他真值）。
# filter 只保留「判断为真」的元素，元素本身不会被改变。
#
# 【注意】filter 返回的也是迭代器，也要 list() 才能直接看。

def is_even(n):
    return n % 2 == 0


evens = filter(is_even, numbers)
print("filter 的类型：", type(evens))
print("只要偶数：", list(evens))
print("再取一次：", list(evens))

# 输出：
# filter 的类型： <class 'filter'>
# 只要偶数： [2, 4]
# 再取一次： []
#
# 【重点】filter 只负责「留不留」，不负责「改成什么」。
#   想既筛选又变换，通常 filter 和 map 组合使用，或者用列表推导式。

scores = [85, 42, 90, 58, 77]
passed = list(filter(lambda score: score >= 60, scores))
print("及格分数：", passed)

# 输出：
# 及格分数： [85, 90, 77]

# filter(None, ...) 是一个特殊用法：
# 传 None 作为判断函数时，会保留所有「真值」，丢掉所有「假值」。
mixed = [0, 1, "", "hi", None, [], [0], False, True]
truthy = list(filter(None, mixed))
print("所有真值：", truthy)

# 输出：
# 所有真值： [1, 'hi', [0], True]
#
# 【为什么】0、""、None、[]、False 在布尔上下文里都是 False；
#   而 [0] 是「非空列表」，所以它是 True——别被里面的 0 骗了。


# ==============================================================================
# 知识点 3：reduce —— 把一串值压成一个值
# ==============================================================================
#
# reduce 在 functools 模块里，使用前必须导入：
#     from functools import reduce
#
# 语法：reduce(函数, 可迭代对象[, 初始值])
#
# 它做的是「累积」：
#   1. 先取前两个元素，调用函数，得到一个中间结果
#   2. 把中间结果和第三个元素再传进函数
#   3. 重复，直到只剩一个结果
#
# 【注意】reduce 在 Python 3 里被移出了内置函数，因为大多数场景
#   用 sum / max / min / join 或普通循环更清楚。它仍然有用，但别滥用。

from functools import reduce

sum_numbers = reduce(lambda a, b: a + b, [1, 2, 3, 4, 5])
print("累加：", sum_numbers)

product = reduce(lambda a, b: a * b, [1, 2, 3, 4])
print("累乘：", product)

# 输出：
# 累加： 15
# 累乘： 24
#
# 【过程】累加的计算顺序是：
#   ((1 + 2) + 3) + 4) + 5
#   第一次 a=1, b=2 → 3
#   第二次 a=3, b=3 → 6
#   第三次 a=6, b=4 → 10
#   第四次 a=10, b=5 → 15

# 第三个参数是初始值：它会在第一次计算前被当作 a
with_initial = reduce(lambda a, b: a + b, [1, 2, 3], 100)
print("带初始值 100：", with_initial)

# 空序列没有初始值会报错
try:
    reduce(lambda a, b: a + b, [])
except TypeError as e:
    print("空序列报错：", e)

# 给了初始值就不会报错，直接返回初始值
empty_result = reduce(lambda a, b: a + b, [], 0)
print("空序列 + 初始值：", empty_result)

# 输出：
# 带初始值 100： 106
# 空序列报错： reduce() of empty iterable with no initial value
# 空序列 + 初始值： 0
#
# 【重点】reduce 不知道「空列表加起来应该是 0」；
#   你必须通过初始值告诉它。这和 sum([]) 自动返回 0 不一样。

# reduce 的顺序很关键：减法和加法不同，它是左结合的
print("10 - 2 - 3 =", reduce(lambda a, b: a - b, [10, 2, 3]))
print("100 起步再减：", reduce(lambda a, b: a - b, [10, 2, 3], 100))

# 输出：
# 10 - 2 - 3 = 5
# 100 起步再减： 85
#
# 【过程】第一行是 (10 - 2) - 3 = 5；
#   第二行是 ((100 - 10) - 2) - 3 = 85。
#   reduce 不会聪明地改变顺序，它永远从左往右折叠。

# 【重点】能直接用的内置函数，优先用内置函数：
#   sum(xs)、max(xs)、"".join(xs) 都比 reduce 更短、更快、更清楚。
#   reduce 留给「找不到现成函数」的累积逻辑。


# ==============================================================================
# 知识点 4：和列表推导式的对比
# ==============================================================================
#
# 列表推导式（list comprehension）是 Python 里更常用的写法：
#     [表达式 for 元素 in 可迭代对象 if 条件]
#
# 很多用 map / filter 能做的事，推导式也能做，而且往往更好读。

nums = [1, 2, 3, 4, 5]

# 逐项变换：两种写法
squares_map = list(map(lambda x: x * x, nums))
squares_comp = [x * x for x in nums]
print("map 结果：", squares_map)
print("推导式结果：", squares_comp)
print("两者相同吗？", squares_map == squares_comp)

# 输出：
# map 结果： [1, 4, 9, 16, 25]
# 推导式结果： [1, 4, 9, 16, 25]
# 两者相同吗？ True

# 变换 + 筛选：map + filter 嵌套
even_squares_map = list(
    map(lambda x: x * x, filter(lambda x: x % 2 == 0, nums))
)
print("map+filter：", even_squares_map)

# 同样的事情用推导式，一行就能读懂
even_squares_comp = [x * x for x in nums if x % 2 == 0]
print("推导式：    ", even_squares_comp)

# 输出：
# map+filter： [4, 16]
# 推导式：     [4, 16]
#
# 【重点】「变换 + 筛选」同时出现时，推导式通常更直观：
#   从左往右读就是「对每个 x，如果它是偶数，就取平方」。
#   map(filter(...)) 需要从里往外读，多了一层理解成本。

# 【建议】已有函数（float、len、str.strip）直接 map 很好；
#   要写 lambda 时，先想想推导式是不是更清楚。

# 一张选择表：
#
#   需求                              推荐
#   --------------------------------  ----------------------------
#   对每个元素套用已有函数            map
#   只按条件保留元素                  filter / 推导式的 if
#   既要变换又要筛选                  列表推导式
#   需要惰性、一次性的数据流          map / filter（不转列表）
#   同时遍历多个序列                  map 或 zip + 推导式
#   累积成一个值                      reduce / sum / max / join
#   逻辑复杂到一行写不下              普通 for 循环 + def


# ==============================================================================
# 知识点 5：综合实战 —— 订单数据处理
# ==============================================================================
#
# 需求：
#   1. 算出每个订单的小计（单价 × 数量）
#   2. 算出所有订单的总金额
#   3. 找出小计 >= 300 的订单

orders = [
    {"name": "键盘", "price": 199, "qty": 2},
    {"name": "鼠标", "price": 89, "qty": 1},
    {"name": "显示器", "price": 899, "qty": 1},
]

# 第一步：map 把每个订单变成一个小计
subtotals = list(map(lambda order: order["price"] * order["qty"], orders))
print("各订单小计：", subtotals)

# 第二步：reduce 把所有小计加起来
total = reduce(lambda acc, subtotal: acc + subtotal, subtotals, 0)
print("总金额：", total)

# 第三步：filter 挑出大额订单，再用列表推导式取名字
big_orders = list(filter(lambda order: order["price"] * order["qty"] >= 300, orders))
print("大额订单：", [order["name"] for order in big_orders])

# 输出：
# 各订单小计： [398, 89, 899]
# 总金额： 1386
# 大额订单： ['键盘', '显示器']
#
# 【解读】
#   键盘：199 × 2 = 398，不小于 300，保留
#   鼠标：89 × 1 = 89，小于 300，过滤掉
#   显示器：899 × 1 = 899，保留
#
# 【重点】这段代码里 map / filter / reduce 各司其职：
#   变换用 map，筛选用 filter，汇总用 reduce。
#   每一步的中间结果都打印出来，出问题时容易定位。


# ==============================================================================
# 知识点 6：常见错误
# ==============================================================================
#
# 【常见错误 1】把 filter 当成 map 用，以为它会「改变」元素
not_doubled = list(filter(lambda n: n * 2, [1, 2, 3, 4]))
print("filter 里乘 2 的结果：", not_doubled)

# 输出：
# filter 里乘 2 的结果： [1, 2, 3, 4]
#
# 【为什么】lambda 返回的 2、4、6、8 都被当成「真值」，
#   所以每个元素都被保留，但元素本身根本没变。
#   要变换请用 map，要筛选请让判断函数返回 True / False。

# 【常见错误 2】对空序列用 reduce 且不给初始值
try:
    reduce(lambda a, b: a + b, [])
except TypeError as e:
    print("空序列错误：", e)

# 输出：
# 空序列错误： reduce() of empty iterable with no initial value
#
# 【修正】要么给初始值，要么先用 if 判断序列是否为空。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. map(函数, 序列)：对每个元素做变换，返回迭代器
# 2. filter(判断函数, 序列)：保留判断为真的元素，返回迭代器
# 3. reduce(函数, 序列[, 初始值])：从左往右累积成一个值，需要导入
# 4. Python 3 的 map / filter 是惰性迭代器，只能遍历一次
# 5. filter 只筛选不修改；想修改元素要用 map
# 6. reduce 空序列且无初始值会 TypeError；sum/max/join 通常更合适
# 7. 变换 + 筛选同时出现时，列表推导式通常更易读
# 8. 多序列 map 在最短序列结束时停止，不会报错
# 9. 选择顺序：内置函数 > 推导式 > map/filter > 手写循环（按可读性权衡）


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：用 map 把 ["1", "2", "3"] 转成整数列表
#         再用 reduce 求它们的和
#
# 练习 2：用 filter 从 1~30 中筛出「能被 3 整除」的数
#         然后用 map 把它们都平方，最后打印结果
#
# 练习 3：把下面这段代码改写成列表推导式，比较哪种更好读：
#         result = list(map(lambda x: x * 10, filter(lambda x: x > 0, nums)))
#
# 练习 4：用 reduce 求 [2, 3, 4] 的连乘，再给它加一个初始值 5，
#         观察结果如何变化，并解释原因
#
# 【下一步】04_sorted与key.py
# ==============================================================================
