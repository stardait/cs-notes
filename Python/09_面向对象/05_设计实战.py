"""
================================================================================
第 9 章 · 面向对象
文件 05：设计实战
================================================================================

【学习目标】
    1. 用类写一个银行账户：属性保护、存款、取款、流水记录
    2. 用类管理学生成绩：增删查、平均分、排名
    3. 用类实现栈（Stack）和队列（Queue），理解「接口一致、实现不同」
    4. 理解「组合优于继承」，学会用组合搭出更灵活的结构

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一个完整的小项目
    - 「输出」块是运行后的实际结果，代码下面的注释说明「这行为什么这么写」
    - 直接运行：python 05_设计实战.py

【前置知识】
    - 前四个文件：class、self、@property、继承、魔术方法
    - 第 4 章：列表；第 5 章：字典
================================================================================
"""

# ==============================================================================
# 知识点 1：实战 —— 银行账户类
# ==============================================================================
#
# 【需求】账户有 owner 和 balance；支持 deposit / withdraw；余额不能被外部
#   改成负数；每笔操作都要留流水。
#
# 【设计思路】balance 用 @property 保护，只允许通过 deposit / withdraw 修改；
#   流水列表必须在 __init__ 里创建（否则会被所有账户共享！）；
#   操作失败时抛异常，让调用方明确知道「这次没成功」。

class BankAccount:
    """银行账户：演示封装与属性保护。"""

    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance             # 真正的余额，只通过属性访问
        self.history = []                   # 【重点】流水必须在 __init__ 里建

    @property
    def balance(self):
        """只读属性：外部只能看，不能直接赋值。"""
        return self._balance

    def deposit(self, amount):
        """存款。金额不合法就抛异常，不改状态。"""
        if amount <= 0:
            raise ValueError(f"存款金额必须大于 0，收到：{amount}")
        self._balance += amount
        self.history.append(f"存入 {amount} 元")     # 记一笔流水
        return self._balance

    def withdraw(self, amount):
        """取款。余额不足就抛异常，不改任何状态。"""
        if amount <= 0:
            raise ValueError(f"取款金额必须大于 0，收到：{amount}")
        if amount > self._balance:
            raise ValueError(f"余额不足：想取 {amount}，只有 {self._balance}")
        self._balance -= amount
        self.history.append(f"取出 {amount} 元")
        return self._balance


acc = BankAccount("张三", 100)
print("--- 银行账户基本操作 ---")
print(f"开户余额：{acc.balance}，存 50 后：{acc.deposit(50)}，取 30 后：{acc.withdraw(30)}")
print(f"流水：{acc.history}")

# 输出：
# --- 银行账户基本操作 ---
# 开户余额：100，存 50 后：150，取 30 后：120
# 流水：['存入 50 元', '取出 30 元']
#
# 【重点】balance 是只读属性，history 记下了每一笔 —— 数据和行为都在类里。
print("\n--- 保护的边界：这些操作都会被拦住 ---")# 三组「调皮的调用」，每一个都应该失败，且余额不变
cases = [("直接改余额", lambda: setattr(acc, "balance", 999999)),
         ("取太多", lambda: acc.withdraw(10000)),
         ("存负数", lambda: acc.deposit(-50))]
for i, (label, action) in enumerate(cases, start=1):
    try:
        action()
    except (AttributeError, ValueError) as e:
        print(f"{i}) {label}：{type(e).__name__}: {e}")
print(f"折腾一圈，余额还是：{acc.balance}")

# 输出：
# --- 保护的边界：这些操作都会被拦住 ---
# 1) 直接改余额：AttributeError: property 'balance' of 'BankAccount' object has no setter
# 2) 取太多：ValueError: 余额不足：想取 10000，只有 120
# 3) 存负数：ValueError: 存款金额必须大于 0，收到：-50
# 折腾一圈，余额还是：120
#
# 【重点】三次非法操作全被拒绝，余额一分没动 —— 这就是「让对象永远处于
#         合法状态」的价值。如果 balance 是公开属性，
#         别人一句 acc.balance = -999 就把账搞乱了。
#
# 【常见错误】如果写成类属性 history = []，两个账户会共用同一个列表，
#             一个人存的钱会出现在另一个人的流水里（02 文件讲过的坑）。


# ==============================================================================
# 知识点 2：实战 —— 学生成绩管理
# ==============================================================================
#
# 【需求】GradeBook 管理多个学生；支持添加、按名查找、平均分、排名。
# 【设计思路】Student 只管「一个学生」，GradeBook 管「一群学生」，
#   组合在这里天然出现：GradeBook 里装着一堆 Student 对象。

class Student:
    """单个学生。"""

    def __init__(self, name, score):
        self.name = name
        self.score = score

    def is_pass(self):
        return self.score >= 60

    def __repr__(self):
        return f"{self.name}({self.score})"


class GradeBook:
    """成绩册：管理一群学生。"""

    def __init__(self):
        self.students = []              # 组合：里面装的是 Student 对象

    def add(self, name, score):
        """添加学生。分数范围做校验。"""
        if not 0 <= score <= 100:
            raise ValueError(f"分数必须在 0~100 之间，收到：{score}")
        self.students.append(Student(name, score))

    def find(self, name):
        """按名字查找，找不到返回 None。"""
        for s in self.students:
            if s.name == name:
                return s
        return None
    def average(self):
        """平均分。空成绩册返回 0，避免除零错误。"""
        if not self.students:
            return 0
        return round(sum(s.score for s in self.students) / len(self.students), 2)

    def ranking(self):
        """按分数从高到低排名。"""
        return sorted(self.students, key=lambda s: s.score, reverse=True)


book = GradeBook()
for name, score in [("张三", 92), ("李四", 55), ("王五", 78), ("赵六", 88)]:
    book.add(name, score)

print("\n--- 学生成绩管理 ---")
print(f"全部学生：{book.students}")
print(f"平均分：{book.average()}，第一名：{book.ranking()[0]}")
print(f"找王五：{book.find('王五')}，找不存在的人：{book.find('孙七')}")

# 输出：
# --- 学生成绩管理 ---
# 全部学生：[张三(92), 李四(55), 王五(78), 赵六(88)]
# 平均分：78.25，第一名：张三(92)
# 找王五：王五(78)，找不存在的人：None
#
# 【重点】book.add("王五", 78) 传进去的是姓名和分数两个「原始数据」，
#         但 add 内部把它们变成了 Student 对象 —— 对外简单，对内规范。

print("\n--- 统计与排名 ---")
for rank, s in enumerate(book.ranking(), start=1):
    status = "及格" if s.is_pass() else "不及格"
    print(f"  第 {rank} 名：{s.name} {s.score} 分（{status}）")
print(f"及格人数：{sum(1 for s in book.students if s.is_pass())}")
try:
    book.add("坏人", 120)
except ValueError as e:
    print(f"加 120 分：ValueError: {e}")

# 输出：
# --- 统计与排名 ---
#   第 1 名：张三 92 分（及格）
#   第 2 名：赵六 88 分（及格）
#   第 3 名：王五 78 分（及格）
#   第 4 名：李四 55 分（不及格）
# 及格人数：3
# 加 120 分：ValueError: 分数必须在 0~100 之间，收到：120
#
# 【注意】sum(1 for s in ... if ...) 是统计个数的常用写法，比
#         len([s for s in ... if ...]) 更省内存（不建中间列表）。


# ==============================================================================
# 知识点 3：实战 —— 用类实现栈和队列
# ==============================================================================
#
# 【讲解】栈（Stack）后进先出（LIFO），像一摞盘子，最后放上去的最先拿走；
#   队列（Queue）先进先出（FIFO），像排队买奶茶，先来的先服务。
#
# 【重点】两者对外接口几乎一样（push/pop/peek/size），但内部不同：栈用 list，
#         尾部进出是 O(1)；队列若用 list.pop(0) 要挪动整个列表，是 O(n)。
#         所以队列用 collections.deque，两端都是 O(1)。这就是「接口一致、
#         实现不同」的典型设计。

from collections import deque       # deque：双端队列，专为队列设计


class Stack:
    """栈：后进先出。"""

    def __init__(self):
        self._items = []            # 下划线表示「内部数据，别直接碰」

    def push(self, item):
        self._items.append(item)    # 从尾部放

    def pop(self):
        """弹出栈顶元素。空栈时抛 IndexError。"""
        if not self._items:
            raise IndexError("空栈不能 pop")
        return self._items.pop()    # 从尾部取

    def peek(self):
        """看一眼栈顶，但不拿走。"""
        if not self._items:
            raise IndexError("空栈没有栈顶")
        return self._items[-1]

    def size(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items})"


class Queue:
    """队列：先进先出。"""

    def __init__(self):
        self._items = deque()       # 【重点】用 deque，而不是 list

    def enqueue(self, item):
        self._items.append(item)    # 从尾部加入

    def dequeue(self):
        """取出队首元素。空队列时抛 IndexError。"""
        if not self._items:
            raise IndexError("空队列不能 dequeue")
        return self._items.popleft()    # 从头部取出，O(1)

    def peek(self):
        """看一眼队首，但不拿走。"""
        if not self._items:
            raise IndexError("空队列没有队首")
        return self._items[0]

    def size(self):
        return len(self._items)

    def __repr__(self):
        return f"Queue({list(self._items)})"


print("\n--- 栈：后进先出 ---")
stack = Stack()
for ch in "ABCD":
    stack.push(ch)
print(f"依次放入 A B C D：{stack}，大小 {stack.size()}，peek 一下：{stack.peek()}")
print(f"pop 出：{stack.pop()}，再 pop 出：{stack.pop()}，剩下：{stack}")

# 输出：
# --- 栈：后进先出 ---
# 依次放入 A B C D：Stack(['A', 'B', 'C', 'D'])，大小 4，peek 一下：D
# pop 出：D，再 pop 出：C，剩下：Stack(['A', 'B'])

print("\n--- 队列：先进先出 ---")
queue = Queue()
for ch in "ABCD":
    queue.enqueue(ch)
print(f"依次排入 A B C D：{queue}，大小 {queue.size()}，peek 一下：{queue.peek()}")
print(f"dequeue 出：{queue.dequeue()}，再出：{queue.dequeue()}，剩下：{queue}")

# 输出：
# --- 队列：先进先出 ---
# 依次排入 A B C D：Queue(['A', 'B', 'C', 'D'])，大小 4，peek 一下：A
# dequeue 出：A，再出：B，剩下：Queue(['C', 'D'])
#
# 【重点】同样的输入 A B C D，栈取出的是 D→C，队列取出的是 A→B。
#         这就是「后进先出」和「先进先出」的直观差别。
#
# 【常见错误】空容器要明确约定怎么办。这里选择抛异常而不是返回 None ——
#         因为 None 也可能是正常数据，用它表示「出错」会让调用方分不清。

# ==============================================================================
# 知识点 4：组合优于继承 —— 一个能换零件的机器人
# ==============================================================================
#
# 【讲解】如果 Robot 有 2 种走路方式（轮子、腿）和 2 种武器（激光、火箭），
#   用继承要做 WheelRobot、LegRobot……再叠加武器，类就爆炸成 2×2=4 个，
#   而且一旦造出来就是「那个类」，中途不能改。用组合就简单了：
#   让 Robot 持有两个零件对象，想换就换，不用新建类。
#
# 【重点】继承是「运行时不能改」的，组合是「运行时能换」的。

class WheelLegs:
    def move(self):
        return "用轮子滚过去"


class WalkerLegs:
    def move(self):
        return "用两条腿走过去"


class Laser:
    def attack(self):
        return "发射激光"


class Rocket:
    def attack(self):
        return "发射火箭弹"


class Robot:
    """机器人：自己不会走也不会打，全交给装进来的零件。"""

    def __init__(self, name, legs, weapon):
        self.name = name
        self.legs = legs            # 组合：装一个「会走的」零件
        self.weapon = weapon        # 组合：装一个「会打的」零件

    def move(self):
        return f"{self.name} {self.legs.move()}"

    def attack(self):
        return f"{self.name} {self.weapon.attack()}"


print("\n--- 组合：装不同零件，得到不同行为 ---")
robot_a = Robot("机器人 A", WheelLegs(), Laser())
robot_b = Robot("机器人 B", WalkerLegs(), Rocket())
print(f"A 移动：{robot_a.move()}；A 攻击：{robot_a.attack()}")
print(f"B 移动：{robot_b.move()}；B 攻击：{robot_b.attack()}")

# 输出：
# --- 组合：装不同零件，得到不同行为 ---
# A 移动：机器人 A 用轮子滚过去；A 攻击：机器人 A 发射激光
# B 移动：机器人 B 用两条腿走过去；B 攻击：机器人 B 发射火箭弹

print("\n--- 组合的杀手锏：运行时换零件 ---")
print(f"换之前：{robot_a.move()}")
robot_a.legs = WalkerLegs()             # 直接把轮子换成腿，继承做不到
print(f"换腿后：{robot_a.move()}")

# 输出：
# --- 组合的杀手锏：运行时换零件 ---
# 换之前：机器人 A 用轮子滚过去
# 换腿后：机器人 A 用两条腿走过去
#
# 【重点】如果 robot_a 是 WheelRobot 的实例，它这辈子只能滚。用组合，
#         同一个对象可以「先滚后走」，这就是灵活性。
# 【注意】组合也有代价：Robot 自己不会走路，得靠零件。如果零件接口不统一
#         （有的叫 move 有的叫 run），就得在 Robot 里做适配。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. 银行账户：用 @property 保护 balance，流水列表在 __init__ 里创建
# 2. 非法操作要「拒绝 + 报错」：抛 ValueError / AttributeError，别默默返回 None
# 3. 成绩册：Student 管一个学生，GradeBook 管一群，这是天然的组合结构
# 4. average() 要先判断空列表，否则 ZeroDivisionError；排名用 sorted(key=...)
# 5. 栈是 LIFO，用 list 尾部进出；队列是 FIFO，用 deque（list.pop(0) 是 O(n)）
# 6. 空容器要明确约定：抛异常比返回 None 更清晰
# 7. 组合优于继承：类爆炸时用组合；需要运行时替换行为时用组合
# 8. 写类顺序：数据 → 方法 → 保护 → 再考虑继承还是组合；类名要一看就懂


# ==============================================================================
# 【动手练习】
# ==============================================================================#
# 练习 1：给 BankAccount 增加 transfer(other, amount) 方法，
#         从自己转账给别人。要求：余额不足时报错，双方流水都要记录。
#
# 练习 2：给 GradeBook 增加 remove(name) 和 top_n(n)：
#         remove 删掉指定学生（不存在时返回 False），top_n 返回前 n 名。
#
# 练习 3：用 Stack 实现「括号匹配检查」：给定字符串 "((a+b)*c)" 返回 True，
#         "((a+b)" 返回 False。提示：遇到左括号入栈，右括号出栈。
#
# 练习 4：把 Robot 改造成「有耐久度的机器人」：加 health 属性，
#         attack() 时返回伤害值，受击时 health 减少。
#
# 【下一步】第 10 章：迭代器与生成器
# ==============================================================================