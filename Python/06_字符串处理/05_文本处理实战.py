"""
================================================================================
第 6 章 · 字符串处理
文件 05：文本处理实战
================================================================================

【学习目标】
    1. 用「分步拆解」的思路做词频统计
    2. 手写一个邮箱格式校验函数，并系统测试边界情况
    3. 从混杂文本里提取数字，比较手写扫描和正则
    4. 输出真正对齐的中英文表格（解决汉字占两列的问题）
    5. 解析 URL 查询参数，理解编码与多值参数

【怎么用这个文件】
    - 从上往下读，每个「实战」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 05_文本处理实战.py

【前置知识】
    - 01~04 号文件（字符串基础、常用方法、格式化、编码）
    - 第 5 章：字典的增删改查
================================================================================
"""

import re
from urllib.parse import parse_qs, unquote, unquote_plus

# ==============================================================================
# 实战 1：统计词频 —— 经典问题，五步搞定
# ==============================================================================
#
# 【讲解】「统计每个单词出现了几次」是文本处理的第一课，拆开就五步：
#       1. 统一大小写（the 和 The 要算同一个词）
#       2. 去掉标点（不然 "dog." 和 "dog" 会被当成两个词）
#       3. 按空白切分（split() 一行搞定）
#       4. 用字典累加次数（dict.get(键, 默认值) 是好帮手）
#       5. 排序取前几名（次数从多到少，次数相同按字母排）
#
# 【重点】真实场景还要处理词形变化（run/runs/running）和停用词（the/a/of），
#   这些属于自然语言处理，本章只做最基础的分词统计。

text = """The quick brown fox jumps over the lazy dog.
The dog barks, and the fox runs!"""

# 第 1 步 + 第 2 步：统一小写，再逐个去掉标点
cleaned = text.lower()
for mark in [".", ",", "!", "?", ";", ":"]:
    cleaned = cleaned.replace(mark, "")     # 把标点替换成空串 = 删除

# 第 3 步：按任意空白切分（换行也会被当成分隔符）
words = cleaned.split()
print(len(words), words[:6])                # 总词数 + 前 6 个，确认切得对

# 输出：
# 16 ['the', 'quick', 'brown', 'fox', 'jumps', 'over']

# 第 4 步：字典计数。freq.get(w, 0) 的意思是「有这个键就取值，没有就当 0」
freq = {}
for w in words:
    freq[w] = freq.get(w, 0) + 1
print(freq)

# 输出：
# {'the': 4, 'quick': 1, 'brown': 1, 'fox': 2, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 2, 'barks': 1, 'and': 1, 'runs': 1}

# 第 5 步：排序。把「次数的相反数」和「单词」组成元组，直接 sort() 就会
#   先按次数降序（因为取了负），再按字母升序。第 7 章学了 sorted(key=...) 可写得更直白。
ranked = []
for word, count in freq.items():
    ranked.append((-count, word))
ranked.sort()

print(f"总词数：{len(words)}，不同单词：{len(freq)}")
for neg_count, word in ranked[:5]:
    count = -neg_count                      # 把负号还原成正的次数
    bar = "*" * count                       # 用星号画出柱状图
    print(f"{word:<8}{bar:<6}{count}")

# 输出：
# 总词数：16，不同单词：11
# the     ****  4
# dog     **    2
# fox     **    2
# and     *     1
# barks   *     1
#
# 【注意】字典是「插入顺序」保存的，所以直接 print(freq) 时，the 排第一只是
#   因为它在原文里最先出现，不是因为它次数最多。


# ==============================================================================
# 实战 2：验证邮箱格式 —— 把规则一条条写成 if
# ==============================================================================
#
# 【讲解】邮箱看起来简单，规则却不少。一个「够用」的校验可以拆成 7 条：
#       1. 必须有且只有一个 @          2. @ 前后都不能为空
#       3. 整体不能有空格              4. 用户名只能含字母、数字、._%+-
#       5. 用户名不能以点开头/结尾，也不能有连续两个点
#       6. 域名必须有点，且每一段都不能为空
#       7. 最后一段（顶级域名）必须是字母，长度至少 2
#
# 【为什么】格式校验只能挡住「明显不是邮箱」的输入，真正验证邮箱是否存在，
#   只能发一封验证邮件。【重点】校验是为了体验和防脏数据，不是为了安全。

def validate_email(email):
    """检查邮箱格式，合法返回 True，否则返回 False。"""
    if email.count("@") != 1:                   # 规则 1：@ 恰好一个
        return False

    local, _, domain = email.partition("@")     # 按第一个 @ 切成两半

    if not local or not domain:                 # 规则 2：两边都不能空
        return False
    if " " in email:                            # 规则 3：不能有空格
        return False

    allowed = "abcdefghijklmnopqrstuvwxyz0123456789._%+-"
    if not set(local.lower()) <= set(allowed):  # 规则 4：用户名字符白名单
        return False
    if local.startswith(".") or local.endswith(".") or ".." in local:
        return False                            # 规则 5：点的位置

    labels = domain.split(".")                  # 规则 6：域名必须有点，每段非空
    if len(labels) < 2 or "" in labels:
        return False

    tld = labels[-1]                            # 规则 7：顶级域名是字母且至少 2 位
    if not tld.isalpha() or len(tld) < 2:
        return False

    return True


test_emails = [
    "alice@example.com",
    "bob.smith@mail.co.uk",
    "user+tag@example.org",
    "charlie@localhost",
    "@example.com",
    "david@.com",
    "eve@@example.com",
    "frank@exam ple.com",
    "gina@example.c",
    "henry@example..com",
]

print(f"{'邮箱':<26}{'结果'}")
print("-" * 34)
for email in test_emails:
    verdict = "通过" if validate_email(email) else "拒绝"
    print(f"{email:<26}{verdict}")

# 输出：
# 邮箱                        结果
# ----------------------------------
# alice@example.com         通过
# bob.smith@mail.co.uk      通过
# user+tag@example.org      通过
# charlie@localhost         拒绝
# @example.com              拒绝
# david@.com                拒绝
# eve@@example.com          拒绝
# frank@exam ple.com        拒绝
# gina@example.c            拒绝
# henry@example..com        拒绝
#
# 【注意】上面表格的中文列宽对不齐！原因和处理办法见实战 4。
#
# 【进阶】真实项目里通常用正则一行搞定，但可读性差、错误提示也不友好：
print(bool(re.match(r"^[\w.+-]+@[\w-]+\.[\w.]+$", "alice@example.com")))

# 输出：
# True
#
# 【重点】上面这个正则就挡不住 "a@b..com"，而且解释起来很费劲。
#   规则少的时候，老实写 if 反而更好维护。


# ==============================================================================
# 实战 3：从文本里提取数字 —— 手写扫描 vs 正则
# ==============================================================================
#
# 【讲解】需求：从「订单编号 A102，金额 3500 元，折扣 12.5%，共 3 件」
#   里把数字都找出来。
#
#   思路一（手写）：从左往右扫，遇到数字就攒起来，遇到非数字就收一笔。
#   思路二（正则）：第 12 章会系统讲，这里先借来用一下。

order = "订单编号 A102，金额 3500 元，折扣 12.5%，共 3 件。"

# 思路一：逐字符扫描，只认 0~9
numbers = []
current = ""
for ch in order:
    if ch.isdigit():
        current = current + ch          # 是数字：攒起来
    else:
        if current:
            numbers.append(current)     # 遇到非数字：结算上一笔
            current = ""
if current:                             # 别忘了结尾可能还剩一笔
    numbers.append(current)

print(numbers)

# 输出：
# ['102', '3500', '12', '5', '3']
#
# 【注意】12.5 被拆成了 '12' 和 '5' 两个数字——小数点不是数字。
#   这就是手写扫描的局限：规则一复杂，代码就跟着复杂。

# 思路二：用正则一次性描述「数字长什么样」
#   \d+      一个或多个数字
#   \.       字面的小数点
#   \d+\.\d+ 整数部分 + 小数点 + 小数部分
#   |        或者
match_all = re.findall(r"\d+\.\d+|\d+", order)
print(match_all)

# 输出：
# ['102', '3500', '12.5', '3']

# 转成数字再求和，验证提取结果是对的
total = 0.0
for item in match_all:
    total = total + float(item)             # 提取出来的是字符串，必须转换
print(f"合计：{total:,.2f}")

# 输出：
# 合计：3,617.50
#
# 【重点】正则的优势是「声明式」：你描述要找什么样子的东西，而不是怎么一步步找。
#   【常见错误】提取出来的永远是字符串，参与计算必须 float() / int()。
#   【进阶】带单位的数字可以用分组限定：re.findall(r"(\d+(?:\.\d+)?)\s*元",
#   "3.5 元 12 元") 会得到 ['3.5', '12']，其中 (?:...) 表示「只分组、不捕获」。


# ==============================================================================
# 实战 4：输出对齐的表格 —— 解决汉字占两列的问题
# ==============================================================================
#
# 【讲解】03 号文件说过：len("张三") 是 2，但终端里它占 2 列宽（每个汉字占 2 列）。
#   于是 f"{'张三':<8}" 只补了 6 个空格，视觉上却比补 8 个空格的英文窄。
#
# 【怎么办】自己算「显示宽度」：常见汉字的码点都大于 0x2E7F，
#   把它算成 2 列，其余算 1 列，然后手动补空格。
#   真实项目里更严谨的做法是用第三方库 wcwidth。

def display_width(text):
    """估算字符串在终端里占几列：汉字算 2，其余算 1。"""
    width = 0
    for ch in text:
        width += 2 if ord(ch) > 0x2E7F else 1   # 汉字的码点普遍大于 0x2E7F
    return width


def pad(text, width, align="left"):
    """按显示宽度补空格，让中英文混排也能对齐。"""
    padding = width - display_width(text)
    if padding <= 0:
        return text
    if align == "right":
        return " " * padding + text
    return text + " " * padding


data = [("张三", "数学", 95), ("欧阳娜娜", "英语", 88), ("李四", "语文", 100)]

line = "+" + "-" * 10 + "+" + "-" * 6 + "+" + "-" * 6 + "+"
print(line)
print("|" + pad("姓名", 10) + "|" + pad("科目", 6) + "|" + pad("分数", 6, "right") + "|")
print(line)
for name, subject, score in data:
    print("|" + pad(name, 10) + "|" + pad(subject, 6) + "|" + pad(str(score), 6, "right") + "|")
print(line)

# 输出：
# +----------+------+------+
# |姓名      |科目  |  分数|
# +----------+------+------+
# |张三      |数学  |    95|
# |欧阳娜娜  |英语  |    88|
# |李四      |语文  |   100|
# +----------+------+------+
#
# 【重点】对照一下：如果直接用 f"{'姓名':<10}"，因为 len 是 2 而不是 4，
#   补出来的空格会多 2 个，边框就会歪。中英文混排的表格，
#   必须用「显示宽度」而不是 len() 来对齐。
#
# 【补充】emoji 和一些特殊符号的宽度更麻烦（有的占 2 列，有的占 1 列），
#   真要做得完美，直接用 wcwidth 库，不要自己硬编码。


# ==============================================================================
# 实战 5：解析 URL 查询参数
# ==============================================================================
#
# 【讲解】网址里问号 ? 后面那一串就是「查询参数」，格式是：
#
#       键1=值1&键2=值2&键3=值3
#
#   参数值里的中文、空格等字符不能直接出现在 URL 里，
#   必须先「百分号编码」（URL encoding）：
#       空格 → %20（或 +）    中文 → 每个字节写成 %XX
#
# 【为什么】URL 规范只允许一小部分 ASCII 字符，
#   中文「教程」的 UTF-8 字节是 e6 95 99 e7 a8 8b，编码后就是 %E6%95%99%E7%A8%8B。

url = ("https://example.com/search"
       "?keyword=python%E6%95%99%E7%A8%8B&page=2&sort=price&tag=a&tag=b")

# 第 1 步：把路径和查询串分开
base, _, query = url.partition("?")
print(base, query, sep="\n")

# 输出：
# https://example.com/search
# keyword=python%E6%95%99%E7%A8%8B&page=2&sort=price&tag=a&tag=b

# 第 2 步：按 & 切成键值对，按 = 切开，再解码
#   注意：同一个键可能出现多次（tag=a&tag=b），所以值统一用列表存
params = {}
for pair in query.split("&"):
    key, _, value = pair.partition("=")
    key = unquote_plus(key)             # 键也要解码，虽然通常没有中文
    value = unquote_plus(value)         # unquote_plus 会把 + 还原成空格
    params.setdefault(key, []).append(value)

print(params)

# 输出：
# {'keyword': ['python教程'], 'page': ['2'], 'sort': ['price'], 'tag': ['a', 'b']}

# 标准库已经写好了：parse_qs 一行就能得到同样的结构
print(parse_qs(query))

# 输出：
# {'keyword': ['python教程'], 'page': ['2'], 'sort': ['price'], 'tag': ['a', 'b']}
#
# 【重点】从 URL 里取出来的值永远是「字符串」，页码要参与计算必须自己 int()。
print(f"关键词：{params['keyword'][0]}，页码：{int(params['page'][0])}")
print("标签：" + "、".join(params["tag"]))

# 输出：
# 关键词：python教程，页码：2
# 标签：a、b

# unquote 与 unquote_plus 的区别：+ 号算不算空格
print(repr(unquote_plus("a+b%20c")))
print(repr(unquote("a+b%20c")))

# 输出：
# 'a b c'
# 'a+b c'
#
# 【注意】查询串里的 + 按规范代表空格，所以解析查询参数要用 unquote_plus。
#   如果解码的是 URL 的路径部分，+ 就是普通加号，要用 unquote。
#
# 【常见错误】直接对整条 URL 用 split("=")，结果参数值里带 = 时全乱套。
#   正确做法是先按 & 切、再对每个键值对用 partition("=") 只切第一个等号。
print("a=1=2".partition("="))
print("a=1=2".split("="))

# 输出：
# ('a', '=', '1=2')
# ['a', '1', '2']


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 词频统计五步：统一大小写 → 去标点 → split → 字典累加 → 排序
# 2. dict.get(键, 0) + 1 是最常用的计数写法，配合 [] 赋值即可
# 3. 排序取 TopN：用 (-次数, 单词) 元组 sort，次数相同还能按字母排
# 4. 邮箱校验是「规则清单」：@ 数量、空值、空格、字符白名单、点的位置、TLD
# 5. 格式校验挡不住假邮箱，真实性只能靠发验证邮件
# 6. 手写扫描适合简单规则；规则一复杂就换正则，声明式更省代码
# 7. 提取出来的数字是字符串，参与计算前必须 int() / float()
# 8. 中英文混排的表格要按「显示宽度」补空格，不能用 len()
# 9. URL 查询参数格式：?键=值&键=值，中文需要百分号编码
# 10. 解析参数用 partition("=") 只切第一个等号，值里带 = 也不会错
# 11. unquote_plus 会把 + 还原成空格；同一个键出现多次时，值要存成列表


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：统计一段英文里出现次数最多的 3 个字母（提示：遍历字符 + 字典计数）
# 练习 2：给 validate_email 增加一条规则：用户名长度不能超过 64 个字符
# 练习 3：从 "身高 175cm，体重 68.5kg，年龄 28 岁" 里提取所有数字并求和
# 练习 4：用 display_width + pad 打印一张 4 列的成绩表（姓名、语文、数学、英语）
# 练习 5：解析 URL "https://shop.com/list?cat=book&price=10-50&page=3"，
#         输出每个参数，并把 price 拆成最低价和最高价
# 练习 6：把一个字典 {'name': '张三', 'age': 20} 拼成查询串（提示：urllib.parse.quote）
#
# 【下一步】第 7 章：高阶函数（07_高阶函数/）
# ==============================================================================
