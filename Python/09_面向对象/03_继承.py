"""
================================================================================
第 9 章 · 面向对象
文件 03：继承
================================================================================

【学习目标】
    1. 会用 class 子类(父类) 定义继承关系，理解「is-a」的含义
    2. 掌握 super() 的用法，知道它为什么比写死父类名更好
    3. 学会方法重写（override），以及什么时候该调 super()
    4. 看懂多继承和 MRO（方法解析顺序），知道菱形继承为什么不再头疼
    5. 会用 isinstance / issubclass 做类型判断

【怎么用这个文件】
    - 从上往下读，每个「知识点」是一小节
    - 「输出」块是运行后的实际结果，代码下面的注释说明「这行为什么这么写」
    - 直接运行：python 03_继承.py

【前置知识】
    - 01_类与对象.py（class、__init__、self、实例方法）
    - 02_属性与方法进阶.py（类属性、@classmethod 里的 cls）
================================================================================
"""

# ==============================================================================
# 知识点 1：继承是什么 —— 从「复制粘贴」说起
# ==============================================================================
#
# 【讲解】假设要写「猫」和「狗」两个类。它们都有名字、都会吃、都会睡，
#   只有叫声不同。最笨的写法是把吃和睡抄两遍，改一处要改两处。
#
#   继承就是把共同部分抽出来放进「父类」（基类），让「子类」（派生类）
#   自动获得这些能力，自己只写特殊的那部分。
#
# 【重点】继承表达「is-a」关系：猫「是一只」动物，所以 Cat 继承 Animal。
#         如果读起来不像「是一个」，就不该用继承（05 文件讲组合再说）。

class Animal:
    """父类：所有动物共有的部分。"""

    def __init__(self, name):
        self.name = name        # 名字，所有动物都有

    def eat(self):
        print(f"{self.name} 在吃东西")

    def speak(self):
        """父类给个默认叫声，子类可以改成自己的。"""
        print(f"{self.name} 发出了声音")


class Cat(Animal):              # 括号里写父类名，就表示「Cat 继承 Animal」
    """子类：只写自己特有的部分。"""

    def speak(self):
        print(f"{self.name}：喵～")


class Dog(Animal):
    def speak(self):
        print(f"{self.name}：汪汪！")


print("--- 子类自动拥有父类的方法 ---")
c = Cat("咪咪")
d = Dog("旺财")
c.eat()                     # eat 是从 Animal 继承来的，Cat 里根本没写
c.speak()                   # speak 是 Cat 自己重写的
d.eat()
d.speak()

# 输出：
# --- 子类自动拥有父类的方法 ---
# 咪咪 在吃东西
# 咪咪：喵～
# 旺财 在吃东西
# 旺财：汪汪！
#
# 【重点】Cat 的类体里只有 speak 一个方法，但 c.eat() 照样能调 ——
#         因为「自己找不到就往上找父类」。这就是继承省下的代码。
# 【注意】继承是单向的：子类能用父类的东西，父类用不了子类的东西。


# ==============================================================================
# 知识点 2：方法重写（override）—— 子类盖掉父类
# ==============================================================================
#
# 【讲解】子类定义与父类同名的方法，就叫「重写」。调用时优先用子类的版本。
#
# 【类比】员工手册（父类）写「请假提前 3 天」，研发部补充规定（子类）
#         改成「提前 1 天即可」。研发部的人按部门规定办。
#
# 【注意】重写要求方法名相同。名字不同就是新增方法，不是重写。

class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        """父类的默认实现：不知道具体形状，返回 0。"""
        return 0

    def describe(self):
        print(f"{self.name} 的面积是 {self.area()}")     # 注意这里调了 area()


class Square(Shape):
    def __init__(self, side):
        super().__init__("正方形")       # 先把父类那部分初始化好
        self.side = side

    def area(self):
        """重写：正方形有自己的面积公式。"""
        return self.side ** 2


print("\n--- 重写方法后，父类版本被盖住 ---")
print(f"直接调子类 area：{Square(5).area()}")
Square(5).describe()        # describe 是父类的，但它里面调的是子类的 area

# 输出：
# --- 重写方法后，父类版本被盖住 ---
# 直接调子类 area：25
# 正方形 的面积是 25
#
# 【重点】describe() 写在父类里，但它内部调用 self.area() 时，
#         用的是「运行时真实类型」Square 的版本，这就是「多态」。
#         父类写代码时不需要知道子类是谁，运行时自动找对的方法。


# ==============================================================================
# 知识点 3：super() —— 调用父类的方法
# ==============================================================================
#
# 【讲解】子类重写了 __init__ 后，父类的 __init__ 就不再自动跑了。
#   如果父类负责初始化 name，你不显式调用，name 就永远不存在。
#
#   super().__init__(...) 的意思就是「调用父类的 __init__」。
#
# 【重点】为什么写 super() 而不是 Animal.__init__(self, ...)？
#   - super() 认的是 MRO 里的「下一个」，多继承时也能正确跳转
#   - 写死类名的话，一旦调整继承关系，这行就错了
#   - 子类改父类名时不用逐行改
#
# 【两种用法】super().__init__(...) 是「补充」；super().work() 是「扩展」。

class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def work(self):
        print(f"{self.name} 在上班，月薪 {self.salary}")


class Manager(Employee):
    def __init__(self, name, salary, team_size):
        super().__init__(name, salary)      # 【重点】先让父类初始化 name 和 salary
        self.team_size = team_size          # 再初始化自己特有的属性

    def work(self):
        super().work()                      # 先做父类那件事
        print(f"  另外还管理 {self.team_size} 个人")   # 再补充子类的事


print("\n--- super() 的两大用途 ---")
m = Manager("张三", 20000, 8)
m.work()
print(f"父类的属性也在：name={m.name}，salary={m.salary}")

# 输出：
# --- super() 的两大用途 ---
# 张三 在上班，月薪 20000
#   另外还管理 8 个人
# 父类的属性也在：name=张三，salary=20000
#
# 【常见错误】子类写了 __init__ 却忘了调 super().__init__()，然后用父类属性时
#   报 AttributeError: 'xxx' object has no attribute 'name'。
#   原因就是父类的 __init__ 被重写后不再自动执行，那行赋值压根没跑过。
#
# 【延伸】super() 还会一层层往上走。三级继承 ClassC(B) 且 B(A) 时，
#         每层的 super().greet() 会依次执行 C → B → A，一个都不漏。
#         这让每个类都只执行一次，菱形继承也安全。


# ==============================================================================
# 知识点 4：多继承与 MRO —— 一个类可以有几个爸爸？
# ==============================================================================
#
# 【讲解】Python 允许一个类同时继承多个父类：class 子类(父类1, 父类2, ...)
#
#   那「调用方法时到底用谁的」？Python 用 MRO（Method Resolution Order，
#   方法解析顺序）决定：按 MRO 列表从左到右找，找到第一个就用。
#
# MRO 的规则叫「C3 线性化」，听起来吓人，记住三条就够：
#   1. 子类永远排在父类前面
#   2. 多个父类时，按「括号里的书写顺序」从左到右
#   3. 所有类最终都指向 object，它永远排最后
#
# 查看 MRO 有两个办法：类.__mro__（元组）和 类.mro()（列表）。

class A:
    def hello(self):
        return "A.hello"


class B(A):
    def hello(self):
        return "B.hello"


class C(A):
    def hello(self):
        return "C.hello"


class D(B, C):                  # 同时继承 B 和 C
    pass


print("\n--- 多继承的 MRO ---")
print([cls.__name__ for cls in D.__mro__])
print(f"调用 hello() 得到：{D().hello()}")

# 输出：
# --- 多继承的 MRO ---
# ['D', 'B', 'C', 'A', 'object']
# 调用 hello() 得到：B.hello
#
# 【重点】MRO 是 ['D', 'B', 'C', 'A', 'object']，所以 hello() 先看 D（没写），
#         再看 B（有）→ 用 B 的。C 也有 hello，但排在后面，输给了 B。
#         如果写成 class D(C, B)，MRO 就变成 D2 那样，结果改成 C.hello。
#
# 【注意】多继承的顺序会直接改变程序行为，括号里的顺序是有语义的。
#
# 【常见错误】如果两个父类的继承关系「打架」，Python 会拒绝定义这个类，报
#   TypeError: Cannot create a consistent method resolution order (MRO)。
#   例如 B 已经继承了 A，再写 class X(A, B) 就属于矛盾。


# ==============================================================================
# 知识点 5：菱形继承 —— 多继承最经典的形状
# ==============================================================================
#
# 【讲解】菱形继承：B 和 C 都继承 A，D 又同时继承 B 和 C，画出来是个菱形：
#                      A
#                    /   \
#                   B     C
#                    \   /
#                      D
#
#   别的语言（如 C++）在这里要你自己处理「A 的构造被调两次」的问题。
#   Python 用 MRO + super() 自动解决：A 只会被初始化一次。

class Root:
    def __init__(self):
        print("  Root.__init__ 执行")


class Left(Root):
    def __init__(self):
        print("  Left.__init__ 开始")
        super().__init__()          # 会跳到 MRO 里的下一个，不是无脑跳 Root


class Right(Root):
    def __init__(self):
        print("  Right.__init__ 开始")
        super().__init__()


class Diamond(Left, Right):
    def __init__(self):
        print("  Diamond.__init__ 开始")
        super().__init__()


print("\n--- 菱形继承：Root 只被初始化一次 ---")
print(f"Diamond 的 MRO：{[cls.__name__ for cls in Diamond.__mro__]}")
Diamond()

# 输出：
# --- 菱形继承：Root 只被初始化一次 ---
# Diamond 的 MRO：['Diamond', 'Left', 'Right', 'Root', 'object']
#   Diamond.__init__ 开始
#   Left.__init__ 开始
#   Right.__init__ 开始
#   Root.__init__ 执行
#
# 【重点】结果里 Root.__init__ 只打印了一次！这就是 MRO 的功劳：
#         Diamond → Left → Right → Root → object，每个类只走一次。
#         关键点是 Left 里的 super() 跳到了 Right，而不是 Root ——
#         因为 super() 认的是 MRO 表，不是「字面上的父类」。


# ==============================================================================
# 知识点 6：isinstance 和 issubclass —— 判断类型关系
# ==============================================================================
#
# 【讲解】
#   isinstance(对象, 类)    ：这个对象是这类（或它的子类）的实例吗？
#   issubclass(子类, 父类)  ：这个类是这个类的子类吗？
#
# 【重点】isinstance 会「沿继承链判断」：Cat 的对象既是 Cat 也是 Animal。
#         这一点和 type() 不同，type() 只认精确类型。

print("\n--- isinstance 与 issubclass ---")
c2 = Cat("咪咪")
print(f"c2 是 Cat 吗：{isinstance(c2, Cat)}")
print(f"c2 是 Animal 吗：{isinstance(c2, Animal)}   ← 沿继承链判断")
print(f"Animal 的对象是 Cat 吗：{isinstance(Animal('无名'), Cat)}   ← 父类不是子类")
print(f"Cat 是 Animal 的子类吗：{issubclass(Cat, Animal)}")
print(f"Animal 是 Cat 的子类吗：{issubclass(Animal, Cat)}")
print(f"Cat 是自己的子类吗：{issubclass(Cat, Cat)}     ← 算，规定如此")
print(f"type(c2) 是 Animal 吗：{type(c2) is Animal}   ← is 只认精确类型")

# 输出：
# --- isinstance 与 issubclass ---
# c2 是 Cat 吗：True
# c2 是 Animal 吗：True   ← 沿继承链判断
# Animal 的对象是 Cat 吗：False   ← 父类不是子类
# Cat 是 Animal 的子类吗：True
# Animal 是 Cat 的子类吗：False
# Cat 是自己的子类吗：True     ← 算，规定如此
# type(c2) 是 Animal 吗：False   ← is 只认精确类型
#
# 【重点】判断「是不是某类」请用 isinstance，别用 type(x) is 类名。
#         因为 isinstance 认可继承关系，type 只认精确类型。
#
# 【注意】经典彩蛋：isinstance(True, int) 是 True，因为 bool 是 int 的子类。
#         所以别用 isinstance(x, int) 判断「是不是纯整数」。

print(f"\n彩蛋 isinstance(True, int) = {isinstance(True, int)}")
print(f"bool 的 MRO：{[cls.__name__ for cls in bool.__mro__]}")

# 输出：
# 彩蛋 isinstance(True, int) = True
# bool 的 MRO：['bool', 'int', 'object']


# ==============================================================================
# 知识点 7：什么时候不该用继承 —— 三个警示信号
# ==============================================================================
#
# 【讲解】继承很强，但滥用比不用更糟。看到下面三种情况，先停下来想想：
#
#   信号 1：读不成「是一个」
#       ❌ class Car(Engine)   汽车「有一个」发动机，不是「是一个」发动机
#       ✅ 应该用组合：把 Engine 作为 Car 的属性（05 文件详细讲）
#
#   信号 2：只是为了复用一两个函数
#       如果只是想用父类的某个工具方法，直接写个函数就行，
#       没必要为此背上整条继承链的包袱。
#
#   信号 3：继承层次超过 3 层
#       层数越深，改一个父类方法影响的面越大，调试要翻好几层。
#       这时通常该考虑组合，或者把职责拆开。
#
# 【重点】一句话总结：继承用于「is-a」且行为需要被替换的场合；
#         组合用于「has-a」或者只是「借用能力」的场合。
#
# 组合长这样：Car 不继承 Engine，而是把 Engine 对象装进自己的属性里，
# 需要启动时调用 self.engine.start()。能力照样有，关系却是「有一个」。
# 完整的组合代码在 05_设计实战.py 里，这里先记住这个区别就行。


# ==============================================================================
# 【本章小结】
# ==============================================================================
#
# 1. class 子类(父类) 建立继承，表达「is-a」；子类自动获得父类的方法
# 2. 方法重写：子类定义同名方法盖住父类的版本，调用时优先用子类的
# 3. 重写 __init__ 后必须显式调 super().__init__(...)，否则父类属性不存在
# 4. super() 认的是 MRO 里的「下一个」，不是字面上的父类；比写死类名更安全
# 5. 多继承语法 class C(A, B)，括号顺序有语义，决定谁优先
# 6. MRO 规则：子类在前、父类按书写顺序、object 永远最后
# 7. 菱形继承下 super() 保证每个祖先只初始化一次，Root 不会被执行两遍
# 8. isinstance 沿继承链判断，issubclass 判断类与类的继承关系
# 9. 判断类型用 isinstance，不要用 type(x) is 类；bool 是 int 的子类
# 10. 读不成「是一个」、只想复用一两个函数、层次过深时，用组合别用继承


# ==============================================================================
# 【动手练习】
# ==============================================================================
#
# 练习 1：写一个 Animal 父类（name 属性 + speak 方法），
#         再写 Bird 和 Fish 两个子类，各自重写 speak。
#         Bird 额外有 fly() 方法。创建对象并逐个调用。
#
# 练习 2：写 Vehicle 父类（brand、speed），子类 Car 增加 seats。
#         子类重写 __init__ 并调用 super()，再用 isinstance 验证
#         「Car 的对象也是 Vehicle」。
#
# 练习 3：定义 A、B、C 三个类，其中 B(A)、C(A)，再定义 D(B, C)。
#         打印 D.__mro__，然后分别试 D(B, C) 和 D(C, B)，观察结果差异。
#
# 【下一步】04_魔术方法.py
# ==============================================================================
