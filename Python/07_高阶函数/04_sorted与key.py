"""
================================================================================
第 7 章 · 高阶函数
文件 04：sorted 与 key
================================================================================

【学习目标】
    1. 分清 sorted() 和 list.sort()：一个返回新列表，一个原地修改
    2. 理解 key 参数：排序前先给每个元素算一个「排序依据」
    3. 学会用 len、str.lower、abs、lambda 等做 key
    4. 掌握多级排序：元组 key、正负号、稳定排序
    5. 学会用 operator.itemgetter 让代码更简洁
    6. 知道 reverse=True 能做什么、不能做什么

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 04_sorted与key.py

【前置知识】
    - 文件 01：函数作为参数
    - 文件 02：lambda 表达式
    - 第 4 章：列表、元组；第 5 章：字典
================================================================================
"""

# ==============================================================================
# 知识点 1：sorted() 和 list.sort() 有什么区别？
# ==============================================================================
#
# 两个都能排序，区别只有一句话：
#
#   sorted(任何可迭代对象)  → 返回一个「新的排好序的列表」，原数据不动
#   列表.sort()             → 原地排序，返回 None
#
# 【类比】sorted 像「把文件复印一份，把复印件按页码排好」；
#   sort 像「直接把你桌上那叠文件重新排一遍」。
#
# 【重点】看到 `x = 列表.sort()` 就要警惕：x 会是 None，不是列表！

numbers = [3, 1, 4, 1, 5, 9, 2]

ascending = sorted(numbers)
print("sorted 返回的新列表：", ascending)
print("原列表没有变：", numbers)
print("从大到小：", sorted(numbers, reverse=True))

# 输出：
# sorted 返回的新列表： [1, 1, 2, 3, 4, 5, 9]
# 原列表没有变： [3, 1, 4, 1, 5, 9, 2]
# 从大到小： [9, 5, 4, 3, 2, 1, 1]

numbers.sort()
print("sort 之后原列表：", numbers)
print("sort 的返回值：", numbers.sort())

# 输出：
# sort 之后原列表： [1, 1, 2, 3, 4, 5, 9]
# sort 的返回值： None
#
# 【为什么】sort 的设计是「就地修改」，不需要返回值。
#   Python 用返回 None 来提醒你：这个操作有副作用，别把它赋值给变量。

print("排序字符串：", sorted("cab"))
print("排序元组：", sorted((3, 1, 2)))

# 输出：
# 排序字符串： ['a', 'b', 'c']
# 排序元组： [1, 2, 3]
#
# 【重点】sorted 的返回值永远是 list，即使输入是字符串或元组。


# ==============================================================================
# 知识点 2：默认排序 vs key 参数
# ==============================================================================
#
# 不传 key 时，sorted 直接拿元素互相比较：
#   数字比大小；字符串比字符编码；元组从第一个元素开始逐项比较。
#
# 这会带来两个常见结果：
#   1. 大写字母排在小写字母前面（编码更小）
#   2. "10" 排在 "2" 前面（逐字符比，不是按数值比）

words = ["banana", "apple", "Cherry"]
print("默认排序：", sorted(words))
print("忽略大小写：", sorted(words, key=str.lower))

number_strings = ["10", "2", "1"]
print("字符串排序：", sorted(number_strings))
print("按数值排序：", sorted(number_strings, key=int))

# 输出：
# 默认排序： ['Cherry', 'apple', 'banana']
# 忽略大小写： ['apple', 'banana', 'Cherry']
# 字符串排序： ['1', '10', '2']
# 按数值排序： ['1', '2', '10']
#
# 【重点】key 接收一个函数。sorted 会对每个元素调用一次 key(元素)，
#   用返回值作为「排序依据」，最后按依据的顺序放回原元素。
#
# 【类比】运动会按身高排队：
#   key 是「量身高」这个动作；裁判量的只是身高，
#   但最后站队的是一个个完整的人，不是一串数字。

words2 = ["bbb", "a", "cc"]
print("按长度排序：", sorted(words2, key=len))

nums = [-5, 2, -1, 4]
print("按绝对值排序：", sorted(nums, key=abs))

# 输出：
# 按长度排序： ['a', 'cc', 'bbb']
# 按绝对值排序： [-1, 2, 4, -5]
#
# 【注意】key=len 传的是函数对象 len，不是 len()。
#   写成 len() 会立刻报错，因为 len 需要参数。


# ==============================================================================
# 知识点 3：多级排序与稳定排序
# ==============================================================================
#
# 想让 key 返回多个排序依据，最自然的办法是返回一个元组：
#
#     key=lambda s: (第一依据, 第二依据, ...)
#
# 元组按「字典序」比较：先比第一个；相等再比第二个……
#
# 【类比】排行榜先按分数排；分数一样，再按年龄排；
#   年龄还一样，再按报名先后排。

students = [
    {"name": "小明", "score": 85, "age": 18},
    {"name": "小红", "score": 92, "age": 17},
    {"name": "小刚", "score": 78, "age": 18},
    {"name": "小丽", "score": 92, "age": 16},
]

for student in sorted(students, key=lambda s: s["score"]):
    print(f"{student['name']}：{student['score']} 分")

# 输出：
# 小刚：78 分
# 小明：85 分
# 小红：92 分
# 小丽：92 分
#
# 【重点】排序依据是分数，但结果里是完整的学生字典。
#   小红和小丽都是 92 分，保持原列表里的先后顺序：小红在前。

# key 函数对每个元素只会调用一次（不是每次比较都调用）
calls = []


def counting_key(student):
    calls.append(student["name"])
    return student["score"]


sorted(students, key=counting_key)
print("key 调用次数与顺序：", len(calls), calls)

# 输出：
# key 调用次数与顺序： 4 ['小明', '小红', '小刚', '小丽']
#
# 【为什么】Python 先算所有 key，再排序，最后按顺序放回元素，
#   所以 key 不会被反复调用，适合放较复杂的取值逻辑。

# 需求：分数从高到低，分数相同则年龄从小到大
ranking = sorted(students, key=lambda s: (-s["score"], s["age"]))
for student in ranking:
    print(f"{student['name']} 分数 {student['score']} 年龄 {student['age']}")

# 输出：
# 小丽 分数 92 年龄 16
# 小红 分数 92 年龄 17
# 小明 分数 85 年龄 18
# 小刚 分数 78 年龄 18
#
# 【重点】分数降序就在分数前加负号：-92 < -85，所以 92 分排在前面；
#   年龄升序就保持正数。这是「数字字段混合方向」最常用的小技巧。

# 【稳定排序】相等的元素，排序后保持原来的相对顺序。
# Python 的 sorted 和 list.sort 都是稳定排序。
same_score = sorted(students, key=lambda s: s["score"], reverse=True)
print("只按分数降序：", [s["name"] for s in same_score])

# 输出：
# 只按分数降序： ['小红', '小丽', '小明', '小刚']
#
# 【解读】小红和小丽都是 92 分，原列表里小红在前，所以结果里小红仍在前。
#   reverse=True 只改变「比较方向」，不会把相等元素的相对顺序翻过来。

# 利用稳定性，也可以「先排次要条件，再排主要条件」
step1 = sorted(students, key=lambda s: s["age"])
step2 = sorted(step1, key=lambda s: s["score"], reverse=True)
print("先年龄、后分数：", [s["name"] for s in step2])

# 输出：
# 先年龄、后分数： ['小丽', '小红', '小明', '小刚']
#
# 【重点】多趟排序的顺序不能反：
#   先按主要条件排、再按次要条件排，第二趟会把主要条件打乱。
#   口诀：先排次要的，再排主要的。


# ==============================================================================
# 知识点 4：operator.itemgetter —— 取字段的专用工具
# ==============================================================================
#
# itemgetter 可以生成一个「取下标 / 取键」的函数：
#
#     itemgetter(1)          ≈ lambda x: x[1]
#     itemgetter("score")    ≈ lambda x: x["score"]
#     itemgetter(0, 2)       ≈ lambda x: (x[0], x[2])
#
# 【好处】意图更明确、写得短，底层是 C 实现，通常比 lambda 快一点。
# 【注意】itemgetter 取的是「下标或字典键」，不是对象属性。

from operator import itemgetter

pairs = [("小明", 85), ("小红", 92), ("小刚", 78)]
print("按分数排序：", sorted(pairs, key=itemgetter(1)))
print("按分数取最高：", max(pairs, key=itemgetter(1)))

get_score = itemgetter(1)
print("单独取分数：", get_score(("小明", 85)))

# 输出：
# 按分数排序： [('小刚', 78), ('小明', 85), ('小红', 92)]
# 按分数取最高： ('小红', 92)
# 单独取分数： 85
#
# 【重点】itemgetter(1) 返回的是一个函数，所以可以直接当 key。
#   get_score(("小明", 85)) 等价于 ("小明", 85)[1]。

# 多字段排序：先按部门，再按分数
employees = [
    {"dept": "Sales", "name": "小明", "score": 85},
    {"dept": "Tech", "name": "小红", "score": 92},
    {"dept": "Sales", "name": "小刚", "score": 78},
    {"dept": "Tech", "name": "小丽", "score": 92},
]

for employee in sorted(employees, key=itemgetter("dept", "score")):
    print(employee["dept"], employee["name"], employee["score"])

# 输出：
# Sales 小刚 78
# Sales 小明 85
# Tech 小红 92
# Tech 小丽 92
#
# 【解读】先按 dept 的字典序：Sales 在 Tech 前；同一部门内按 score 升序。
#   两个 Tech 都是 92 分，保持原顺序：小红在前，小丽在后。

# 对字典的 items() 排序：按数量从少到多
inventory = {"苹果": 3, "香蕉": 5, "橙子": 2}
for name, count in sorted(inventory.items(), key=itemgetter(1)):
    print(name, count)

# 输出：
# 橙子 2
# 苹果 3
# 香蕉 5
#
# 【为什么】inventory.items() 产生 ("苹果", 3) 这样的元组，
#   itemgetter(1) 取第二个元素（数量）作为排序依据。


# ==============================================================================
# 知识点 5：reverse 参数 —— 反转比较方向
# ==============================================================================
#
# reverse=True 表示「按相反的比较方向排序」，不是「排完再倒过来」。
# 对稳定排序来说，相等元素仍然保持原始相对顺序。
#
# 【重点】reverse=True 是「整体反转比较方向」：
#   所有字段都跟着反向。想只让某一个字段降序，请用负号或多趟排序。

scores = [88, 95, 70, 95, 60]
print("升序：", sorted(scores))
print("降序：", sorted(scores, reverse=True))

# 输出：
# 升序： [60, 70, 88, 95, 95]
# 降序： [95, 95, 88, 70, 60]

# 下面用英文名避免中文编码顺序的干扰
people = [("Bob", 90), ("Alice", 90), ("Cara", 85)]

wrong = sorted(people, key=lambda p: (p[1], p[0]), reverse=True)
right = sorted(people, key=lambda p: (-p[1], p[0]))

print("全部 reverse：", wrong)
print("负号 + 元组：", right)

# 输出：
# 全部 reverse： [('Bob', 90), ('Alice', 90), ('Cara', 85)]
# 负号 + 元组： [('Alice', 90), ('Bob', 90), ('Cara', 85)]
#
# 【解读】
#   wrong：分数降序，但同分时 Bob 排在 Alice 前面（名字也降序）
#   right：分数降序，同分时 Alice 排在 Bob 前面（名字升序）
#
# 【结论】「数字降序 + 其他字段升序」的首选写法是 (-数字, 其他字段)。


# ==============================================================================
# 知识点 6：常见错误
# ==============================================================================
#
# 【常见错误 1】把 key 写成「函数调用的结果」
#   key=len("abc") 得到整数 3，sorted 却需要一个可调用对象
try:
    sorted(words2, key=len("abc"))
except TypeError as e:
    print("错误信息：", e)

# 输出：
# 错误信息： 'int' object is not callable
#
# 【修正】去掉括号：key=len。要传的是「函数本身」。

# 【常见错误 2】以为 sort() 会返回排序后的列表
unsorted = [3, 1, 2]
result = unsorted.sort()
print("原列表：", unsorted)
print("返回值：", result)

# 输出：
# 原列表： [1, 2, 3]
# 返回值： None
#
# 【修正】要么用 new_list = sorted(unsorted)，
#   要么调用 unsorted.sort() 后直接使用 unsorted，不要接返回值。

# 【常见错误 3】直接对字典列表排序，忘了写 key
try:
    sorted(students)
except TypeError as e:
    print("错误信息：", e)

# 输出：
# 错误信息： '<' not supported between instances of 'dict' and 'dict'
#
# 【为什么】字典之间没有定义 < 运算，必须用 key 告诉它比哪个字段。

# 【常见错误 4】把数字和字符串混在一起排序
try:
    sorted([3, "1", 2])
except TypeError as e:
    print("错误信息：", e)

# 输出：
# 错误信息： '<' not supported between instances of 'str' and 'int'
#
# 【修正】先统一类型：
mixed = ["3", "1", "2"]
print("统一转 int：", sorted(mixed, key=int))

# 输出：
# 统一转 int： ['1', '2', '3']


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. sorted(iterable) 返回新列表；list.sort() 原地修改并返回 None
# 2. key 接收一个函数，用它的返回值作为排序依据，不改变原元素
# 3. key 对每个元素只调用一次，适合放较复杂的取值逻辑
# 4. 常见 key：len、str.lower、abs、int、lambda、itemgetter
# 5. 多级排序用元组 key；数字降序可以取负：(-score, age)
# 6. 稳定排序：相等元素保持原顺序；可以先排次要条件，再排主要条件
# 7. reverse=True 会反转整个比较方向，不能只反转其中一个字段
# 8. itemgetter 适合按下标 / 字典键取排序依据，可一次取多个字段
# 9. key 要传函数对象，不能传函数调用结果；sort() 的返回值是 None


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：把 ["python", "Java", "C", "go"] 按长度从短到长排序；
#         长度相同的，按字母顺序排
#
# 练习 2：把 [("苹果", 3), ("香蕉", 5), ("橙子", 2)] 按数量从多到少排序
#         要求分别用 lambda 和 itemgetter 写一遍
#
# 练习 3：给定学生列表，按「分数从高到低、年龄从小到大」排序；
#         再试着只用 reverse=True 写一遍，观察同分学生的顺序变化
#
# 练习 4：解释为什么 `result = nums.sort()` 之后 result 是 None，
#         以及应该怎么改
#
# 【下一步】05_闭包.py
# ==============================================================================
