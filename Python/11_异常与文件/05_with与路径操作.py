"""
================================================================================
第 11 章 · 异常与文件
文件 05：with 与路径操作
================================================================================

【学习目标】
    1. 用 with 自动关闭文件，再也不用担心忘记 close
    2. 看懂上下文管理器：__enter__ 和 __exit__ 到底什么时候执行
    3. 自己写上下文管理器（类写法 + @contextmanager 装饰器）
    4. 用 pathlib 处理路径：拼接、拆解、判断存在、创建目录
    5. 遍历目录：iterdir、glob、rglob 的区别

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 演示用的临时目录会在运行结束时自动删除
    - 「输出」块是运行后的实际结果
    - 直接运行：python 05_with与路径操作.py

【前置知识】
    - 文件 04：open()、文件读写、encoding
    - 第 9 章：类、特殊方法 __enter__ / __exit__
================================================================================
"""

import tempfile                        # 建临时目录
import shutil                          # 删除目录
from pathlib import Path               # 路径操作的主角
from contextlib import contextmanager  # 用装饰器写上下文管理器

DEMO_DIR = Path(tempfile.mkdtemp(prefix="py11_path_"))   # 演示专用目录
print("演示目录已创建（系统临时目录，运行结束会删除）")

# ==============================================================================
# 知识点 1：为什么需要 with —— 从「手动 close」说起
# ==============================================================================
#
# 【讲解】文件 04 里我们用 open() + close()，问题是中间只要出岔子，close() 就执行
#   不到了：写文件时抛个异常，f.close() 永远执行不到，缓冲区没落盘、句柄没释放。
#   老办法是用 try/finally 兜住，但啰嗦。with 就是这套 try/finally 的语法糖：不管
#   块里是正常结束、return 还是抛异常，退出时都会自动调用 close()。
#
# 【类比】with 像「自动门」：进门自动开，出门自动关，不用记着手动关。
# 【重点】with 块结束时资源就被释放了，不用（也不该）再手动 close。多个文件可以
#   写在同一个 with 里，用逗号隔开：with open(a) as fa, open(b) as fb。

print("\n--- 1. with 自动关闭 ---")

target = DEMO_DIR / "with_demo.txt"

with open(target, "w", encoding="utf-8") as f:
    f.write("用 with 写入\n")
    print("  代码块内部，关闭了吗？", f.closed)     # 还在块里，没关
print("  代码块外部，关闭了吗？", f.closed)         # 出块就关好了

with open(target, "r", encoding="utf-8") as f:
    print("  读回来：", repr(f.read()))

# 块里抛异常，with 同样会关闭文件
try:
    with open(target, "w", encoding="utf-8") as f:
        raise RuntimeError("模拟中途出事")          # 故意炸一下
except RuntimeError as e:
    print("  捕获到异常：", e)
    print("  但文件已被 with 关闭：", f.closed)

# 输出：
# --- 1. with 自动关闭 ---
#   代码块内部，关闭了吗？ False
#   代码块外部，关闭了吗？ True
#   读回来： '用 with 写入\n'
#   捕获到异常： 模拟中途出事
#   但文件已被 with 关闭： True


# ==============================================================================
# 知识点 2：上下文管理器 —— with 背后发生了什么
# ==============================================================================
#
# 【讲解】任何实现了下面两个方法的对象，都能用在 with 里：
#   __enter__(self)                    进入 with 时调用，返回值给 as 后面的变量
#   __exit__(self, exc_type, exc, tb)  离开 with 时调用（正常、return、异常都算）
# __exit__ 的三个参数就是「块里出了什么错」：没出错时都是 None；出错时 exc_type
# 是异常类，exc 是异常对象，tb 是 Traceback。
#
# 【重点】__exit__ 的返回值决定异常要不要继续往外传：返回 True 会把异常「吞掉」，
#   外面看不到；返回 False 或干脆不 return（None），异常照常传播。可以想象成
#   「出门还钥匙时顺手把报警器关了」，外面就听不到响了。

print("\n--- 2. 上下文管理器的机制 ---")


class Recorder:
    """只会说话的上下文管理器，用来看 __enter__ / __exit__ 的调用时机。"""

    def __enter__(self):
        print("  [__enter__] 进入 with，比如：打开文件")
        return "我是 as 拿到的值"        # 返回值赋给 as 变量

    def __exit__(self, exc_type, exc, tb):
        print("  [__exit__] 离开 with，比如：关闭文件")
        print("     出错了吗？", exc_type is not None)
        if exc_type is not None:
            print("     异常：", exc_type.__name__, "-", exc)
        return False                    # False = 不吞异常


with Recorder() as value:
    print("  块内，as 拿到：", value)

try:
    with Recorder():
        raise ValueError("故意抛个错")   # __exit__ 返回 False，异常会传出去
except ValueError as e:
    print("  外层接住了：", e)

# 输出：
# --- 2. 上下文管理器的机制 ---
#   [__enter__] 进入 with，比如：打开文件
#   块内，as 拿到： 我是 as 拿到的值
#   [__exit__] 离开 with，比如：关闭文件
#     出错了吗？ False
#   [__enter__] 进入 with，比如：打开文件
#   [__exit__] 离开 with，比如：关闭文件
#     出错了吗？ True
#     异常： ValueError - 故意抛个错
#   外层接住了： 故意抛个错
#
# 【常见错误】__exit__ 里不小心 return True，错误就被静默吞掉，排查极痛苦。除非
#   你非常确定「这个错可以忽略」，否则一律 return False（或不写 return）。


# ==============================================================================
# 知识点 3：用 @contextmanager 几行写一个上下文管理器
# ==============================================================================
#
# 【讲解】为了做上下文管理器专门写个类太啰嗦。contextlib 提供 @contextmanager，
#   用一个生成器函数就能搞定，骨架是「准备 → yield → 清理」：
#       @contextmanager
#       def 名字(参数):
#           进入时的准备            ← 相当于 __enter__
#           try:
#               yield 交给 with 的值  ← with 块在这里执行
#           finally:
#               离开时的清理          ← 相当于 __exit__
# 【重点】yield 前后的代码就是「进入」和「离开」，yield 的值就是 as 拿到的值。
#   try/finally 一定要写，否则 with 块里抛异常时，清理代码会被跳过。

print("\n--- 3. @contextmanager 写法 ---")


@contextmanager
def section(title):
    """打印分节标记：进入时开始，结束时收尾。"""
    print(f"  >>> {title} 开始")
    try:
        yield title                     # 这里把控制权交给 with 块
    finally:
        print(f"  <<< {title} 结束")


with section("读取数据") as name:
    print("      正在处理：", name)

try:
    with section("会出错的任务"):
        raise RuntimeError("任务失败了")
except RuntimeError as e:
    print("  异常传出来了：", e, " ← 说明 finally 清理已经执行过")

# 输出：
# --- 3. @contextmanager 写法 ---
#   >>> 读取数据 开始
#       正在处理： 读取数据
#   <<< 读取数据 结束
#   >>> 会出错的任务 开始
#   <<< 会出错的任务 结束
#   异常传出来了： 任务失败了  ← 说明 finally 清理已经执行过


# ==============================================================================
# 知识点 4：pathlib 基础 —— Path 对象与 / 拼接
# ==============================================================================
#
# 【讲解】Path 把「路径」变成对象，拼接用除号 /，干净又不会漏斜杠：
#       字符串：base + "/" + name      ← 自己管斜杠，多一个少一个都可能出错
#       Path：  base / name            ← 一个 / 搞定，Windows / Linux 都认
# 【重点】/ 拼接的规则：右边是绝对路径时，结果直接就是右边（前面全被丢掉）。这是
#   既定行为，不是 bug。Path 在 Windows 上打印反斜杠、Linux 上打印正斜杠，它自己处理。

print("\n--- 4. Path 与 / 拼接 ---")

rel = Path("data") / "notes" / "a.txt"
print("  用 / 拼接：", rel)
print("  是绝对路径吗？", rel.is_absolute())
print("  字符串拼接：", "data" + "/" + "notes" + "/" + "a.txt")
print("  右边是绝对路径：", Path("data") / Path("C:/other/x.txt"))

# 输出：
# --- 4. Path 与 / 拼接 ---
#   用 / 拼接： data\notes\a.txt
#   是绝对路径吗？ False
#   字符串拼接： data/notes/a.txt
#   右边是绝对路径： C:\other\x.txt
#
# 【注意】第 1、4 行在 Windows 上显示反斜杠，Linux/macOS 上是正斜杠；这正是 Path 的价值。


# ==============================================================================
# 知识点 5：拆解路径 —— name / stem / suffix / parent / parts
# ==============================================================================
#
# 【讲解】常用属性：p.name 最后一段（含扩展名）；p.stem 去掉最后一个扩展名；
#   p.suffix 最后一个扩展名；p.suffixes 所有扩展名列表；p.parent 上一级；p.parts 各段。
# 【常见错误】以为 p.stem 是「去掉所有扩展名」：a.tar.gz 的 stem 是 "a.tar"，不是
#   "a"。要改扩展名用 p.with_suffix(".md")，别手动切字符串。

print("\n--- 5. 拆解路径 ---")

sample = Path("D:/study/notes/python.txt")
print("  str(p)  :", str(sample))
print("  name    :", sample.name, "| stem:", sample.stem, "| suffix:", sample.suffix)
print("  parent  :", sample.parent)
print("  parts   :", sample.parts)

archive = Path("backup.tar.gz")
print("  backup.tar.gz 的 stem    :", archive.stem, " ← 只去掉最后一个扩展名")
print("  backup.tar.gz 的 suffixes:", archive.suffixes)
print("  with_suffix('.md')       :", Path("readme.txt").with_suffix(".md"))

# 输出：
# --- 5. 拆解路径 ---
#   str(p)  : D:\study\notes\python.txt
#   name    : python.txt | stem: python | suffix: .txt
#   parent  : D:\study\notes
#   parts   : ('D:\\', 'study', 'notes', 'python.txt')
#   backup.tar.gz 的 stem    : backup.tar  ← 只去掉最后一个扩展名
#   backup.tar.gz 的 suffixes: ['.tar', '.gz']
#   with_suffix('.md')       : readme.md


# ==============================================================================
# 知识点 6：判断存在、创建目录、便捷读写
# ==============================================================================
#
# 【讲解】Path 把这些操作都变成了方法，比 os.path 系列好记：
#   p.exists() / p.is_file() / p.is_dir()        存在？是文件？是目录？
#   p.mkdir(parents=True, exist_ok=True)         建目录（含中间层，已存在不报错）
#   p.read_text(encoding="utf-8")                一次性读文本
#   p.write_text(内容, encoding="utf-8")         一次性写文本（会覆盖！）
# 【重点】mkdir 这两个参数几乎总是一起用，是「安全建目录」的标准写法。write_text
#   和 open(..., "w") 一样会整个覆盖旧文件；它适合小文件，大文件用 with + 逐行读。

print("\n--- 6. 判断存在与便捷读写 ---")

notes_dir = DEMO_DIR / "notes"
print("  创建前，notes 存在吗？", notes_dir.exists())

notes_dir.mkdir(parents=True, exist_ok=True)      # 不存在就建
notes_dir.mkdir(parents=True, exist_ok=True)      # 再来一次，也不报错
print("  创建后，存在吗？", notes_dir.exists(), "| 是目录吗？", notes_dir.is_dir())

todo = notes_dir / "todo.txt"
todo.write_text("第一件事：学 with\n第二件事：学 pathlib\n", encoding="utf-8")
print("  写入后，是文件吗？", todo.is_file())
print("  读回来：", repr(todo.read_text(encoding="utf-8")))
print("  文件大小：", todo.stat().st_size, "字节")

# 输出：
# --- 6. 判断存在与便捷读写 ---
#   创建前，notes 存在吗？ False
#   创建后，存在吗？ True | 是目录吗？ True
#   写入后，是文件吗？ True
#   读回来： '第一件事：学 with\n第二件事：学 pathlib\n'
#   文件大小： 53 字节


# ==============================================================================
# 知识点 7：遍历目录 —— iterdir / glob / rglob
# ==============================================================================
#
# 【讲解】三个方法，从「只看一层」到「钻到最深处」：
#   p.iterdir()        列出直接子项（文件和目录都算），不递归
#   p.glob("*.txt")    按通配符匹配，只在一层里找
#   p.rglob("*.txt")   递归匹配，等价于 glob("**/*.txt")
# 【重点】三者顺序都是「操作系统给的顺序」，不保证按名字排；要稳定输出就 sorted()。
# 【类比】iterdir 看这一层抽屉，glob 在这层按标签找，rglob 拉开所有抽屉找。

print("\n--- 7. 遍历目录 ---")

tree = DEMO_DIR / "tree"
(tree / "deep").mkdir(parents=True, exist_ok=True)     # 一次建两层
(tree / "a.txt").write_text("a", encoding="utf-8")
(tree / "b.txt").write_text("b", encoding="utf-8")
(tree / "deep" / "c.txt").write_text("c", encoding="utf-8")
(tree / "deep" / "note.md").write_text("d", encoding="utf-8")

print("  tree 的直接子项（iterdir）：")
for item in sorted(tree.iterdir()):        # sorted 让顺序稳定
    kind = "目录" if item.is_dir() else "文件"
    print(f"    [{kind}] {item.name}")

print("  tree 这一层的 .txt（glob）：")
for item in sorted(tree.glob("*.txt")):
    print("    ", item.name)

print("  tree 里所有 .txt（rglob，递归）：")
for item in sorted(tree.rglob("*.txt")):
    print("    ", item.name)

# 输出：
# --- 7. 遍历目录 ---
#   tree 的直接子项（iterdir）：
#     [文件] a.txt
#     [文件] b.txt
#     [目录] deep
#   tree 这一层的 .txt（glob）：
#      a.txt
#      b.txt
#   tree 里所有 .txt（rglob，递归）：
#      a.txt
#      b.txt
#      c.txt
#
# 【看点】glob("*.txt") 没找到 deep/c.txt（它不在这一层），rglob 钻进去了。


# ==============================================================================
# 知识点 8：路径两个高频坑
# ==============================================================================
#
# 【坑 1】手写反斜杠："C:\new\test.txt" 里的 \n 被当成换行符，路径直接坏掉，报
#   FileNotFoundError 还看不出错在哪。正确写法：r"C:\new\test.txt"、"C:/new/test.txt"，
#   或者干脆用 Path 拼接，压根不碰反斜杠。
# 【坑 2】以为相对路径「相对脚本」。它相对的是「当前工作目录」——你在哪个目录
#   运行 python 就是哪个。换个目录运行就找不到文件。像「我家楼下那家店」：换个
#   出发点，「楼下」就不是同一家店了。
#   ✅ 稳妥写法：BASE = Path(__file__).parent，再 BASE / "data" / "a.txt"。

print("\n--- 8. 两个高频坑 ---")

script_dir = Path(__file__).parent          # 脚本自己所在的目录
print("  脚本目录名：", script_dir.name, " ← 从哪儿运行都是它")
print("  拼出数据目录名：", (script_dir / "data").name)

bad = "C:\new\test.txt"                     # 反斜杠被转义：含换行和制表符
print("  这个「路径」有", len(bad), "个字符，第 3 个是换行吗？", bad[2] == "\n")

# 输出：
# --- 8. 两个高频坑 ---
#   脚本目录名： 11_异常与文件  ← 从哪儿运行都是它
#   拼出数据目录名： data
#   这个「路径」有 13 个字符，第 3 个是换行吗？ True


# ==============================================================================
# 收尾：清理临时目录
# ==============================================================================

shutil.rmtree(DEMO_DIR, ignore_errors=True)   # 连子目录一起删干净
print("\n演示目录已清理：", DEMO_DIR.exists() == False)
# 输出：
# 演示目录已清理： True


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. with = try/finally 的语法糖：退出代码块自动 close，出异常也不漏
# 2. 一个 with 可以打开多个文件，逗号隔开，退出时按相反顺序关闭
# 3. 上下文管理器要实现 __enter__（进入）和 __exit__（离开）；__exit__ 返回 True
#    会吞掉异常，返回 False/None 则继续传播（默认行为）
# 4. @contextmanager + yield 几行就能写出上下文管理器，记得配 try/finally
# 5. Path 用 / 拼接路径，比字符串拼接安全，自动处理平台差异
# 6. name / stem / suffix / parent / parts 拆路径；a.tar.gz 的 stem 是 a.tar
# 7. exists / is_file / is_dir 判断；mkdir(parents=True, exist_ok=True) 安全建目录
# 8. read_text / write_text 适合小文件；大文件还是 with + 逐行读
# 9. iterdir 看一层，glob 找一层，rglob 递归找；要稳定顺序就 sorted()
# 10. 相对路径相对的是「当前工作目录」，要相对脚本就用 Path(__file__).parent


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：用 @contextmanager 写 safe_open(path, mode)，进入时打印「打开 xxx」，
#         退出时打印「关闭 xxx」。
#
# 练习 2：用 pathlib 统计某个目录里：有多少 .py 文件、多少个目录、总大小多少字节
#         （提示：rglob、is_file、stat().st_size）。
#
# 练习 3：写一个函数，把某目录下所有 .txt 改成 .md（提示：with_suffix + rename，
#         先在小目录里试）。
#
# 练习 4：用 Path(__file__).parent 得到脚本目录，拼出「练习输出.txt」，写入
#         「Hello pathlib」，再用 read_text 验证。
#
# 【下一步】06_模块与标准库.py（第 12 章）
# ==============================================================================
