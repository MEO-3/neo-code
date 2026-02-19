"""Educational projects with 3-level system.

Based on "Coding for Beginners Using Python" by Rosie Dickins.
Each project has 3 difficulty levels:
  Level 1 "Kham pha" (6-8): Nearly complete code, change 1-2 values
  Level 2 "Lap trinh vien" (9-11): Key parts blanked out with ___, hints provided
  Level 3 "Chuyen gia" (12+): Only task description + code skeleton
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProjectLevel:
    """A single difficulty level for a project."""
    code: str
    hints: list[str] = field(default_factory=list)


@dataclass
class Project:
    """An educational project with multiple difficulty levels."""
    id: str
    title: str
    title_en: str
    category: str
    category_en: str
    description: str
    description_en: str
    solution: str
    concepts: list[str]
    levels: dict[int, ProjectLevel] = field(default_factory=dict)
    field_id: str = ""


# ── Category names ──
CAT_FIRST_STEPS = "Buoc dau tien"
CAT_FIRST_STEPS_EN = "First Steps"
CAT_TURTLE_BASIC = "Turtle co ban"
CAT_TURTLE_BASIC_EN = "Basic Turtle"
CAT_LOOPS_PATTERNS = "Vong lap & Hoa van"
CAT_LOOPS_PATTERNS_EN = "Loops & Patterns"
CAT_FUNCTIONS = "Ham"
CAT_FUNCTIONS_EN = "Functions"
CAT_GAMES = "Tro choi & Thach thuc"
CAT_GAMES_EN = "Games & Challenges"


PROJECTS: list[Project] = [
    # ══════════════════════════════════════════
    # Category 1: Buoc dau tien
    # ══════════════════════════════════════════
    Project(
        id="hello_world",
        title="Hello World",
        title_en="Hello World",
        category=CAT_FIRST_STEPS,
        category_en=CAT_FIRST_STEPS_EN,
        description="Viet chuong trinh dau tien: in loi chao ra man hinh voi ten cua ban.",
        description_en="Write your first program: print a greeting with your name.",
        concepts=["print", "string", "variable"],
        solution='''\
# Chao mung ban den voi Python!
name = "Neo"
print("Xin chao,", name, "!")
print("Chao mung ban den voi NEO CODE!")
print("Hay bat dau hoc lap trinh nao!")
''',
        levels={
            1: ProjectLevel(
                code='''\
# Chao mung ban den voi Python!
# Hay thay ten "Neo" bang ten cua ban
name = "Neo"
print("Xin chao,", name, "!")
print("Chao mung ban den voi NEO CODE!")
print("Hay bat dau hoc lap trinh nao!")
''',
                hints=["Thay doi ten trong dau ngoac kep"],
            ),
            2: ProjectLevel(
                code='''\
# Hay dien ten cua ban vao cho trong
name = ___
print("Xin chao,", ___, "!")
print("Chao mung ban den voi NEO CODE!")
''',
                hints=[
                    'name = "Ten cua ban" (nho dau ngoac kep)',
                    "Dung bien name de in ra",
                ],
            ),
            3: ProjectLevel(
                code='''\
# Nhiem vu: In loi chao voi ten cua ban
# Goi y: dung print() va bien name
''',
                hints=[
                    "Tao bien name chua ten ban",
                    "Dung print() de in ra man hinh",
                ],
            ),
        },
    ),

    Project(
        id="simple_calculator",
        title="May tinh don gian",
        title_en="Simple Calculator",
        category=CAT_FIRST_STEPS,
        category_en=CAT_FIRST_STEPS_EN,
        description="Lam may tinh thuc hien cac phep cong, tru, nhan, chia.",
        description_en="Build a calculator that does addition, subtraction, multiplication, and division.",
        concepts=["variable", "arithmetic", "print"],
        solution='''\
# May tinh don gian
a = 15
b = 4

print("a =", a)
print("b =", b)
print("-------------------")
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)
''',
        levels={
            1: ProjectLevel(
                code='''\
# May tinh don gian
# Hay thay doi so a va b de thu
a = 15
b = 4

print("a =", a)
print("b =", b)
print("-------------------")
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)
''',
                hints=["Thay doi gia tri a va b roi bam Run"],
            ),
            2: ProjectLevel(
                code='''\
# Dien so vao cho trong
a = ___
b = ___

print("a + b =", ___)
print("a - b =", ___)
print("a * b =", ___)
print("a / b =", ___)
''',
                hints=[
                    "Dien so bat ky vao a va b",
                    "Phep cong: a + b, Phep tru: a - b",
                ],
            ),
            3: ProjectLevel(
                code='''\
# Nhiem vu: Tao may tinh cong tru nhan chia
# Goi y: tao 2 bien so, in ket qua cac phep tinh
''',
                hints=[
                    "Tao bien a va b chua so",
                    "Dung +, -, *, / de tinh toan",
                    "Dung print() de in ket qua",
                ],
            ),
        },
    ),

    # ══════════════════════════════════════════
    # Category 2: Turtle co ban
    # ══════════════════════════════════════════
    Project(
        id="square",
        title="Hinh vuong",
        title_en="Square",
        category=CAT_TURTLE_BASIC,
        category_en=CAT_TURTLE_BASIC_EN,
        description="Ve hinh vuong bang Turtle. Dung vong lap for de lap lai 4 lan: tien va quay.",
        description_en="Draw a square with Turtle. Use a for loop to repeat 4 times: move forward and turn.",
        concepts=["turtle", "for loop", "forward", "right"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("cyan")

for i in range(4):
    t.forward(100)
    t.right(90)

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("cyan")

# Hay thay doi kich thuoc hinh vuong (100 -> ?)
for i in range(4):
    t.forward(100)
    t.right(90)

turtle.done()
''',
                hints=["Thay 100 bang so khac de thay doi kich thuoc"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("cyan")

# Ve hinh vuong: lap 4 lan
for i in range(___):
    t.forward(___)
    t.right(___)

turtle.done()
''',
                hints=[
                    "Hinh vuong co 4 canh",
                    "Moi canh dai bang nhau, vd: 100",
                    "Moi goc quay la 90 do",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)

# Nhiem vu: Ve hinh vuong bang vong lap for
# Goi y: forward() de tien, right() de quay

turtle.done()
''',
                hints=[
                    "Dung for i in range(4):",
                    "Trong vong lap: t.forward(100) roi t.right(90)",
                ],
            ),
        },
    ),

    Project(
        id="triangle",
        title="Tam giac",
        title_en="Triangle",
        category=CAT_TURTLE_BASIC,
        category_en=CAT_TURTLE_BASIC_EN,
        description="Ve tam giac deu bang Turtle. Tam giac co 3 canh va moi goc ngoai la 120 do.",
        description_en="Draw an equilateral triangle with Turtle. A triangle has 3 sides and each exterior angle is 120 degrees.",
        concepts=["turtle", "for loop", "forward", "left", "angles"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("yellow")

for i in range(3):
    t.forward(120)
    t.left(120)

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("yellow")

# Hay doi mau sac (yellow -> ?)
for i in range(3):
    t.forward(120)
    t.left(120)

turtle.done()
''',
                hints=["Thu mau khac: red, blue, green, orange, pink"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("yellow")

# Ve tam giac: lap 3 lan
for i in range(___):
    t.forward(___)
    t.left(___)

turtle.done()
''',
                hints=[
                    "Tam giac co 3 canh",
                    "Chieu dai canh: 120",
                    "Goc ngoai tam giac deu = 120 do",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)

# Nhiem vu: Ve tam giac deu
# Goi y: goc ngoai = 360 / so_canh

turtle.done()
''',
                hints=[
                    "Tam giac co 3 canh",
                    "Goc ngoai = 360 / 3 = 120 do",
                ],
            ),
        },
    ),

    Project(
        id="star",
        title="Ngoi sao 5 canh",
        title_en="5-pointed Star",
        category=CAT_TURTLE_BASIC,
        category_en=CAT_TURTLE_BASIC_EN,
        description="Ve ngoi sao 5 canh nhieu mau. Moi canh quay 144 do.",
        description_en="Draw a colorful 5-pointed star. Each turn is 144 degrees.",
        concepts=["turtle", "for loop", "list", "colors"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(3)

colors = ["red", "orange", "yellow", "green", "blue"]

for i in range(5):
    t.pencolor(colors[i])
    t.forward(150)
    t.right(144)

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(3)

# Hay thay doi danh sach mau sac
colors = ["red", "orange", "yellow", "green", "blue"]

for i in range(5):
    t.pencolor(colors[i])
    t.forward(150)
    t.right(144)

turtle.done()
''',
                hints=["Thay doi mau trong danh sach colors"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(3)

colors = ["red", "orange", "yellow", "green", "blue"]

for i in range(___):
    t.pencolor(colors[i])
    t.forward(___)
    t.right(___)

turtle.done()
''',
                hints=[
                    "Ngoi sao co 5 canh",
                    "Moi canh dai khoang 150",
                    "Goc quay la 144 do (360*2/5)",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(3)

# Nhiem vu: Ve ngoi sao 5 canh nhieu mau
# Goi y: lap 5 lan, moi lan tien va quay 144 do

turtle.done()
''',
                hints=[
                    "Tao danh sach 5 mau",
                    "Goc quay = 144 do",
                ],
            ),
        },
    ),

    # ══════════════════════════════════════════
    # Category 3: Vong lap & Hoa van
    # ══════════════════════════════════════════
    Project(
        id="spiral",
        title="Xoan oc",
        title_en="Spiral",
        category=CAT_LOOPS_PATTERNS,
        category_en=CAT_LOOPS_PATTERNS_EN,
        description="Tao hinh xoan oc day mau sac. Moi lan lap, tang chieu dai buoc di.",
        description_en="Create a colorful spiral. Each iteration increases the step length.",
        concepts=["turtle", "for loop", "variable increment", "modulo"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]

for i in range(80):
    t.pencolor(colors[i % len(colors)])
    t.forward(i * 2)
    t.right(91)

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]

# Hay thay doi so 91 de xem hinh thay doi
for i in range(80):
    t.pencolor(colors[i % len(colors)])
    t.forward(i * 2)
    t.right(91)

turtle.done()
''',
                hints=["Thu thay 91 bang 89, 90, 92 de xem su khac biet"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]

for i in range(___):
    t.pencolor(colors[i % len(colors)])
    t.forward(i * ___)
    t.right(___)

turtle.done()
''',
                hints=[
                    "Lap khoang 80 lan",
                    "i * 2 de tang chieu dai moi buoc",
                    "Quay khoang 91 do de tao xoan oc",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)

# Nhiem vu: Ve hinh xoan oc day mau sac
# Goi y: dung for i in range(), tang forward moi lan

turtle.done()
''',
                hints=[
                    "Dung t.forward(i * 2) de tang dan",
                    "Quay khoang 91 do tao hieu ung xoan",
                ],
            ),
        },
    ),

    Project(
        id="flower",
        title="Bong hoa",
        title_en="Flower",
        category=CAT_LOOPS_PATTERNS,
        category_en=CAT_LOOPS_PATTERNS_EN,
        description="Ve bong hoa tu nhieu hinh tron. Moi canh hoa la mot vong tron, xoay deu.",
        description_en="Draw a flower from circles. Each petal is a circle, rotated evenly.",
        concepts=["turtle", "circle", "for loop", "rotation"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "pink", "purple", "cyan"]

for i in range(6):
    t.pencolor(colors[i])
    t.circle(60)
    t.right(60)

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "pink", "purple", "cyan"]

# Hay thay doi so canh hoa (6) va kich thuoc (60)
for i in range(6):
    t.pencolor(colors[i])
    t.circle(60)
    t.right(60)

turtle.done()
''',
                hints=["Thu thay 6 bang 8 va 60 bang 45 (360/8)"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "pink", "purple", "cyan"]

for i in range(___):
    t.pencolor(colors[i])
    t.circle(___)
    t.right(___)

turtle.done()
''',
                hints=[
                    "6 canh hoa",
                    "Ban kinh moi canh: 60",
                    "Goc quay: 360/6 = 60 do",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)

# Nhiem vu: Ve bong hoa tu nhieu hinh tron
# Goi y: moi canh hoa la circle(), xoay deu

turtle.done()
''',
                hints=[
                    "Dung t.circle(60) de ve 1 canh hoa",
                    "Quay 360/so_canh do sau moi canh",
                ],
            ),
        },
    ),

    Project(
        id="rotating_squares",
        title="Hinh vuong xoay",
        title_en="Rotating Squares",
        category=CAT_LOOPS_PATTERNS,
        category_en=CAT_LOOPS_PATTERNS_EN,
        description="Tao hoa van dep tu nhieu hinh vuong xoay chong len nhau.",
        description_en="Create a beautiful pattern from overlapping rotated squares.",
        concepts=["turtle", "nested loop", "rotation pattern"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(1)

colors = ["red", "orange", "yellow", "green", "cyan", "blue"]

for j in range(36):
    t.pencolor(colors[j % len(colors)])
    for i in range(4):
        t.forward(80)
        t.right(90)
    t.right(10)

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(1)

colors = ["red", "orange", "yellow", "green", "cyan", "blue"]

# Hay thay doi so 36 va kich thuoc 80
for j in range(36):
    t.pencolor(colors[j % len(colors)])
    for i in range(4):
        t.forward(80)
        t.right(90)
    t.right(10)

turtle.done()
''',
                hints=["Thu thay 36 bang 18 (xoay 20 do), hoac thay 80 bang 100"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(1)

colors = ["red", "orange", "yellow", "green", "cyan", "blue"]

# Ve 36 hinh vuong, moi hinh xoay 10 do
for j in range(___):
    t.pencolor(colors[j % len(colors)])
    for i in range(4):
        t.forward(___)
        t.right(___)
    t.right(___)

turtle.done()
''',
                hints=[
                    "36 hinh vuong, moi hinh xoay 10 do (36 * 10 = 360)",
                    "Hinh vuong: 4 canh, moi canh 80, quay 90 do",
                    "Sau moi hinh vuong quay them 10 do",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)

# Nhiem vu: Ve hoa van tu nhieu hinh vuong xoay
# Goi y: vong lap ngoai xoay, vong lap trong ve hinh vuong

turtle.done()
''',
                hints=[
                    "Vong ngoai: for j in range(36), xoay 10 do",
                    "Vong trong: ve hinh vuong 4 canh",
                ],
            ),
        },
    ),

    # ══════════════════════════════════════════
    # Category 4: Ham
    # ══════════════════════════════════════════
    Project(
        id="polygon_function",
        title="Ham ve da giac",
        title_en="Polygon Function",
        category=CAT_FUNCTIONS,
        category_en=CAT_FUNCTIONS_EN,
        description="Tao ham ve da giac deu voi so canh bat ky. Dung ham de ve tam giac, ngu giac, luc giac.",
        description_en="Create a function to draw any regular polygon. Use it to draw triangles, pentagons, hexagons.",
        concepts=["function", "parameter", "turtle", "for loop", "angles"],
        solution='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

def draw_polygon(sides, size, color):
    """Ve da giac deu."""
    t.pencolor(color)
    angle = 360 / sides
    for i in range(sides):
        t.forward(size)
        t.right(angle)

shapes = [
    (3, 80, "red"),
    (4, 70, "orange"),
    (5, 60, "yellow"),
    (6, 50, "green"),
    (8, 40, "cyan"),
]

t.penup()
t.goto(-200, 0)
t.pendown()

for sides, size, color in shapes:
    draw_polygon(sides, size, color)
    t.penup()
    t.forward(size + 30)
    t.pendown()

turtle.done()
''',
        levels={
            1: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

def draw_polygon(sides, size, color):
    """Ve da giac deu."""
    t.pencolor(color)
    angle = 360 / sides
    for i in range(sides):
        t.forward(size)
        t.right(angle)

# Hay them hinh moi vao danh sach (so_canh, kich_thuoc, mau)
shapes = [
    (3, 80, "red"),
    (4, 70, "orange"),
    (5, 60, "yellow"),
    (6, 50, "green"),
    (8, 40, "cyan"),
]

t.penup()
t.goto(-200, 0)
t.pendown()

for sides, size, color in shapes:
    draw_polygon(sides, size, color)
    t.penup()
    t.forward(size + 30)
    t.pendown()

turtle.done()
''',
                hints=["Them (10, 30, 'purple') vao danh sach shapes"],
            ),
            2: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

def draw_polygon(sides, size, color):
    """Ve da giac deu."""
    t.pencolor(color)
    angle = 360 / ___
    for i in range(___):
        t.forward(___)
        t.right(angle)

# Ve tam giac va hinh vuong
draw_polygon(3, 80, "red")
draw_polygon(___, ___, "blue")

turtle.done()
''',
                hints=[
                    "angle = 360 / sides (so canh)",
                    "range(sides) de lap dung so canh",
                    "forward(size) de ve moi canh",
                    "Hinh vuong: 4 canh, kich thuoc 70",
                ],
            ),
            3: ProjectLevel(
                code='''\
import turtle

t = turtle.Turtle()
t.speed(0)

# Nhiem vu: Tao ham draw_polygon(sides, size, color)
# rui dung ham do ve nhieu hinh da giac khac nhau
# Goi y: goc quay = 360 / so_canh

turtle.done()
''',
                hints=[
                    "def draw_polygon(sides, size, color):",
                    "angle = 360 / sides",
                    "Goi ham: draw_polygon(5, 60, 'yellow')",
                ],
            ),
        },
    ),

    # ══════════════════════════════════════════
    # Category 5: Tro choi & Thach thuc
    # ══════════════════════════════════════════
    Project(
        id="guess_number",
        title="Doan so",
        title_en="Guess the Number",
        category=CAT_GAMES,
        category_en=CAT_GAMES_EN,
        description="Tao tro choi doan so. May tinh chon so ngau nhien, ban phai doan dung.",
        description_en="Create a number guessing game. The computer picks a random number, you guess it.",
        concepts=["random", "while loop", "if/else", "input", "comparison"],
        solution='''\
import random

secret = random.randint(1, 20)
attempts = 0

print("Toi dang nghi mot so tu 1 den 20.")
print("Ban hay thu doan xem!")

while True:
    guess = int(input("Nhap so cua ban: "))
    attempts += 1

    if guess < secret:
        print("Lon hon!")
    elif guess > secret:
        print("Nho hon!")
    else:
        print(f"Dung roi! Ban doan dung sau {attempts} lan!")
        break
''',
        levels={
            1: ProjectLevel(
                code='''\
import random

# Hay thay doi pham vi so (1-20 -> ?)
secret = random.randint(1, 20)
attempts = 0

print("Toi dang nghi mot so tu 1 den 20.")
print("Ban hay thu doan xem!")

while True:
    guess = int(input("Nhap so cua ban: "))
    attempts += 1

    if guess < secret:
        print("Lon hon!")
    elif guess > secret:
        print("Nho hon!")
    else:
        print(f"Dung roi! Ban doan dung sau {attempts} lan!")
        break
''',
                hints=["Thay doi 20 thanh 100 de kho hon"],
            ),
            2: ProjectLevel(
                code='''\
import random

secret = random.randint(1, ___)
attempts = 0

print("Toi dang nghi mot so tu 1 den 20.")

while True:
    guess = int(input("Nhap so: "))
    attempts += 1

    if guess < secret:
        print(___)
    elif guess > secret:
        print(___)
    else:
        print(f"Dung roi! Sau {attempts} lan!")
        ___
''',
                hints=[
                    "Pham vi: 1 den 20",
                    "Nho hon thi in 'Lon hon!', lon hon thi in 'Nho hon!'",
                    "Dung roi thi break de thoat vong lap",
                ],
            ),
            3: ProjectLevel(
                code='''\
import random

# Nhiem vu: Tro choi doan so
# 1. May tinh chon so ngau nhien (random.randint)
# 2. Nguoi choi nhap so (input)
# 3. So sanh va goi y "Lon hon" / "Nho hon"
# 4. Lap lai cho den khi doan dung
''',
                hints=[
                    "Dung random.randint(1, 20)",
                    "Dung while True: de lap",
                    "So sanh bang if/elif/else",
                    "Dung break khi doan dung",
                ],
            ),
        },
    ),
]


def _get_all_projects() -> list[Project]:
    """Get all projects including robot challenges."""
    from neo_code.education.robot_challenges import ROBOT_PROJECTS
    return PROJECTS + ROBOT_PROJECTS


def get_projects_by_category() -> dict[str, list[Project]]:
    """Return projects grouped by category."""
    categories: dict[str, list[Project]] = {}
    for project in _get_all_projects():
        categories.setdefault(project.category, []).append(project)
    return categories


def get_project_by_id(project_id: str) -> Project | None:
    """Find a project by its ID."""
    for project in _get_all_projects():
        if project.id == project_id:
            return project
    return None
