"""
================================================================================
第 10 章 · 迭代器与生成器
文件 05：实战应用
================================================================================

【学习目标】
    1. 用生成器「逐行读取大文件」，不把文件读进内存
    2. 用生成器写「无限斐波那契序列」，按需取用
    3. 用生成器「分批处理数据」，控制内存和批量提交
    4. 掌握实战中的几个坑：文件句柄、生成器耗尽、异常处理

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 05_实战应用.py

【前置知识】
    第 11 章之前的文件读写基础（open / with / 编码）
    文件 02~04（生成器、生成器表达式、itertools、管道）
================================================================================
"""

import itertools
import os
import tempfile

# ==============================================================================
# 知识点 1：读取大文件 —— 一行一行地处理
# ==============================================================================
#
# 假设你有一个 100 GB 的日志文件，要统计每种级别出现了多少次。
# 用 f.readlines() 会一次性把 100 GB 读进内存，机器直接卡死。
# 正确做法：一行一行读，读一行处理一行，处理完就扔掉。
#
# 【重点】文件对象本身就是「可迭代对象」，而且它就是自己的迭代器，
#         所以 for line in f 是「惰性读取」，同一时刻内存里只有一行。
#
# 为了让例子能直接运行，我们先用 tempfile 造一个几十行的小日志，
# 思路和 100 GB 的日志完全一样。

LOG_LINES = [
    "2026-03-01 08:00:01 INFO  用户 alice 登录成功",
    "2026-03-01 08:00:03 DEBUG 缓存命中 key=home",
    "2026-03-01 08:00:07 INFO  查询商品列表 耗时 12ms",
    "2026-03-01 08:00:11 WARNING 库存不足 sku=1024",
    "2026-03-01 08:00:15 ERROR 数据库连接超时 retry=1",
    "2026-03-01 08:00:16 INFO  重试成功",
    "2026-03-01 08:00:20 ERROR 支付回调验签失败 order=8848",
    "2026-03-01 08:00:24 INFO  用户 alice 下单成功",
    "2026-03-01 08:00:30 WARNING 请求耗时 1800ms path=/api/orders",
    "2026-03-01 08:00:35 ERROR 库存服务无响应 sku=1024",
]

log_path = os.path.join(tempfile.gettempdir(), "python_ch10_demo.log")
with open(log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG_LINES) + "\n")     # 每行末尾补换行

print("--- 准备样本日志 ---")
print("写入临时文件：", os.path.basename(log_path))
print("行数：", len(LOG_LINES), "  字节数：", os.path.getsize(log_path))

# 输出：
# --- 准备样本日志 ---
# 写入临时文件： python_ch10_demo.log
# 行数： 10   字节数： 548


def read_lines(path):
    """逐行读取文件：内存里永远只有当前这一行"""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:                       # f 是迭代器，惰性读取
            yield line.rstrip("\n")          # 去掉行尾换行符再交出去


print("\n--- 逐行读取并统计 ---")
level_count = {}
for line in read_lines(log_path):
    parts = line.split()                     # 按空白切分，多个空格也能切
    level = parts[2]                         # 第 3 列是日志级别
    level_count[level] = level_count.get(level, 0) + 1

for level, count in level_count.items():     # dict 保持插入顺序
    print(f"  {level}：{count} 条")

# 输出：
# --- 逐行读取并统计 ---
#   INFO：4 条
#   DEBUG：1 条
#   WARNING：2 条
#   ERROR：3 条
#
# 【为什么】如果这里用 f.readlines()，就是把整个文件变成一个大列表，
#         再逐条遍历。文件越大，内存占用越高，最后必然 MemoryError。
#         for line in f 则由文件对象在底层控制缓冲区，内存占用恒定。

print("\n--- 只挑出 ERROR 行（生成器负责过滤）---")


def only_errors(lines):
    """从任意「行序列」里只挑出 ERROR 行"""
    for line in lines:
        if " ERROR " in line:                # 前后带空格，避免误匹配
            yield line


for line in only_errors(read_lines(log_path)):
    print("  " + line)

# 输出：
# --- 只挑出 ERROR 行（生成器负责过滤）---
#   2026-03-01 08:00:15 ERROR 数据库连接超时 retry=1
#   2026-03-01 08:00:20 ERROR 支付回调验签失败 order=8848
#   2026-03-01 08:00:35 ERROR 库存服务无响应 sku=1024

print("\n--- 只要前 2 行：后面的根本不读 ---")
first_two = list(itertools.islice(read_lines(log_path), 2))
for line in first_two:
    print("  " + line)

# 输出：
# --- 只要前 2 行：后面的根本不读 ---
#   2026-03-01 08:00:01 INFO  用户 alice 登录成功
#   2026-03-01 08:00:03 DEBUG 缓存命中 key=home
#
# 【重点】islice 只读到第 2 行就停，剩下 8 行连磁盘都不用碰。
#         文件越大，这种「提前退出」省下的时间越多。
# 【注意】生成器里用 with open，如果在没读完时提前 break，
#         文件要等生成器被回收（或显式 close）时才关闭。
#         所以「读到一半就停」的场合，最好用 with 包住外层循环，
#         或者把 path 传进来、在函数内部读完（本例就是这样）。

os.remove(log_path)                          # 清理临时文件，别把垃圾留在系统里


# ==============================================================================
# 知识点 2：无限斐波那契序列 —— 用到哪算到哪
# ==============================================================================
#
# 斐波那契数列：0, 1, 1, 2, 3, 5, 8, 13, ...
# 它没有上限，用列表存「全部」是不可能的，但用生成器可以无限产出。
#
# 【生活类比】打印机装了一卷纸：想要多长就打印多长，
#             不需要一开始就把整卷纸展开铺满房间。

print("\n--- 定义斐波那契生成器 ---")


def fibonacci():
    """无限斐波那契序列：0, 1, 1, 2, 3, 5, ..."""
    a, b = 0, 1
    while True:
        yield a                   # 交出当前的 a，然后暂停
        a, b = b, a + b           # 恢复时从这里继续：推进一步


print("前 10 个：", list(itertools.islice(fibonacci(), 10)))
print("前 20 个的和：", sum(itertools.islice(fibonacci(), 20)))
print("前 15 个里的偶数：", [x for x in itertools.islice(fibonacci(), 15) if x % 2 == 0])

# 输出：
# --- 定义斐波那契生成器 ---
# 前 10 个： [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
# 前 20 个的和： 10945
# 前 15 个里的偶数： [0, 2, 8, 34, 144]
#
# 【重点】每次调用 fibonacci() 都得到一个「全新的」生成器，
#         所以三行代码各自从头开始，互不干扰（第 2 行不是接着第 1 行）。

print("\n--- 按条件取：第一个超过 10000 的 ---")
first_big = next(x for x in fibonacci() if x > 10000)
print("第一个超过 10000 的斐波那契数：", first_big)

print("\n--- 按条件取：小于 1000 的所有项 ---")
small = itertools.takewhile(lambda x: x < 1000, fibonacci())
print(list(small))

# 输出：
# --- 按条件取：第一个超过 10000 的 ---
# 第一个超过 10000 的斐波那契数： 10946
#
# --- 按条件取：小于 1000 的所有项 ---
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
#
# 【重点】生成器 + next(生成器表达式) 是「找到第一个满足条件的元素」
#         的惯用写法，比先建列表再循环更省内存。
#         想取「第 n 项」也一样：next(itertools.islice(fibonacci(), 20, None))。


# ==============================================================================
# 知识点 3：分批处理数据 —— 攒够一批就干活
# ==============================================================================
#
# 很多操作「一条一条做」太慢，「全部一起做」又占内存：
#     写数据库、调接口、发邮件、批量上传……
# 折中方案：攒够 N 条就处理一批（batch），这就是「分批处理」。
#
# 【生活类比】洗衣机不会一件衣服就洗一次，也不会攒一屋子才洗，
#             而是攒够一桶就洗一桶。

print("\n--- 写法 1：用列表攒，攒满就交出去 ---")


def chunks(iterable, size):
    """把任意可迭代对象切成每份 size 个的批次"""
    batch = []                       # 攒批次的篮子
    for item in iterable:
        batch.append(item)
        if len(batch) == size:       # 攒满了
            yield batch              # 交出去
            batch = []               # 换一个新篮子
    if batch:                        # 最后不足一批的也要交出去
        yield batch


for index, batch in enumerate(chunks(range(1, 11), 3), start=1):
    print(f"  第 {index} 批：{batch}")

# 输出：
# --- 写法 1：用列表攒，攒满就交出去 ---
#   第 1 批：[1, 2, 3]
#   第 2 批：[4, 5, 6]
#   第 3 批：[7, 8, 9]
#   第 4 批：[10]
#
# 【重点】最后那个 if batch 不能省！否则 10 这个「零头」会被丢掉。
# 【注意】batch = [] 也是必须的：如果直接 batch.clear()，
#         就会把已经交出去的列表清空（生成器传出去的是同一个列表对象）。

print("\n--- 写法 2：用 islice 切，无限序列也能分批 ---")


def chunks_stream(iterable, size):
    """和 chunks 一样，但不需要先把数据攒在列表里"""
    iterator = iter(iterable)        # 拿到迭代器
    while True:
        batch = list(itertools.islice(iterator, size))   # 切一批
        if not batch:                # 切不出东西了，结束
            return
        yield batch


print("从无限序列里分批，只取 3 批：")
for index, batch in enumerate(chunks_stream(itertools.count(1), 4), start=1):
    print(f"  第 {index} 批：{batch}")
    if index == 3:
        break

# 输出：
# --- 写法 2：用 islice 切，无限序列也能分批 ---
# 从无限序列里分批，只取 3 批：
#   第 1 批：[1, 2, 3, 4]
#   第 2 批：[5, 6, 7, 8]
#   第 3 批：[9, 10, 11, 12]
#
# 【重点】chunks_stream 不需要知道总长度，也不需要把数据全部读进来，
#         所以它能处理无限序列 —— 这是列表切片做不到的。

print("\n--- 实战：每批 3 条，批量写入「数据库」---")


def save_batch(batch):
    """假装把一批数据写进数据库，返回写入条数"""
    print(f"  [数据库] 写入 {batch}")
    return len(batch)


total = 0
for batch in chunks(range(1, 8), 3):
    total += save_batch(batch)
print("一共写入：", total, "条")

# 输出：
# --- 实战：每批 3 条，批量写入「数据库」---
#   [数据库] 写入 [1, 2, 3]
#   [数据库] 写入 [4, 5, 6]
#   [数据库] 写入 [7]
# 一共写入： 7 条
#
# 【重点】每批只占 3 条数据的内存，数据库连接也只开一次（批内共享），
#         这就是「流式处理」：数据再多，内存占用也不随总量增长。
#         数据量小的时候看不出差别，但 1000 万条一次性 list() 要几百 MB，
#         分批处理永远只占「一批」的内存。


# ==============================================================================
# 知识点 4：【常见错误】实战里最容易翻车的地方
# ==============================================================================
#
# 1. 用 f.readlines() 读大文件 → 内存爆掉
# 2. 生成器里裸写 open()，提前退出时文件迟迟不关
# 3. 忘记处理「最后不足一批」的零头
#
# 【常见错误 3】下面是「最后一批被丢掉」的翻车现场：

print("\n--- 错误 1：忘了处理最后一批零头 ---")


def bad_chunks(iterable, size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    # 少写了 if batch: yield batch


print("错误版本：", [list(b) for b in bad_chunks(range(1, 8), 3)])
print("正确版本：", [list(b) for b in chunks(range(1, 8), 3)])

# 输出：
# --- 错误 1：忘了处理最后一批零头 ---
# 错误版本： [[1, 2, 3], [4, 5, 6]]
# 正确版本： [[1, 2, 3], [4, 5, 6], [7]]
#
# 【重点】7 这个零头被悄悄丢了 —— 这种 bug 不会报错，
#         只会让数据对不上，排查起来非常费劲。
#
# 【另一个高频坑】生成器只能消费一次：sum(g) 之后再 sum(g) 就是 0。
#         要被算两次，就先 list() 物化，或者重新调一次生成器函数。

print("\n--- 错误 2：在生成器里裸写 open() ---")


def leaky_reader(path):
    f = open(path, "r", encoding="utf-8")    # 手动打开，没有 with
    for line in f:
        yield line
    f.close()                                # 只有读完才会执行到这里


probe_path = os.path.join(tempfile.gettempdir(), "python_ch10_probe.log")
with open(probe_path, "w", encoding="utf-8") as writer:
    writer.write("甲\n乙\n")

gen = leaky_reader(probe_path)
print("读到：", next(gen).strip())
gen.close()                                  # 提前放弃时必须显式关闭
print("生成器没走完，f.close() 不会执行，只能靠 close() 兜底")

# 输出：
# --- 错误 2：在生成器里裸写 open() ---
# 读到： 甲
# 生成器没走完，f.close() 不会执行，只能靠 close() 兜底
#
# 【怎么避免】生成器内部打开文件，一定用 with open(...)：
#         生成器被 close() 或回收时，with 会自动关闭文件。

print("\n--- 正确姿势：with 包住整个读取过程 ---")


def safe_reader(path):
    with open(path, "r", encoding="utf-8") as f:   # 无论如何都会关
        for line in f:
            yield line.strip()


print("内容：", list(safe_reader(probe_path)))
os.remove(probe_path)                        # 清理临时文件

# 输出：
# --- 正确姿势：with 包住整个读取过程 ---
# 内容： ['甲', '乙']
#
# 【重点】with + yield 是生成器读文件的标准组合。
#         即使调用方 break 掉，生成器被回收时 with 也会执行清理。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 大文件要逐行读：for line in f 是惰性的，内存占用与文件大小无关
# 2. 文件对象本身就是迭代器（iter(f) is f），用完一定要关闭
# 3. 生成器里用 with open(...)，提前退出也能自动清理资源
# 4. 无限序列用 while True + yield，取用时配 islice / takewhile / next
# 5. next(x for x in 序列 if 条件) 是「找第一个满足条件的元素」的标准写法
# 6. 分批处理：攒够 size 个就 yield 一批，别忘了处理最后的零头
# 7. chunks_stream 用 islice 实现，能处理无限序列，内存恒定
# 8. 生成器只能消费一次；需要复用就 list() 物化或重新创建


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写一个 word_count(path) 生成器，逐行读取文本文件并产出每个单词，
#         再用 collections.Counter 统计词频（提示：不要一次读入整个文件）
# 练习 2：写一个无限生成器 powers_of_two()，产出 1, 2, 4, 8, ...
#         再用 islice 取出前 20 个
# 练习 3：实现 batched(iterable, size) 生成器，要求支持任意可迭代对象，
#         并处理最后不足一批的情况
# 练习 4：写一个 tqdm_like(iterable, total) 生成器，每处理 10% 就打印一次进度
# 练习 5：综合题：从一个大文本文件里，每 1000 行统计一次错误数量并打印，
#         要求全程内存占用不超过几千行
#
# 【下一步】第 11 章：异常与文件
# ==============================================================================
