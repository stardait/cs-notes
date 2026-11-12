"""
================================================================================
第 11 章 · 异常与文件
文件 04：文件读写
================================================================================

【学习目标】
    1. 掌握文件操作的三步骤：打开 → 读写 → 关闭
    2. 分清 open() 的各种模式：r / w / a / x / + / b
    3. 会用 read() / readline() / readlines() / for 循环读文件
    4. 理解文件指针（tell / seek），知道 r+ 是「覆盖」不是「插入」
    5. 明白为什么永远要显式写 encoding="utf-8"

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 所有演示文件都建在系统临时目录里，运行结束自动删除，不污染你的学习目录
    - 「输出」块是运行后的实际结果
    - 直接运行：python 04_文件读写.py

【前置知识】
    - 文件 01~03：异常处理
    - 第 6 章：字符串
================================================================================
"""

import tempfile                        # 用来创建临时目录，放演示文件
import shutil                          # 用来删除整个临时目录
from pathlib import Path               # 路径对象，第 5 个文件会详细讲

# 建一个临时目录做演示：mkdtemp 返回一个独一无二的新目录
DEMO_DIR = Path(tempfile.mkdtemp(prefix="py11_file_"))
print("演示目录已创建（系统临时目录，运行结束会删除）")

# ==============================================================================
# 知识点 1：文件操作三步骤 —— 打开、读写、关闭
# ==============================================================================
#
# 【讲解】操作文件就像去图书馆借书：打开（open）→ 借出来用（read / write）→
#   归还（close）。不归还的后果：别人借不到（文件被占用），管理员也不知道你
#   什么时候用完。
#
# 【重点】不 close 会怎样？写进文件的数据可能还堵在「缓冲区」里（内存），程序
#   一崩、一断电，数据就丢了。close() 会强制把缓冲区内容刷到硬盘。
# 【类比】缓冲区像奶茶店的取餐台：做好 10 杯才一起端出来（批量写更高效），
#   close() 就是「好了，全端出来」。实际写代码请用 with（文件 05 详讲）。

print("\n--- 1. 打开、写入、关闭 ---")

buffer_path = DEMO_DIR / "buffer.txt"

f = open(buffer_path, "w", encoding="utf-8")   # 打开：拿到文件对象
f.write("这句话还堵在缓冲区里")                  # 写入：先放在内存缓冲区
size_before = buffer_path.stat().st_size        # 看看硬盘上现在有多少字节
f.close()                                       # 关闭：把缓冲区刷到硬盘
size_after = buffer_path.stat().st_size         # 再看一次

print("  close 之前，文件大小 > 0 ?", size_before > 0, " ← 数据还在内存里")
print("  close 之后，文件大小 > 0 ?", size_after > 0, " ← 现在才真正落盘")

# 输出：
# --- 1. 打开、写入、关闭 ---
#   close 之前，文件大小 > 0 ? False  ← 数据还在内存里
#   close 之后，文件大小 > 0 ? True  ← 现在才真正落盘


# ==============================================================================
# 知识点 2：open() 的模式总表
# ==============================================================================
#
# 【讲解】open(路径, 模式, encoding=...) 的第二个参数决定「怎么开」：
#
#   模式   含义           文件不存在时   文件已存在时
#   -----  -------------- -------------  ------------------
#   "r"    只读（默认）   报错           从头读
#   "w"    只写           新建           清空重写（危险！）
#   "a"    追加           新建           在末尾接着写
#   "x"    独占新建       新建           报错（防覆盖）
#   "r+"   读写           报错           从头读，可写（覆盖）
#   "b"    二进制         配合上面使用，如 "rb" / "wb"
#
# 【重点】"w" 是最危险的模式：一打开就把原文件清空，哪怕你一个字都没写！
#   想「只改一点」千万别用 w，用 a 或 r+。"b" 是附加标志（如 "rb"），读写 bytes。

print("\n--- 2. 各种模式 ---")

mode_path = DEMO_DIR / "modes.txt"

# r 模式打开不存在的文件：FileNotFoundError
try:
    open(DEMO_DIR / "还没建的文件.txt", "r", encoding="utf-8")
except FileNotFoundError as e:
    print("  r 模式 + 文件不存在 →", type(e).__name__)

# w 模式：文件不存在就新建
with open(mode_path, "w", encoding="utf-8") as f:
    f.write("第一版内容")
print("  w 模式新建并写入完成，文件存在 ?", mode_path.exists())

# x 模式：文件已存在就报错，专门用来防止覆盖
try:
    open(mode_path, "x", encoding="utf-8")
except FileExistsError as e:
    print("  x 模式 + 文件已存在 →", type(e).__name__, " ← 防止覆盖的好帮手")

# 输出：
# --- 2. 各种模式 ---
#   r 模式 + 文件不存在 → FileNotFoundError
#   w 模式新建并写入完成，文件存在 ? True
#   x 模式 + 文件已存在 → FileExistsError  ← 防止覆盖的好帮手


# ==============================================================================
# 知识点 3：写入 —— write 与「覆盖 vs 追加」
# ==============================================================================
#
# 【讲解】write(字符串) 把内容写进去，返回写入的字符数；writelines(列表) 把一串
#   字符串依次写进去（不会自动加换行）。
# 【重点】"w" 是清空重写，"a" 是末尾追加。这是新手最容易搞混的一对：想把日志
#   一行行加上，用 a；想重新生成一份文件，用 w。
# 【常见错误】以为 w 是「在原文后面写」，结果把重要文件清空 —— 而且不可恢复。
# 【类比】w 像「把本子撕了换新的」，a 像「翻到最后一页接着写」。

print("\n--- 3. 写入：覆盖 vs 追加 ---")

diary = DEMO_DIR / "diary.txt"

with open(diary, "w", encoding="utf-8") as f:
    count = f.write("第一行：今天学文件读写\n")
    print("  write() 返回写入的字符数：", count, " ← 含换行符")

with open(diary, "a", encoding="utf-8") as f:            # a：追加，不动原内容
    f.write("第二行：追加模式不会清空旧内容\n")

with open(diary, "w", encoding="utf-8") as f:            # w：清空重写！
    f.write("第三行：w 模式把前面两行都清掉了\n")

with open(diary, "r", encoding="utf-8") as f:
    print("  现在文件里只有：", repr(f.read()))

# 输出：
# --- 3. 写入：覆盖 vs 追加 ---
#   write() 返回写入的字符数： 12  ← 含换行符
#   现在文件里只有： '第三行：w 模式把前面两行都清掉了\n'
#
# 【重点】看清了吗？w 模式一打开就清空，前两行彻底没了。想「改一点」就先整体读出来、
#   改完再整体写回去。


# ==============================================================================
# 知识点 4：读取 —— read / readline / readlines / for 循环
# ==============================================================================
#
# 【讲解】四种读法，按「一次读多少」区分：
#   f.read()        一次读完整个文件，返回 str（大文件会吃掉大量内存）
#   f.read(n)       只读 n 个字符
#   f.readline()    读一行（含行尾 \n）；读完以后返回空字符串 ""
#   f.readlines()   一次读完，返回列表，每个元素是一行（含 \n）
#   for line in f:  逐行迭代，最省内存，处理大文件首选
# 【重点】每一行都带着行尾的 "\n"，直接 print 会出现多余空行，配 rstrip() 去掉。

print("\n--- 4. 四种读取方式 ---")

with open(diary, "w", encoding="utf-8") as f:            # 重新造一个三行的文件
    f.write("第一行\n第二行\n第三行\n")

with open(diary, "r", encoding="utf-8") as f:
    print("  read() 读全部：", repr(f.read()))
    print("  再 read() 一次：", repr(f.read()), " ← 指针已到末尾，读到空字符串")

with open(diary, "r", encoding="utf-8") as f:
    print("  read(3) 只读 3 个字符：", repr(f.read(3)))

with open(diary, "r", encoding="utf-8") as f:
    print("  第 1 次 readline()：", repr(f.readline()))
    print("  第 2 次 readline()：", repr(f.readline()))
    print("  第 3 次 readline()：", repr(f.readline()))
    print("  第 4 次 readline()：", repr(f.readline()), " ← 到末尾了，返回空串")

with open(diary, "r", encoding="utf-8") as f:
    print("  readlines()：", f.readlines())

with open(diary, "r", encoding="utf-8") as f:
    print("  for 循环逐行（记得 rstrip）：")
    for i, line in enumerate(f, start=1):                 # enumerate 从 1 开始编号
        print(f"    第 {i} 行：{line.rstrip()}")

# 输出：
# --- 4. 四种读取方式 ---
#   read() 读全部： '第一行\n第二行\n第三行\n'
#   再 read() 一次： ''  ← 指针已到末尾，读到空字符串
#   read(3) 只读 3 个字符： '第一行'
#   第 1 次 readline()： '第一行\n'
#   第 2 次 readline()： '第二行\n'
#   第 3 次 readline()： '第三行\n'
#   第 4 次 readline()： ''  ← 到末尾了，返回空串
#   readlines()： ['第一行\n', '第二行\n', '第三行\n']
#   for 循环逐行（记得 rstrip）：
#     第 1 行：第一行
#     第 2 行：第二行
#     第 3 行：第三行
#
# 【注意】read() 不带参数很省事，但 1 GB 的文件会一次性读进内存；大文件用 for。


# ==============================================================================
# 知识点 5：文件指针 —— tell 与 seek
# ==============================================================================
#
# 【讲解】文件对象内部有一个「书签」，记录下次从哪儿读写：f.tell() 看位置，
#   f.seek(0) 挪回开头（最常用）。
# 【重点】读文件是「顺序读」，读完指针就到末尾了。想再读一遍必须 seek(0)，
#   否则读到的是空字符串 —— 这就是上面「再 read() 一次」返回 '' 的原因。
# 【注意】文本模式 tell() 返回「字节偏移」，一个汉字占 3 字节（UTF-8），
#   所以读 3 个汉字后 tell() 是 9，不是 3。别拿它当字符下标用。

print("\n--- 5. 文件指针 ---")

with open(diary, "r", encoding="utf-8") as f:
    print("  开头 tell() =", f.tell())
    text = f.read(3)                    # 读 3 个汉字
    print("  读了", repr(text), "之后 tell() =", f.tell(), " ← 汉字占 3 字节")
    f.seek(0)                           # 书签挪回开头
    print("  seek(0) 之后 tell() =", f.tell())
    print("  重新读一行：", repr(f.readline()))

# 输出：
# --- 5. 文件指针 ---
#   开头 tell() = 0
#   读了 '第一行' 之后 tell() = 9  ← 汉字占 3 字节
#   seek(0) 之后 tell() = 0
#   重新读一行： '第一行\n'


# ==============================================================================
# 知识点 6：r+ 模式 —— 读写同一个文件，但它是「覆盖」
# ==============================================================================
#
# 【讲解】r+ 打开后可读可写，位置从头开始。写入是「像打字机一样覆盖」，不是
#   「插入」：写几个字符就盖掉几个字符，后面的内容不会往后挪。
# 【为什么容易出错】写的比原内容短，旧内容会残留一截：在第 5 个位置写 "AB"，
#   "0123456789" 变成 "0123AB6789"（后面 6789 还在）。真要「插入」，只能读出
#   全部内容、拼接好、再整体重写。
# 【注意】读写混用时不 seek 定位，行为很难预测（还会受缓冲区影响）。日常建议：
#   要么读、要么写；确需修改就「读出 → 改 → 重写」。

print("\n--- 6. r+ 模式是覆盖，不是插入 ---")

overwrite_path = DEMO_DIR / "overwrite.txt"
with open(overwrite_path, "w", encoding="utf-8") as f:
    f.write("0123456789")

with open(overwrite_path, "r+", encoding="utf-8") as f:
    print("  先读 4 个字符：", repr(f.read(4)))
    f.seek(4)                           # 明确把书签挪到第 5 个字节
    f.write("AB")                       # 在这里覆盖写入
    f.seek(0)
    print("  覆盖写入 'AB' 后：", repr(f.read()), " ← 长度没变，只是被盖掉")

# 输出：
# --- 6. r+ 模式是覆盖，不是插入 ---
#   先读 4 个字符： '0123'
#   覆盖写入 'AB' 后： '0123AB6789'  ← 长度没变，只是被盖掉


# ==============================================================================
# 知识点 7：编码 —— 为什么永远要写 encoding="utf-8"
# ==============================================================================
#
# 【讲解】文件里存的不是「文字」而是字节。文字 → 字节叫编码，字节 → 文字叫解码，
#   两边必须用同一套规则，否则就是乱码或直接报错。
# 【重点】不写 encoding 时，Python 用「系统默认编码」：老版中文 Windows 可能是
#   GBK，新版和 Linux/macOS 多是 UTF-8。同一个程序在别人电脑上就可能读出乱码，
#   所以规矩是：open() 里永远显式写 encoding="utf-8"。
# 【errors 参数】编码存不下某个字符时：strict（默认）抛异常；ignore 悄悄丢掉
#   （最危险，数据静默丢失）；replace 换成 "?"（至少能看出有问题）。

print("\n--- 7. 编码问题 ---")

encoding_path = DEMO_DIR / "encoding.txt"

with open(encoding_path, "w", encoding="utf-8") as f:
    f.write("中文内容\n")
with open(encoding_path, "r", encoding="utf-8") as f:
    print("  UTF-8 写、UTF-8 读：", repr(f.read()))

emoji_path = DEMO_DIR / "emoji.txt"
try:
    with open(emoji_path, "w", encoding="gbk") as f:     # GBK 装不下 emoji
        f.write("表情：😀")
except UnicodeEncodeError as e:
    print("  GBK 存不下 emoji →", type(e).__name__)

with open(emoji_path, "w", encoding="gbk", errors="replace") as f:
    f.write("表情：😀")                                  # 存不下的字符换成 ?
with open(emoji_path, "r", encoding="gbk") as f:
    print("  errors='replace' 写进去，读回来：", repr(f.read()))

broken = DEMO_DIR / "broken.bin"
with open(broken, "wb") as f:
    f.write(b"\xff\xfe\x00")                             # 不是合法的 UTF-8 字节
try:
    with open(broken, "r", encoding="utf-8") as f:
        f.read()
except UnicodeDecodeError as e:
    print("  用 UTF-8 读非法字节 →", type(e).__name__)

# 输出：
# --- 7. 编码问题 ---
#   UTF-8 写、UTF-8 读： '中文内容\n'
#   GBK 存不下 emoji → UnicodeEncodeError
#   errors='replace' 写进去，读回来： '表情：?'
#   用 UTF-8 读非法字节 → UnicodeDecodeError
#
# 【补充】文件开头若有无形的 BOM（记事本另存 UTF-8 时可能加），用 "utf-8-sig" 读。


# ==============================================================================
# 知识点 8：二进制模式 —— 读写图片、音频要用 b
# ==============================================================================
#
# 【讲解】文本模式（"r"/"w"）面对 str，会自动做编码转换和换行符转换；
#   二进制模式（"rb"/"wb"）面对 bytes，原样搬进搬出，一个字节都不改。
# 【什么时候用 b】图片、音频、压缩包、exe 不是文字，用文本模式打开会在解码时炸掉，
#   或者写进去的字节被悄悄改掉（换行符被替换）。
# 【重点】文本模式只能 write(str)，二进制模式只能 write(bytes)，混用抛 TypeError。

print("\n--- 8. 二进制模式 ---")

bin_path = DEMO_DIR / "data.bin"
data = bytes([0, 1, 2, 255])            # 四个字节：0x00 0x01 0x02 0xFF

with open(bin_path, "wb") as f:         # wb：二进制写，不需要 encoding
    f.write(data)
with open(bin_path, "rb") as f:         # rb：二进制读
    raw = f.read()
print("  写入并读回：", raw)
print("  类型是：", type(raw).__name__, " ← bytes 不是 str")

try:
    with open(bin_path, "wb") as f:
        f.write("我想写字符串")          # 二进制模式不收 str
except TypeError as e:
    print("  往 wb 文件里写 str →", e)

with open(diary, "rb") as f:            # 同一个文本文件，用 b 模式读
    raw = f.read()
print("  文本文件用 b 读：", repr(raw[:9]), "... 共", len(raw), "字节")

# 输出：
# --- 8. 二进制模式 ---
#   写入并读回： b'\x00\x01\x02\xff'
#   类型是： bytes  ← bytes 不是 str
#   往 wb 文件里写 str → a bytes-like object is required, not 'str'
#   文本文件用 b 读： b'\xe7\xac\xac\xe4\xb8\x80\xe8\xa1\x8c' ... 共 33 字节
#
# 【看点】3 行中文，每行 3 个字 × 3 字节 = 9 字节，加上 Windows 下换行占 2 字节
#   （\r\n），一共 (9 + 2) × 3 = 33 字节。文本模式读时 \r\n 会被自动转成 \n，
#   所以你看到的是 3 行；b 模式看到的是原始字节，一个都不少。


# ==============================================================================
# 收尾：清理临时目录
# ==============================================================================

shutil.rmtree(DEMO_DIR, ignore_errors=True)   # 递归删除整个演示目录
print("\n演示文件已清理：", DEMO_DIR.exists() == False)
# 输出：
# 演示文件已清理： True


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 文件操作三步走：open → read/write → close；不 close 数据可能还在缓冲区
# 2. 模式：r 只读 / w 清空重写（危险）/ a 追加 / x 独占新建 / r+ 读写覆盖 / b 二进制
# 3. "w" 一打开就清空文件；想保留旧内容用 "a"，想改一点就「读出 → 改 → 重写」
# 4. 四种读法：read() 全读、read(3) 读 3 个字符、readline() 读一行、readlines() 读成列表
# 5. 大文件用 for line in f 逐行读；读完指针在末尾，要再读必须 seek(0)
# 6. 文本模式 tell() 返回的是字节偏移；r+ 的写入是「覆盖」不是「插入」
# 7. 永远显式写 encoding="utf-8"；errors="replace" 能救急，但数据会被替换
# 8. 二进制模式读写 bytes，图片 / 音频 / 压缩包只能用 b 模式
# 9. 相对路径相对的是「当前工作目录」，不是脚本所在目录


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写 count_lines(path)，用 for 循环统计行数；再写 count_words(path) 统计单词数。
#
# 练习 2：把一段文字写进文件，再用 "a" 追加 3 行，最后逐行读出并打印行号。
#
# 练习 3：写 copy_file(src, dst)，用 "rb" / "wb" 每次读 1024 字节来复制；
#         想一想为什么复制图片不能用 "r" / "w"。
#
# 练习 4：用 "gbk" 读含 emoji 的 UTF-8 文件，看是报 UnicodeDecodeError 还是乱码。
#
# 【下一步】05_with与路径操作.py
# ==============================================================================
