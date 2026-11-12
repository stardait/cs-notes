"""
================================================================================
第 11 章 · 异常与文件
文件 01：异常处理基础
================================================================================

【学习目标】
    1. 明白「异常」是什么，以及不处理异常会发生什么
    2. 掌握 try / except / else / finally 四件套各自的分工
    3. 学会用多个 except 精准区分不同的错误
    4. 看懂 Python 的异常类型层次（谁是谁的父类），理解 except 的顺序
    5. 记住几个最常见的坏习惯：裸 except、吞异常、try 包太大

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 代码下面的注释说明「这行为什么这么写」
    - 「输出」块是运行后的实际结果
    - 直接运行：python 01_异常处理基础.py

【前置知识】
    - 第 3 章：函数（def / return）
    - 第 9 章：类（class）—— 本文件只用它看异常类的继承关系
================================================================================
"""

# ==============================================================================
# 知识点 1：异常是什么？程序出错了会怎样
# ==============================================================================
#
# 【讲解】写程序就像开车，异常就是「爆胎」。爆胎时你有两个选择：
#   没有备胎 → 车停在原地（程序崩溃退出）；有备胎 → 换胎继续走（接住异常）。
#
# Python 的「出错」分两种：
#   语法错误 SyntaxError：还没开始跑，解释器一读就发现写错了（少括号、少冒号）
#   运行时异常 Exception：语法没问题，跑到某一行才炸（除以 0、文件不存在……）
#
# 【重点】异常不是洪水猛兽，它是 Python 的「错误上报机制」：函数遇到自己解决
#   不了的情况，就抛出（raise）一个异常对象，一层层往上传，直到有人接住
#   （except）；没人接，程序就带着 Traceback 退出。语法错误根本进不了 try。

print("=== 1. 异常是什么 ===")          # 分节标题，方便对照输出
print("程序开始执行")                    # 这行一定会打印

try:                                    # try：告诉 Python「下面这段可能会炸」
    result = 10 / 0                     # 除数为 0，抛出 ZeroDivisionError
except ZeroDivisionError as e:          # except：接住这类异常，绑定给变量 e
    print("捕获到异常：", e)             # e 是异常对象，打印出错误信息

print("程序继续往下走")                  # 异常被接住了，所以能走到这里

# 输出：
# === 1. 异常是什么 ===
# 程序开始执行
# 捕获到异常： division by zero
# 程序继续往下走
#
# 【补充】如果去掉 try/except 让异常「没人接」，屏幕会打印类似下面这样的东西
#   （这只是示意，不是本文件的输出）：
#       Traceback (most recent call last):
#         File "01_异常处理基础.py", line 45, in <module>
#           result = 10 / 0
#       ZeroDivisionError: division by zero
#   读法是从下往上：最后一行说什么错，倒数第二段指出错在哪一行（第 2 个文件详讲）。


# ==============================================================================
# 知识点 2：try / except 的最小骨架
# ==============================================================================
#
# 【讲解】结构只有两块：
#       try:               有风险的代码   ← 出事就跳到 except
#       except 异常类型:    出事后怎么补救 ← 处理完，从 except 后面继续跑
#
# 【重点】try 里「出事那一行之后」的代码不会执行，直接跳到 except。
# 【注意】except 后面必须写异常类型，不写类型等于什么都抓（知识点 6 讲危害）。

def safe_divide(a, b):
    """安全除法：除数为 0 时返回 None，而不是让程序崩溃。"""
    try:
        return a / b                    # 唯一有风险的一行
    except ZeroDivisionError:           # 只接「除以 0」这一种错
        print("  提示：除数不能为 0")    # 给使用者一个看得懂的提示
        return None                     # 出错时返回明确的值，调用方好判断


print("\n--- 2. try/except 最小骨架 ---")            # 换行 + 分节标题
print("safe_divide(10, 2) =", safe_divide(10, 2))    # 10/2，一路顺畅
print("safe_divide(10, 0) =", safe_divide(10, 0))    # 触发 except，返回 None
print("safe_divide(0, 5)  =", safe_divide(0, 5))     # 0 除以 5 合法，别误伤

# 输出：
# --- 2. try/except 最小骨架 ---
# safe_divide(10, 2) = 5.0
#   提示：除数不能为 0
# safe_divide(10, 0) = None
# safe_divide(0, 5)  = 0.0
#
# 【注意】第 2 行提示排在结果前面，因为 print 的参数要先算完才打印：
#         safe_divide 内部先执行了 except 里的 print，才轮到外层 print。


# ==============================================================================
# 知识点 3：多个 except 与 else —— 分清「哪一步错了」和「哪一步成了」
# ==============================================================================
#
# 【讲解】一个 try 里可能出好几种错，就写好几个 except，每个管一种：
#   输入 "abc" 说「不是整数」，除数是 0 说「除数不能为 0」。这比笼统地喊
#   一句「出错了」有用得多。
#
# 【注意】Python 从上往下逐个比对 except，第一个匹配上的就执行，执行完就跳出
#   整个 try/except，后面的分支不再检查。
#
# 【else 是什么】可选的一块，在 except 之后、finally 之前，只在「try 里一行都
#   没出错」时执行。它的作用是划清地盘：
#       try   = 只放可能有风险的那一步
#       else  = 成功之后的正常流程
#       except = 只负责失败补救
#   很多人把整个流程塞进 try，结果第 2、3 步的错也被同一个 except 抓住，
#   然后提示「读取失败」，可真正的错在「保存结果」—— 你会照着错方向排查半天。

def parse_score(text, divisor):
    """把文本转成数字再除以 divisor，两种错误分别处理。"""
    try:
        number = int(text)              # 可能抛 ValueError（文本不是数字）
        result = number / divisor       # 可能抛 ZeroDivisionError（除数为 0）
    except ValueError:                  # 只管「值不对」
        print(f"  「{text}」不是合法整数")
    except ZeroDivisionError:           # 只管「除以 0」
        print("  除数不能为 0")
    else:                               # try 里一行都没出错，才走这里
        print(f"  {number} / {divisor} = {result}")


print("\n--- 3. 多个 except 与 else ---")
parse_score("90", 3)                    # 正常：走 else
parse_score("abc", 3)                   # ValueError：第一个 except
parse_score("90", 0)                    # ZeroDivisionError：第二个 except

# 输出：
# --- 3. 多个 except 与 else ---
#   90 / 3 = 30.0
#   「abc」不是合法整数
#   除数不能为 0


# ==============================================================================
# 知识点 4：finally —— 无论成败都要执行的收尾
# ==============================================================================
#
# 【讲解】finally 是第四块，特点是「赖着不走」：不管 try 成功、失败、还是
#   中途 return，它一定会执行。
#
# 【什么时候用】收尾工作：关文件、断开数据库连接、释放锁。这些事「必须做」，
#   放在 finally 里最保险。
#
# 【重点】return 也拦不住 finally —— Python 会先把 finally 跑完，再真的返回。
# 【常见错误】在 finally 里写 return 会「吃掉」还没处理完的异常，让错误凭空
#   消失。finally 里只做收尾，别写 return。

print("\n--- 4. finally 一定会执行 ---")


def demo_return():
    """演示 return 之前，finally 仍会执行。"""
    try:
        print("  1. try 开始")
        return "正常返回"                # 准备返回……
    finally:
        print("  2. finally：return 也要先等我跑完")   # 但必须先执行这里


print("  函数返回值：", demo_return())   # 先打印 finally 那行，再打印返回值

# 输出：
# --- 4. finally 一定会执行 ---
#   1. try 开始
#   2. finally：return 也要先等我跑完
#   函数返回值： 正常返回


def risky():
    """演示异常向外传播时，finally 同样会执行。"""
    try:
        print("  3. risky：进入 try")
        return 1 / 0                    # 抛异常，这里没有 except
    finally:
        print("  4. risky：finally 执行（异常还没被处理）")   # 依然执行


try:
    risky()                             # 异常从 risky 里传出来
except ZeroDivisionError:               # 在这里才被接住
    print("  5. 外层捕获到 ZeroDivisionError")

# 输出：
#   3. risky：进入 try
#   4. risky：finally 执行（异常还没被处理）
#   5. 外层捕获到 ZeroDivisionError


# ==============================================================================
# 知识点 5：异常类型层次与 except 的顺序
# ==============================================================================
#
# 【讲解】Python 的异常全都是类，而且排成一棵继承树：
#
#       BaseException
#       ├── SystemExit                退出程序
#       ├── KeyboardInterrupt         你按了 Ctrl+C
#       └── Exception                 ← 日常业务异常都在这下面
#           ├── ArithmeticError → ZeroDivisionError
#           ├── LookupError
#           │   ├── KeyError          字典没有这个键
#           │   └── IndexError        列表没有这个下标
#           ├── OSError → FileNotFoundError
#           └── ValueError / TypeError / ...
#
# 【重点】except 父类 = 连子类一起抓。except LookupError 能同时接住 KeyError
#   和 IndexError。except Exception 能接住 99% 的普通错误，但接不住 Ctrl+C ——
#   这是好事，你不该把用户主动按 Ctrl+C 也当成程序 bug 处理掉。
#
# 【重点】except 是「从上往下、先中先赢」。父类写前面会拦住后面所有具体分支，
#   所以顺序必须「具体在前、笼统在后」，像医院分诊：先专科，最后才全科。

print("\n--- 5. 异常类型层次（MRO）---")
# __mro__ 是方法解析顺序，也就是这条继承链，从自己一直排到 object
for cls in [ZeroDivisionError, FileNotFoundError, KeyError, IndexError,
            ValueError, Exception, BaseException]:
    print("  " + " → ".join(c.__name__ for c in cls.__mro__))   # 拼成 A → B → C

# 输出：
# --- 5. 异常类型层次（MRO）---
#   ZeroDivisionError → ArithmeticError → Exception → BaseException → object
#   FileNotFoundError → OSError → Exception → BaseException → object
#   KeyError → LookupError → Exception → BaseException → object
#   IndexError → LookupError → Exception → BaseException → object
#   ValueError → Exception → BaseException → object
#   Exception → BaseException → object
#   BaseException → object
#
# 【看点】FileNotFoundError 的爸爸是 OSError，不是 Exception 的直系儿子。
#   所以 except Exception（爷爷）和 except OSError（爸爸）都能抓到它。

print("\n  用父类捕获子类：")
try:
    {}["a"]                             # 空字典取键 → KeyError
except LookupError as e:                # 用 KeyError 的父类接
    print("    LookupError 抓住 KeyError：", e)
    print("    注意 KeyError 打印键名会带引号，这是它的特色")

try:
    {}["x"]                             # 触发 KeyError
except Exception:                       # ❌ 笼统的写在最前面，抢先匹配
    print("  ❌ 被 Exception 抢先抓住，下面的 KeyError 分支成了摆设")
except KeyError:                        # 这行是「死代码」
    print("  这行永远不会执行")

try:
    {}["x"]                             # 同样的错误
except KeyError:                        # ✅ 具体的先上
    print("  ✅ 具体异常 KeyError 先接住了")
except Exception:                       # ✅ 笼统的放最后兜底
    print("  ✅ 兜底的 Exception 放在最后")

# 输出：
#   用父类捕获子类：
#     LookupError 抓住 KeyError： 'a'
#     注意 KeyError 打印键名会带引号，这是它的特色
#   ❌ 被 Exception 抢先抓住，下面的 KeyError 分支成了摆设
#   ✅ 具体异常 KeyError 先接住了


# ==============================================================================
# 知识点 6：别把异常吞掉，也别让 try 兜得太宽
# ==============================================================================
#
# 【讲解】新手最爱写这种代码：
#       try:
#           干活
#       except:
#           pass          # ❌ 出错了，但一声不吭
#   这叫「吞异常」。后果是：程序明明出问题了，日志里却什么都没有，
#   你只能对着错误的结果发呆，完全不知道从哪查。
#
# 【重点】三种写法的区别：
#       except: pass                    最差 —— 连 Ctrl+C 都吞，还没线索
#       except Exception: pass          差   —— 至少不吞 Ctrl+C，照样没线索
#       except Exception as e: ...      好   —— 记下类型和消息再决定怎么办
#
# 【另一个坏习惯】try 包得太大。范围越大，except 越可能抓到「不该由它负责」的错误，
#   提示就会张冠李戴（下面 bad_scope 就是反例）。标准：这行真会抛这个异常吗？

print("\n--- 6. 别吞异常 / 别让 try 兜太宽 ---")


def silent_fail(text):
    """❌ 反面教材：出错了一声不吭。"""
    try:
        return int(text)
    except ValueError:
        pass                            # 吞掉异常，什么都不说


def loud_fail(text):
    """✅ 正确做法：至少留下能排查的线索。"""
    try:
        return int(text)
    except ValueError as e:
        print(f"  [警告] 无法把 {text!r} 转成整数：{e}")   # 说清哪句话、什么原因
        return None                     # 再给调用方一个明确结果


print("  silent_fail('abc') =", silent_fail("abc"), " ← 调用方只拿到 None，不知道为什么")
print("  loud_fail('abc')   =", loud_fail("abc"))

# 输出：
# --- 6. 别吞异常 / 别让 try 兜太宽 ---
#   silent_fail('abc') = None  ← 调用方只拿到 None，不知道为什么
#   [警告] 无法把 'abc' 转成整数：invalid literal for int() with base 10: 'abc'
#   loud_fail('abc')   = None


def bad_scope():
    """反例：try 范围太大，兜底的 except 写错了方向。"""
    try:
        number = int("8")               # 这一步成功了
        names = ["Alice", "Bob"]        # 只有两个元素
        print("  取到：", names[number])  # ❌ 真正出错的是这里：索引 8 越界
    except ValueError:                  # 这个 except 接不住 IndexError
        print("  ❌ 输入不是数字")        # 这句提示永远不会打印


print("  --- 反例：try 包太大 ---")
try:
    bad_scope()                         # 内层没接住，异常继续往外传
except IndexError as e:                 # 由外层接住，程序才没崩
    print("  外层抓到 IndexError：", e)
    print("  ↑ 你以为处理了输入问题，其实程序崩在列表越界上")

# 输出：
#   --- 反例：try 包太大 ---
#   外层抓到 IndexError： list index out of range
#   ↑ 你以为处理了输入问题，其实程序崩在列表越界上

print("\n  异常对象里到底有什么：")
try:
    int("abc")                          # 故意制造一个 ValueError
except ValueError as e:                 # e 就是这个异常对象
    print("  type(e).__name__ :", type(e).__name__)   # 类名，写日志最常用
    print("  str(e)           :", str(e))             # 给人看的错误消息
    print("  repr(e)          :", repr(e))            # 给开发者看的完整形式
    print("  e.args           :", e.args)             # 原始参数元组

# 输出：
#   异常对象里到底有什么：
#   type(e).__name__ : ValueError
#   str(e)           : invalid literal for int() with base 10: 'abc'
#   repr(e)          : ValueError("invalid literal for int() with base 10: 'abc'")
#   e.args           : ("invalid literal for int() with base 10: 'abc'",)
#
# 【为什么】写日志用 f"{type(e).__name__}: {e}"，既有类型又有消息；只 print 一句
#   「出错了」，等于把破案线索全部销毁。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 异常是 Python 上报错误的机制；没人接住，程序才会带着 Traceback 退出
# 2. try 放有风险的代码，except 放补救；try 里出事那行之后的代码不再执行
# 3. 一个 try 可配多个 except，每种错误给不同提示；匹配规则是先中先赢
# 4. else 只在 try 没出错时执行，用来划清「正常路径」和「补救路径」
# 5. finally 无论如何都执行（return 也拦不住），专放收尾；别在 finally 里 return
# 6. 异常是继承树：ZeroDivisionError → ArithmeticError → Exception → BaseException
# 7. except 父类会连子类一起抓，所以顺序必须「具体在前、笼统在后」
# 8. 别吞异常；至少记下 type(e).__name__ 和 str(e)，否则等于销毁证据
# 9. try 范围越小越好，只罩住真正有风险的那一行，错误归因才清楚


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写 get_average(numbers)，传入空列表时捕获错误并提示「列表不能为空」，
#         返回 None。提示：用 try/except 包住 sum() / len() 那一步。
#
# 练习 2：写 calculate(a, b, op) 支持加减乘除，用三个 except 分别处理
#         ZeroDivisionError、TypeError（传了字符串）和兜底的 Exception。
#
# 练习 3：写一个函数，打印 1(try) / 2(else) / 3(finally)，然后在 try 里故意
#         抛 ValueError，观察哪几行不再打印、顺序如何变化。
#
# 练习 4：解释为什么下面这段代码里的 except KeyError 永远执行不到：
#             try: data["x"]                ← 触发 KeyError
#             except Exception: print("A")  ← 却被这里抢先抓住
#             except KeyError: print("B")   ← 死代码
#
# 【下一步】02_常见异常与调试.py
# ==============================================================================
