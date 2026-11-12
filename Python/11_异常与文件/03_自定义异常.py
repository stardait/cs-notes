"""
================================================================================
第 11 章 · 异常与文件
文件 03：自定义异常
================================================================================

【学习目标】
    1. 明白内置异常不够用时，为什么要自己定义异常
    2. 学会继承 Exception 写自定义异常类，并给它带上业务信息
    3. 用继承层次把项目异常组织成一棵树
    4. 掌握 raise 抛异常、raise 重抛，以及 raise ... from ... 异常链
    5. 判断「什么时候应该抛异常」，而不是返回 None 或 False

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 本文件用「银行账户」的小例子贯穿，越读越有画面感
    - 「输出」块是运行后的实际结果
    - 直接运行：python 03_自定义异常.py

【前置知识】
    - 文件 01：try / except / finally
    - 第 9 章：类的定义、继承、super()
================================================================================
"""

# ==============================================================================
# 知识点 1：为什么需要自定义异常
# ==============================================================================
#
# 【讲解】内置异常只描述「底层发生了什么」：ValueError 是「值不合法」、KeyError
#   是「键不存在」，却不告诉你「业务上是什么问题」。用户取钱时余额不足，你抛
#   ValueError，调用方只能猜；抛 InsufficientBalanceError，一眼就懂。
#
# 【类比】内置异常像医院的「内科 / 外科」分诊，自定义异常像「心内科 / 消化内科」。
# 【重点】三个好处：名字本身就是文档；能被精准 except；能携带业务数据。

print("=== 1. 为什么需要自定义异常 ===")

# 内置异常的问题是「太笼统」：同一个 ValueError 可能对应十种业务问题
try:
    raise ValueError("余额不足")        # 消息是人话，类型却不是
except ValueError as e:
    print("  内置异常：", type(e).__name__, "| 消息：", e, "| 只能靠字符串判断业务问题")

# 输出：
# === 1. 为什么需要自定义异常 ===
#   内置异常： ValueError | 消息： 余额不足 | 只能靠字符串判断业务问题


# ==============================================================================
# 知识点 2：最简单的自定义异常 —— 一行就够
# ==============================================================================
#
# 【讲解】自定义异常就是普通类，只要继承 Exception：
#       class BalanceError(Exception):
#           pass
#   Exception 已经实现了所有该有的行为：能被 raise、能被 except、能被 str() 打印。
#
# 【重点】一定继承 Exception，不要继承 BaseException！后者是给系统级退出用的
#   （KeyboardInterrupt、SystemExit），继承它会让别人的 `except Exception` 抓不到
#   你的异常 —— 出了事没人管。
# 【命名规范】异常类名以 Error 结尾（ConfigError、ValidationError），与内置风格一致。
# 【注意】raise 后面可以跟类也可以跟实例：raise BalanceError 会自动实例化，
#   raise BalanceError("余额不足") 更推荐 —— 带上能说清问题的消息。

print("\n--- 2. 最简单的自定义异常 ---")


class BalanceError(Exception):
    """账户相关的错误（最简版：什么都不用写）。"""


print("  BalanceError 的父类：", BalanceError.__bases__[0].__name__)

try:
    raise BalanceError("余额不足")       # 像内置异常一样抛
except BalanceError as e:               # 也像内置异常一样接
    print("  捕获到：", e)
    print("  类型：", type(e).__name__)

# 输出：
# --- 2. 最简单的自定义异常 ---
#   BalanceError 的父类： Exception
#   捕获到： 余额不足
#   类型： BalanceError


# ==============================================================================
# 知识点 3：给异常带上「业务数据」
# ==============================================================================
#
# 【讲解】异常对象就是普通对象，可以存任何东西。重写 __init__ 把关键数据存成
#   属性，调用方 catch 到之后直接读，不用去解析消息字符串。
#
# 【重点】__init__ 里必须调用 super().__init__(消息)！str(e) 打印的是父类保存的
#   args，你不调用 super().__init__，父类就不知道消息是什么。
# 【常见错误】只写 self.msg = msg 却忘了 super().__init__()，于是 str(e) 打印的
#   是构造时的原始参数元组（像 "('age', 'abc')"），而不是你想要的那句话。

print("\n--- 3. 给异常带上业务数据 ---")


class ValidationError(Exception):
    """校验失败：记下哪个字段、什么值、为什么不合法。"""

    def __init__(self, field, value, reason):
        self.field = field              # 出问题的字段名
        self.value = value              # 用户实际给的值
        self.reason = reason            # 为什么不合法
        super().__init__(f"字段 {field} 校验失败：{reason}（值为 {value!r}）")


try:
    raise ValidationError("age", "abc", "必须是整数")
except ValidationError as e:
    print("  消息：", e)                 # super().__init__ 存的那句话
    print("  e.field  =", e.field)       # 调用方能直接读字段名
    print("  e.value  =", e.value)
    print("  e.args   =", e.args)        # 父类保存的原始参数

# 输出：
# --- 3. 给异常带上业务数据 ---
#   消息： 字段 age 校验失败：必须是整数（值为 'abc'）
#   e.field  = age
#   e.value  = abc
#   e.args   = ("字段 age 校验失败：必须是整数（值为 'abc'）",)


# ==============================================================================
# 知识点 4：把异常组织成一棵树
# ==============================================================================
#
# 【讲解】建一个「项目异常基类」，业务异常都继承它，调用方就能自己选粒度：
#       except BankError:              拦住所有银行相关的业务错误
#       except AccountNotFoundError:   只处理「账户不存在」这一种
# 【重点】基类只负责分类，不写业务逻辑；具体信息放子类。以后新增错误只需加子类，
#   老代码一行都不用改。这就是文件 01 讲的「父类能抓子类」的实战价值。

print("\n--- 4. 异常继承树 ---")


class BankError(Exception):
    """本模块所有银行相关异常的基类。"""


class AccountNotFoundError(BankError):
    """账户不存在。"""

    def __init__(self, account_id):
        self.account_id = account_id    # 记下是哪个账户
        super().__init__(f"账户 {account_id} 不存在")


class InsufficientBalanceError(BankError):
    """余额不足。"""

    def __init__(self, needed, available):
        self.needed = needed            # 需要多少钱
        self.available = available      # 账上有多少钱
        super().__init__(f"需要 {needed} 元，可用 {available} 元，还差 {needed - available} 元")


print("  InsufficientBalanceError 的继承链：")
for cls in InsufficientBalanceError.__mro__:      # 从自己一路往上数
    print("    " + cls.__name__)

# 输出：
# --- 4. 异常继承树 ---
#   InsufficientBalanceError 的继承链：
#     InsufficientBalanceError
#     BankError
#     Exception
#     BaseException
#     object
#
# 【看点】它同时是 BankError 和 Exception，所以三种 except 都能接住它。


# ==============================================================================
# 知识点 5：raise —— 主动抛出异常
# ==============================================================================
#
# 【讲解】两种用法：raise 异常对象 主动报错；except 里单独一个 raise 表示「重抛」，
#   把当前异常原样再扔出去。有时你只想记一句日志，处理不了这个错，就必须继续往
#   外扔，否则调用方会以为一切正常。
# 【重点】raise 不带参数时会保留原来的 Traceback，错误现场不会丢。

print("\n--- 5. raise 主动抛出异常 ---")


def withdraw(balance, amount):
    """取钱：金额非法抛 ValueError，余额不够抛 InsufficientBalanceError。"""
    if amount <= 0:
        raise ValueError(f"取款金额必须大于 0，收到 {amount}")
    if balance < amount:
        raise InsufficientBalanceError(amount, balance)
    return balance - amount


print("  withdraw(100, 30) =", withdraw(100, 30))     # 正常取款

try:
    withdraw(100, -5)                   # 金额非法
except ValueError as e:
    print("  金额非法 →", type(e).__name__, ":", e)

try:
    withdraw(100, 200)                  # 余额不足；这次用父类 BankError 接
except BankError as e:
    print("  余额不足 →", e)
    print("    需要：", e.needed, "元；可用：", e.available, "元")
    print("    用父类接也能拿到子类的属性：", type(e).__name__)

# 输出：
# --- 5. raise 主动抛出异常 ---
#   withdraw(100, 30) = 70
#   金额非法 → ValueError : 取款金额必须大于 0，收到 -5
#   余额不足 → 需要 200 元，可用 100 元，还差 100 元
#     需要： 200 元；可用： 100 元
#     用父类接也能拿到子类的属性： InsufficientBalanceError


def load_user(user_id):
    """内层：假装查数据库，查不到就抛异常。"""
    if user_id != 1:
        raise AccountNotFoundError(user_id)
    return {"id": 1, "name": "Alice"}


def get_user_safe(user_id):
    """外层：只记一句日志，然后把异常原样再扔出去。"""
    try:
        return load_user(user_id)
    except AccountNotFoundError:
        print("  [日志] 有人查了一个不存在的账户，已记录")
        raise                           # 重抛：保留原始 Traceback

try:
    get_user_safe(99)                   # 会一路抛出来
except AccountNotFoundError as e:
    print("  外层最终捕获：", e)

# 输出：
#   [日志] 有人查了一个不存在的账户，已记录
#   外层最终捕获： 账户 99 不存在


# ==============================================================================
# 知识点 6：raise from —— 异常链，保留「真正的原因」
# ==============================================================================
#
# 【讲解】底层抛 ValueError，你在上层包装成 ConfigError，会丢掉「底层为什么错」。
#   用 raise ConfigError("...") from e 把两个异常链起来，Traceback 里会多一行
#   The above exception was the direct cause of the following exception。
# 【重点】Python 会自动记录 __context__（处理 A 时又出了 B，关系模糊）；用 from
#   显式指定 __cause__，因果才清楚。确定底层细节对使用者无意义时，用 from None
#   掐断链条，Traceback 会干净很多。

print("\n--- 6. raise from 异常链 ---")


class ConfigError(Exception):
    """配置项有问题。"""


def load_port(text, chain=False):
    """把文本转成端口号；chain=True 时用 from 挂上原始的 ValueError。"""
    try:
        return int(text)
    except ValueError as e:
        message = f"配置项 port 不合法：{text!r}"
        if chain:
            raise ConfigError(message) from e    # ✅ 记录「谁导致的」
        raise ConfigError(message)              # ❌ 原始错误被掩盖

for chain in (False, True):
    try:
        load_port("abc", chain=chain)
    except ConfigError as e:
        cause = type(e.__cause__).__name__ if e.__cause__ else "None"
        print(f"  chain={str(chain):5} cause = {cause:10} context = {type(e.__context__).__name__}")

# 输出：
# --- 6. raise from 异常链 ---
#   chain=False cause = None       context = ValueError
#   chain=True  cause = ValueError context = ValueError
#
# 【怎么看】两种情况都保留了底层 ValueError（__context__），但只有用了 from，
#   __cause__ 才指向它。不加 from 时 Traceback 写的是「During handling of the
#   above exception, another exception occurred」，加了 from 才是「direct cause」。


def load_port_silent(text):
    """from None：主动切断链条，只给使用者看最终结论。"""
    try:
        return int(text)
    except ValueError:
        raise ConfigError(f"配置项 port 不合法：{text!r}") from None


try:
    load_port_silent("abc")
except ConfigError as e:
    print("  from None → cause =", e.__cause__, "| context 被抑制 =", e.__suppress_context__)

# 输出：
#   from None → cause = None | context 被抑制 = True


# ==============================================================================
# 知识点 7：什么时候「应该」抛异常
# ==============================================================================
#
# 【讲解】函数有三种方式告诉调用方「出问题了」：
#   1. 返回 None / False      适合「查不到是正常结果」：字典 get、列表 find
#   2. 返回 (是否成功, 数据)   适合「失败很常见、调用方必须处理」：老式 C 风格
#   3. 抛异常                 适合「约定无法完成，继续往下跑会出错」
#
# 【什么时候该抛】✔ 参数不合法（金额为负）；✔ 状态不对（账户已冻结）；✔ 依赖不可用
#   （文件不存在、网络断了）；✘ 别用它做普通流程控制，能用 if 就用 if。
# 【重点】返回值风格最大的问题是「容易被忽略」：调用方忘了检查 None，程序就带着
#   None 一路往下跑，最后在很远的地方崩掉，现场早丢了。异常无法被忽略。
# 【类比】返回 None 像「在门口贴张纸条说我不在」；抛异常像「当面告诉你我来不了」。

print("\n--- 7. 什么时候该抛异常 ---")


def find_user_silent(users, name):
    """❌ 返回 None：调用方忘了检查就会在后面炸掉。"""
    return users.get(name)


def find_user_strict(users, name):
    """✅ 找不到就抛异常：错误在源头暴露。"""
    if name not in users:
        raise AccountNotFoundError(name)
    return users[name]


users = {"Alice": {"id": 1, "age": 20}}

found = find_user_silent(users, "Bob")               # 返回 None
print("  silent 版本找到的：", found)
try:
    print("  然后访问 found['age']：", found["age"])  # 错误被推迟到这里才爆
except TypeError as e:
    print("  ❌ 在几行之后才炸：", e, " ← 看不出是「用户不存在」导致的")

try:
    find_user_strict(users, "Bob")                   # 源头就炸，原因明确
except AccountNotFoundError as e:
    print("  ✅ 在源头就炸，原因清楚：", e)

# 输出：
# --- 7. 什么时候该抛异常 ---
#   silent 版本找到的： None
#   ❌ 在几行之后才炸： 'NoneType' object is not subscriptable  ← 看不出是「用户不存在」导致的
#   ✅ 在源头就炸，原因清楚： 账户 Bob 不存在


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 内置异常太笼统；自定义异常让「错误类型」本身就说明业务问题
# 2. 最简写法：class XxxError(Exception): pass —— 继承 Exception，别继承 BaseException
# 3. 要带数据就重写 __init__ 存属性，但务必调用 super().__init__(消息)
# 4. 建项目异常基类（如 BankError），子类各管一种，调用方粒度可粗可细
# 5. raise 异常主动报错；except 里单独一个 raise 是重抛，会保留原 Traceback
# 6. raise 新异常 from 原异常 —— 显式记录因果；from None 用于切断无意义的细节
# 7. 该抛异常的场合：参数非法、状态不对、依赖不可用；别用它做普通流程控制
# 8. 抛异常比返回 None 安全：错误在源头暴露，不会被调用方悄悄忽略
# 9. 异常类名以 Error 结尾；基类只做分类，业务信息放子类


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：定义 AgeError(Exception)，写 check_age(age)：小于 0 或大于 150 时抛出，
#         消息里要带上「你输入的是多少」。
#
# 练习 2：设计 LoginError 基类，两个子类 UserNotFoundError 和 WrongPasswordError。
#         写 login(name, pwd) 抛对应异常，并用两个 except 分别处理。
#
# 练习 3：写 safe_int(text)，内部用 int() 转换，失败时抛 DataError 并用 from 挂上
#         原始 ValueError；打印 e.__cause__ 验证链条存在。
#
# 【下一步】04_文件读写.py
# ==============================================================================
