"""
================================================================================
第 10 章 · 迭代器与生成器
文件 04：生成器进阶
================================================================================

【学习目标】
    1. 用生成器表示「无限序列」，并学会安全地取用
    2. 掌握 itertools 里的常用工具（count / cycle / islice / chain / groupby ...）
    3. 理解 yield from：把子生成器的产出「转发」出去
    4. 用生成器搭「管道式」数据处理流水线

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 04_生成器进阶.py

【前置知识】
    文件 02（yield / send / 生成器状态）、文件 03（生成器表达式）
    —— 本文件是它们的组合应用，会大量用到惰性求值
================================================================================
"""

# ==============================================================================
# 知识点 1：无限序列 —— 生成器最擅长的场景
# ==============================================================================
#
# 列表不可能无限长（内存有限），但生成器可以「按需生产，永不结束」。
# 因为生成器只在被 next() 时才算下一个值，没被要的部分根本不存在。
#
# 【重点】无限序列必须配合「限制条件」使用：
#         islice()、takewhile()、break、或者手写计数。
#         千万不要对它用 list()，会卡死。

import itertools


def natural_numbers():
    """自然数序列：1, 2, 3, ... 永远不停"""
    n = 1
    while True:                     # 无限循环，但每次 yield 都暂停
        yield n
        n += 1


def fibonacci():
    """斐波那契数列：0, 1, 1, 2, 3, 5, 8, ..."""
    a, b = 0, 1
    while True:
        yield a                     # 交出当前的 a
        a, b = b, a + b             # 往后推进一步


print("--- 取自然数的前 5 个 ---")
nums = natural_numbers()
print("用 next 逐个取：", [next(nums) for _ in range(5)])

print("\n--- 用 islice 更优雅 ---")
print("前 8 个：", list(itertools.islice(natural_numbers(), 8)))

print("\n--- 斐波那契前 10 个 ---")
print(list(itertools.islice(fibonacci(), 10)))

print("\n--- 跳过前 5 个，只要第 6~10 个 ---")
print(list(itertools.islice(fibonacci(), 5, 10)))

# 输出：
# --- 取自然数的前 5 个 ---
# 用 next 逐个取： [1, 2, 3, 4, 5]
#
# --- 用 islice 更优雅 ---
# 前 8 个： [1, 2, 3, 4, 5, 6, 7, 8]
#
# --- 斐波那契前 10 个 ---
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
#
# --- 跳过前 5 个，只要第 6~10 个 ---
# [5, 8, 13, 21, 34]
#
# 【重点】islice(可迭代对象, 开始, 结束) 和切片 a[开始:结束] 很像，
#         但它支持任何可迭代对象，而且不会把中间的元素存起来。
# 【常见错误】写 list(natural_numbers()) 想看看内容 —— 会一直跑到内存耗尽。


# ==============================================================================
# 知识点 2：itertools 常用工具
# ==============================================================================
#
# itertools 是标准库里的「迭代器工具箱」，里面的函数全都返回迭代器
# （惰性、省内存）。下面是最常用的几个：
#
#   count(start, step)     无限计数
#   cycle(iterable)        无限循环一个序列
#   repeat(x, n)           把 x 重复 n 次
#   islice(it, start, stop) 切片（支持无限序列）
#   chain(*iterables)      把多个序列首尾相接
#   takewhile(pred, it)    一直取，直到条件不成立
#   dropwhile(pred, it)    一直丢，直到条件不成立
#   groupby(it, key)       按 key 分组（相邻的才分到一组！）
#   accumulate(it)         累积求和（也能传别的函数）

print("\n--- count / cycle / repeat ---")
print("count(10, 5)：", list(itertools.islice(itertools.count(10, 5), 5)))
print("cycle('AB')：", list(itertools.islice(itertools.cycle("AB"), 7)))
print("repeat('嘿', 3)：", list(itertools.repeat("嘿", 3)))

print("\n--- chain：首尾相接 ---")
print(list(itertools.chain([1, 2], "ab", (3,))))

print("\n--- takewhile / dropwhile ---")
data = [1, 2, 3, 10, 4, 5]
print("takewhile(<5)：", list(itertools.takewhile(lambda x: x < 5, data)))
print("dropwhile(<5)：", list(itertools.dropwhile(lambda x: x < 5, data)))

print("\n--- accumulate：累积计算 ---")
print("累加：", list(itertools.accumulate([1, 2, 3, 4, 5])))
print("累乘：", list(itertools.accumulate([1, 2, 3, 4, 5], lambda a, b: a * b)))

# 输出：
# --- count / cycle / repeat ---
# count(10, 5)： [10, 15, 20, 25, 30]
# cycle('AB')： ['A', 'B', 'A', 'B', 'A', 'B', 'A']
# repeat('嘿', 3)： ['嘿', '嘿', '嘿']
#
# --- chain：首尾相接 ---
# [1, 2, 'a', 'b', 3]
#
# --- takewhile / dropwhile ---
# takewhile(<5)： [1, 2, 3]
# dropwhile(<5)： [10, 4, 5]
#
# --- accumulate：累积计算 ---
# 累加： [1, 3, 6, 10, 15]
# 累乘： [1, 2, 6, 24, 120]
#
# 【注意】takewhile 和 dropwhile 都只看「开头那一串」：
#         takewhile 在 10 处停下；dropwhile 丢掉 1,2,3 之后就再也不判断了，
#         所以后面的 4、5 依然保留。

print("\n--- groupby：按 key 分组（一定要先排序！）---")
words = ["apple", "avocado", "banana", "blueberry", "cherry"]
for letter, group in itertools.groupby(words, key=lambda w: w[0]):
    print(f"{letter}：{list(group)}")

print("\n--- 没排序会怎样 ---")
unsorted_words = ["banana", "apple", "avocado", "blueberry", "cherry"]
for letter, group in itertools.groupby(unsorted_words, key=lambda w: w[0]):
    print(f"{letter}：{list(group)}")

# 输出：
# --- groupby：按 key 分组（一定要先排序！）---
# a：['apple', 'avocado']
# b：['banana', 'blueberry']
# c：['cherry']
#
# --- 没排序会怎样 ---
# b：['banana']
# a：['apple', 'avocado']
# b：['blueberry']
# c：['cherry']
#
# 【重点】groupby 只把「相邻且 key 相同」的合并成一组。
#         想要 SQL 里 GROUP BY 那种效果，必须先 sorted(..., key=...) 再分组。
# 【常见错误】忘记排序，导致同一个 key 出现多组，这是 groupby 最常见的坑。

# ==============================================================================
# 知识点 3：yield from —— 转发另一个可迭代对象
# ==============================================================================
#
# 场景：A 生成器想把 B 的产出「转交」出去。
#   笨写法：for value in B: yield value
#   好写法：yield from B
#
# 【重点】yield from 不只是省两行代码：它还会把 send()、close() 转给子生成器，
#         并且能拿到子生成器的 return 值（下面会演示）。

print("\n--- yield from 可以接任何可迭代对象 ---")


def combine():
    yield from [1, 2]               # 列表
    yield from (3, 4)               # 元组
    yield from "ab"                 # 字符串
    yield from range(5, 7)          # range


print(list(combine()))

# 输出：
# --- yield from 可以接任何可迭代对象 ---
# [1, 2, 3, 4, 'a', 'b', 5, 6]
#
# 【重点】yield from 后面只要是可迭代对象就行，不一定是生成器。

print("\n--- 实战：拍平嵌套列表 ---")


def flatten(items):
    """把任意深度的嵌套列表拍平成一维"""
    for item in items:
        if isinstance(item, list):      # 还是列表 → 递归进去
            yield from flatten(item)    # 递归 + 转发，一行搞定
        else:
            yield item                  # 不是列表 → 直接产出


nested = [1, [2, 3, [4, 5]], 6, [7, [8]]]
print("原始：", nested)
print("拍平：", list(flatten(nested)))

# 输出：
# --- 实战：拍平嵌套列表 ---
# 原始： [1, [2, 3, [4, 5]], 6, [7, [8]]]
# 拍平： [1, 2, 3, 4, 5, 6, 7, 8]
#
# 【重点】yield from 是「递归生成器」的标准写法。
#         不用 yield from 的话，得写嵌套 for 循环，深度一深就没法看了。

print("\n--- yield from 能拿到子生成器的 return 值 ---")


def worker():
    yield "任务 A"
    yield "任务 B"
    return "子生成器完成了"         # 这个值会传给 yield from 表达式


def boss():
    result = yield from worker()    # 等子生成器全部产出完，result 就是它的 return
    print("  收到子生成器的返回值：", result)
    yield "收工"


print("boss 的产出：", list(boss()))

# 输出：
# --- yield from 能拿到子生成器的 return 值 ---
#   收到子生成器的返回值： 子生成器完成了
# boss 的产出： ['任务 A', '任务 B', '收工']
#
# 【注意】print 出现在 list() 求值过程中，所以显示在「boss 的产出」之前。
# 【重点】yield from 表达式本身的值 = 子生成器 return 的东西（没 return 就是 None）。


# ==============================================================================
# 知识点 4：管道式处理 —— 把生成器串成流水线
# ==============================================================================
#
# Unix 管道：cat file | grep error | sort | head
# 每个命令只做一件事，前一端的输出就是后一端的输入。
#
# 生成器可以搭出同样的流水线：
#     数据源 → 过滤 → 转换 → 格式化 → 消费
#
# 【重点】整条管道是惰性的：不消费就不执行，
#         消费时也是「一个元素走完全程」，而不是「一段走完全部再下一段」。

print("\n--- 搭一条数据处理管道 ---")


def source(rows):
    """数据源：逐个产出原始数据"""
    yield from rows


def keep_even(numbers):
    """过滤器：只留偶数"""
    for n in numbers:
        if n % 2 == 0:
            yield n


def scale(numbers, factor):
    """转换器：乘以系数"""
    for n in numbers:
        yield n * factor


def decorate(numbers):
    """格式化器：加上前缀"""
    for n in numbers:
        yield f"#{n}"


raw = range(1, 11)
pipeline = decorate(scale(keep_even(source(raw)), 10))
print("管道结果：", list(pipeline))

# 输出：
# --- 搭一条数据处理管道 ---
# 管道结果： ['#20', '#40', '#60', '#80', '#100']
#
# 【重点】每个函数的参数和返回值都是「可迭代对象」，
#         所以任意几个都能自由拼接、随意增删某一节。

print("\n--- 观察惰性：管道建好但没消费时，什么都不会发生 ---")


def loud_source(rows):
    for n in rows:
        print(f"  [源] 产出 {n}")
        yield n


def loud_filter(numbers):
    for n in numbers:
        if n % 2 == 0:
            print(f"  [过滤器] 放行 {n}")
            yield n


pipe = loud_filter(loud_source([1, 2, 3, 4]))
print("管道已建好（上面没有任何输出）")
print("开始消费，只取第一个：", next(pipe))
print("再取一个：", next(pipe))

# 输出：
# --- 观察惰性：管道建好但没消费时，什么都不会发生 ---
# 管道已建好（上面没有任何输出）
#   [源] 产出 1
#   [源] 产出 2
#   [过滤器] 放行 2
# 开始消费，只取第一个： 2
#   [源] 产出 3
#   [源] 产出 4
#   [过滤器] 放行 4
# 再取一个： 4
#
# 【重点】注意执行顺序：源产出一个 → 过滤器判断 → 交出去，
#         而不是「源全部产出完，再统一过滤」。这就是流水线的价值。


# ==============================================================================
# 知识点 5：【常见错误】进阶阶段最容易翻的车
# ==============================================================================
#
# 1. 对无限生成器用 list() —— 永远跑不完
# 2. yield from 后面写了不可迭代的东西 —— TypeError
# 3. 管道里重复使用同一个生成器 —— 第二次是空的
# 4. groupby 忘了排序 —— 同一个 key 被拆成好几组

print("\n--- 错误：yield from 不可迭代对象 ---")


def bad():
    yield from 42                   # 42 不是可迭代对象


try:
    list(bad())
except TypeError as e:
    print("报错：", e)

# 输出：
# --- 错误：yield from 不可迭代对象 ---
# 报错： 'int' object is not iterable
#
# 【怎么避免】
#   1. 无限序列永远用 islice / takewhile / break 收口
#   2. yield from 后面只放列表、元组、range、生成器这类可迭代对象
#   3. 管道尽量「一次性用完」；要复用就先把源数据存成列表
#   4. groupby 之前先 sorted(key=...)


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 生成器能表示无限序列（while True + yield），用 islice / takewhile / break 收口
# 2. itertools 是迭代器工具箱：count / cycle / repeat / islice / chain /
#    takewhile / dropwhile / accumulate / pairwise / groupby / tee
# 3. groupby 只合并相邻的同 key 元素，分组前必须先排序
# 4. yield from 用来转发另一个可迭代对象的产出，写法比 for + yield 更短
# 5. yield from 会传递 send / close，并能拿到子生成器的 return 值
# 6. 递归 + yield from 是拍平嵌套结构的标准套路
# 7. 生成器可以串成管道：源 → 过滤 → 转换 → 格式化 → 消费
# 8. 管道是惰性的，消费时才逐元素流动，内存占用恒定


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写一个 primes() 生成器，无限产出质数，再用 islice 取前 20 个
# 练习 2：写一个 cycle_n(iterable, n) 生成器，把序列循环 n 遍
# 练习 3：用 yield from 写一个 flatten，能拍平「任意深度」的嵌套列表
# 练习 4：用 itertools + 生成器搭一条管道：从 1~100 里取 3 的倍数，
#         平方后只保留大于 200 的，输出前 5 个
# 练习 5：用 groupby 统计一段文字中每个单词出现的次数（提示：先 split，再排序）
#
# 【下一步】05_实战应用.py
# ==============================================================================
