"""
================================================================================
第 4 章 · 数据结构：列表与元组
文件 02：列表方法
================================================================================

【学习目标】
    1. 掌握列表最常用的 11 个方法
    2. 分清「原地修改」和「返回新列表」的区别
    3. 知道每个方法返回什么、什么时候会报错
    4. 学会根据场景选对方法，避开新手常踩的坑

【怎么用这个文件】
    - 每个知识点先看讲解，再对照代码和输出
    - 可以打开 Python 交互环境，自己敲一遍
    - 直接运行：python 02_列表方法.py

【前置知识】
    - 01_列表基础.py：创建、索引、切片、遍历
    - 第 3 章：函数调用和参数的基本概念
================================================================================
"""

# ==============================================================================
# 知识点 1：append() 与 extend() —— 加一个，还是加一串？
# ==============================================================================
#
# 【讲解】两个方法都是「往列表末尾加东西」，但加的单位不同。
#
#   append(x)   把 x 当成「一个整体」放到末尾
#   extend(x)   把 x 里的元素「逐个倒出来」放到末尾
#
#   生活类比：
#       append(一箱苹果)    → 把整箱苹果搬到货架上，货架上多了一个「箱子」
#       extend(一箱苹果)    → 把箱子拆开，把每个苹果摆到货架上
#
# 【重点】append() 和 extend() 都是原地修改，返回值都是 None。
#         所以不要写 my_list = my_list.append(1)，这样 my_list 会变成 None！

print("--- append 与 extend ---")

nums = [1, 2]
return_value = nums.append(3)
print(f"append(3) 后：{nums}")
print(f"append() 的返回值：{return_value}")

nums.append([4, 5])
print(f"append([4, 5]) 后：{nums}")

nums2 = [1, 2]
nums2.extend([3, 4])
print(f"extend([3, 4]) 后：{nums2}")

nums3 = [1, 2]
nums3.extend("abc")
print(f"extend('abc') 后：{nums3}")

# 输出：
# --- append 与 extend ---
# append(3) 后：[1, 2, 3]
# append() 的返回值：None
# append([4, 5]) 后：[1, 2, 3, [4, 5]]
# extend([3, 4]) 后：[1, 2, 3, 4]
# extend('abc') 后：[1, 2, 'a', 'b', 'c']
#
# 【注意】extend() 接收的是「可迭代对象」，字符串也可以，
#         所以 extend("abc") 会加进去三个字符，而不是一个字符串 "abc"。
#
# 【常见错误】想合并两个列表，却写成了 append：
#       a = [1, 2]
#       b = [3, 4]
#       a.append(b)     # 得到 [1, 2, [3, 4]]，不是 [1, 2, 3, 4]
#   应该用 a.extend(b)，或者 a = a + b。


# ==============================================================================
# 知识点 2：insert() —— 插队，但要先报位置
# ==============================================================================
#
# 【讲解】insert(index, value) 把 value 插到 index 这个位置，
#   原来 index 及之后的元素全部往后挪一位。
#
#   类比：排队时有人插到第 2 位，原来第 2 位及后面的人都要后退一步。
#
# 【重点】insert() 也是原地修改，返回 None。
#         如果给的索引超过列表长度，它不会报错，而是直接加到末尾。

print("--- insert ---")

letters = ["a", "c"]
print(f"初始：{letters}")

letters.insert(1, "b")
print(f"insert(1, 'b') 后：{letters}")

letters.insert(0, "start")
print(f"insert(0, 'start') 后：{letters}")

letters.insert(100, "end")
print(f"insert(100, 'end') 后：{letters}")

# 输出：
# --- insert ---
# 初始：['a', 'c']
# insert(1, 'b') 后：['a', 'b', 'c']
# insert(0, 'start') 后：['start', 'a', 'b', 'c']
# insert(100, 'end') 后：['start', 'a', 'b', 'c', 'end']
#
# 【注意】索引 100 远超列表长度，Python 不会报 IndexError，
#         而是理解为「插到最后」，这是 insert 的特殊行为。
#
# 【重点】参数顺序是 insert(索引, 值)，别写反。


# ==============================================================================
# 知识点 3：remove()、pop()、clear() —— 三种「删除」各管什么
# ==============================================================================
#
# 【讲解】删除有三种常见需求，对应三个方法：
#
#   remove(值)   按「值」删除，删除第一个匹配项；找不到就报 ValueError
#   pop(索引)    按「位置」删除，并把这个元素返回给你；默认删最后一个
#   clear()      清空整个列表，一个不留
#
# 【重点】remove() 只看值，不看位置；有重复值时只删最前面那个。
#         pop() 是唯一「删完还能拿到」的方法，因为它有返回值。
#
# 【常见错误】remove() 的返回值是 None，不是被删掉的元素。
#   想拿到被删的元素，请用 pop()。

print("--- remove、pop、clear ---")

fruits = ["苹果", "香蕉", "橘子", "香蕉"]
print(f"初始：{fruits}")

fruits.remove("香蕉")
print(f"remove('香蕉') 后：{fruits}")

last = fruits.pop()
print(f"pop() 取出的元素：{last}")
print(f"pop() 后：{fruits}")

removed = fruits.pop(1)
print(f"pop(1) 取出的元素：{removed}")
print(f"pop(1) 后：{fruits}")

fruits.clear()
print(f"clear() 后：{fruits}")

fruits.extend(["苹果"])
try:
    fruits.remove("西瓜")
except ValueError as e:
    print(f"remove 不存在的元素报错：ValueError: {e}")

fruits.clear()
try:
    fruits.pop()
except IndexError as e:
    print(f"pop 空列表报错：IndexError: {e}")

# 输出：
# --- remove、pop、clear ---
# 初始：['苹果', '香蕉', '橘子', '香蕉']
# remove('香蕉') 后：['苹果', '橘子', '香蕉']
# pop() 取出的元素：香蕉
# pop() 后：['苹果', '橘子']
# pop(1) 取出的元素：橘子
# pop(1) 后：['苹果']
# clear() 后：[]
# remove 不存在的元素报错：ValueError: list.remove(x): x not in list
# pop 空列表报错：IndexError: pop from empty list
#
# 【注意】clear() 也是原地清空，返回 None。
#   清空后列表还在，只是里面空了；这和 del fruits 整个删除变量不是一回事。


# ==============================================================================
# 知识点 4：index() 与 count() —— 找位置、数次数
# ==============================================================================
#
# 【讲解】
#   index(值)             找到第一个匹配项，返回它的索引
#   index(值, start)      从 start 开始往后找
#   index(值, start, stop)在 [start, stop) 范围内找
#   count(值)             数一数这个值出现了几次
#
# 【重点】index() 找不到会报 ValueError；
#         count() 找不到只会返回 0，不报错。
#   一个「找不到就翻脸」，一个「找不到就说零」。

print("--- index 与 count ---")

grades = ["A", "B", "A", "C", "A", "B"]

print(f"grades：{grades}")
print(f"count('A')：{grades.count('A')}")
print(f"index('A')：{grades.index('A')}")
print(f"index('A', 1)：{grades.index('A', 1)}")
print(f"index('B', 0, 2)：{grades.index('B', 0, 2)}")
print(f"count('D')：{grades.count('D')}")

try:
    grades.index("D")
except ValueError as e:
    print(f"index('D') 报错：ValueError: {e}")

# 输出：
# --- index 与 count ---
# grades：['A', 'B', 'A', 'C', 'A', 'B']
# count('A')：3
# index('A')：0
# index('A', 1)：2
# index('B', 0, 2)：1
# count('D')：0
# index('D') 报错：ValueError: list.index(x): x not in list
#
# 【常见错误】以为 index('A', 1) 返回「第 2 个 A」。
#   不是。start=1 的意思是「从索引 1 开始找」，
#   找到的第一个 A 在索引 2，所以返回 2，而不是数字 1。
#
# 【注意】index() 的 start/stop 和切片一样左闭右开，所以 index('B', 0, 2) 只查索引 0、1。


# ==============================================================================
# 知识点 5：sort() —— 原地排队
# ==============================================================================
#
# 【讲解】sort() 把列表本身按顺序排好，默认从小到大。
#
#   常用参数：
#       reverse=True     从大到小
#       key=函数         按「函数算出来的结果」排序
#
#   比如按字符串长度排：key=len
#   比如按元组的第二项排：key=lambda item: item[1]
#
# 【重点】sort() 是原地修改，返回 None！
#   想保留原列表、得到一个排序后的新列表，用内置函数 sorted(列表)。
#   名字很像，但一个改自己，一个返回新列表。

print("--- sort ---")

scores = [88, 92, 75, 92]
print(f"排序前：{scores}")

sorted_scores = sorted(scores)
print(f"sorted(scores) 返回新列表：{sorted_scores}")
print(f"原列表保持不变：{scores}")

return_value = scores.sort()
print(f"sort() 的返回值：{return_value}")
print(f"升序后：{scores}")

scores.sort(reverse=True)
print(f"降序后：{scores}")

languages = ["Python", "java", "C++", "go"]
languages.sort(key=str.lower)
print(f"忽略大小写排序：{languages}")

students = [("小明", 85), ("小红", 92), ("小刚", 78)]
students.sort(key=lambda student: student[1], reverse=True)
print(f"按成绩从高到低：{students}")

# 输出：
# --- sort ---
# 排序前：[88, 92, 75, 92]
# sorted(scores) 返回新列表：[75, 88, 92, 92]
# 原列表保持不变：[88, 92, 75, 92]
# sort() 的返回值：None
# 升序后：[75, 88, 92, 92]
# 降序后：[92, 92, 88, 75]
# 忽略大小写排序：['C++', 'go', 'java', 'Python']
# 按成绩从高到低：[('小红', 92), ('小明', 85), ('小刚', 78)]
#
# 【常见错误】写出这种代码：
#       scores = scores.sort()
#   结果 scores 变成 None，之后再调用就报 AttributeError。
#   正确写法只有两种：scores.sort() 或 scores = sorted(scores)。
#
# 【注意】sort() 是稳定排序：成绩相同的人会保持原来的先后顺序，适合多条件排序。


# ==============================================================================
# 知识点 6：reverse() —— 把顺序倒过来
# ==============================================================================
#
# 【讲解】reverse() 原地反转列表，返回 None。
#
#   【易混淆】它和 sort(reverse=True) 完全不是一回事：
#       reverse()            只是把现在的顺序倒过来（不比较大小）
#       sort(reverse=True)   先按大小排好，再从大到小排列
#
#   比如 [3, 1, 2]：
#       reverse()          → [2, 1, 3]
#       sort(reverse=True) → [3, 2, 1]

print("--- reverse ---")

values = [1, 2, 3, 4]
print(f"初始：{values}")

result = values.reverse()
print(f"reverse() 后：{values}")
print(f"reverse() 的返回值：{result}")

values.reverse()
print(f"再 reverse() 一次，回到原顺序：{values}")

# 输出：
# --- reverse ---
# 初始：[1, 2, 3, 4]
# reverse() 后：[4, 3, 2, 1]
# reverse() 的返回值：None
# 再 reverse() 一次，回到原顺序：[1, 2, 3, 4]
#
# 【注意】reversed() 返回的是迭代器，不是列表，需要 list() 转换。
#   values[::-1] 直接返回新列表，也不会改动原列表。


# ==============================================================================
# 知识点 7：copy() —— 复印一份，但只复印了「封面」
# ==============================================================================
#
# 【讲解】copy() 返回一个新列表，新列表和原列表是两个独立的「外层容器」。
#   往副本里 append 元素，不会影响原列表。
#
# 【重点】copy() 是「浅拷贝」：
#   它只复制最外面这一层；如果列表里还有列表，
#   里面的那个列表仍然是两个外层列表「共用」的。
#
#   就像复印一份文件夹：外层文件夹是新的，
#   但文件夹里夹着的同一张纸，还是原来那张纸。
#
# 【注意】`b = a` 不是拷贝，只是给同一个列表多贴了一个标签。
#   这个区别第 5 个文件会用图例和代码详细说明。

print("--- copy ---")

original = [1, 2, 3]
copied = original.copy()
copied.append(4)

print(f"原列表：{original}")
print(f"副本 append 后：{copied}")

alias = original
alias.append(99)
print(f"用 = 赋值再修改：{original}")

matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()
shallow[0][0] = 999

print(f"\n浅拷贝后改内层，原矩阵：{matrix}")
print(f"浅拷贝自己：{shallow}")

# 输出：
# --- copy ---
# 原列表：[1, 2, 3]
# 副本 append 后：[1, 2, 3, 4]
# 用 = 赋值再修改：[1, 2, 3, 99]
#
# 浅拷贝后改内层，原矩阵：[[999, 2], [3, 4]]
# 浅拷贝自己：[[999, 2], [3, 4]]
#
# 【常见错误】以为 copy() 之后就可以随便改嵌套结构。
#   对一维列表确实安全，但对嵌套列表不安全。彻底独立要用 copy.deepcopy()，
#   第 5 个文件会讲。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. append(x) 加一个对象；extend(iterable) 把元素逐个加入
# 2. insert(i, x) 在指定位置插入，越界索引会插到末尾
# 3. remove(x) 按值删第一个匹配项，找不到报 ValueError
# 4. pop(i) 按索引删除并返回元素，默认删最后一个；空列表 pop 报 IndexError
# 5. clear() 清空列表；三者都返回 None
# 6. index(x) 找不到报 ValueError；count(x) 找不到返回 0
# 7. sort() 原地排序返回 None；sorted() 返回新列表
# 8. sort(key=..., reverse=...) 可以自定义排序规则，并且是稳定排序
# 9. reverse() 只是倒序，不比较大小；reversed() 返回迭代器
# 10. copy() 是浅拷贝；b = a 根本不是拷贝
# 11. 所有原地修改的方法都返回 None，别把返回值赋回变量


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：创建购物清单，用 append 加一件商品，用 extend 加三件，用 insert 把牛奶插到最前面。
# 练习 2：创建 [5, 3, 8, 1, 9]，先用 sort 升序，再用 reverse 变成降序，打印每一步。
# 练习 3：先用 count 统计某个分数出现的次数，再遍历统计 90 分以上的人数。
# 练习 4：创建两个列表，分别用 append 和 extend 合并，观察结果有什么不同。
#
# 【下一步】03_列表推导式.py
# ==============================================================================
