"""Sample programs for students to learn from."""
from __future__ import annotations

SAMPLES: list[dict[str, str]] = [
    # ── Python cơ bản ──
    {
        "category": "Python cơ bản",
        "title": "Hello World",
        "description": "Chương trình đầu tiên - in ra màn hình",
        "code": '''\
# Chào mừng bạn đến với Python!
# Hãy thử thay đổi tên của bạn

name = "Neo"
print("Xin chào,", name, "!")
print("Chào mừng bạn đến với NEO CODE!")
print("Hãy bắt đầu học lập trình nào! 🚀")
''',
    },
    {
        "category": "Python cơ bản",
        "title": "Máy tính đơn giản",
        "description": "Phép tính cộng, trừ, nhân, chia",
        "code": '''\
# Máy tính đơn giản
a = 15
b = 4

print("a =", a)
print("b =", b)
print("-------------------")
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)
print("a % b =", a % b)  # Phép chia lấy dư
print("a ** b =", a ** b)  # Lũy thừa: a mũ b
''',
    },
    {
        "category": "Python cơ bản",
        "title": "Vòng lặp For",
        "description": "Học cách sử dụng vòng lặp for",
        "code": '''\
# Vòng lặp for - lặp lại một hành động nhiều lần

# Đếm từ 1 đến 10
print("Đếm số:")
for i in range(1, 11):
    print(i, end=" ")
print()

# In bảng cửu chương
print("\\nBảng cửu chương 5:")
for i in range(1, 11):
    print(f"5 x {i} = {5 * i}")
''',
    },
    {
        "category": "Python cơ bản",
        "title": "Danh sách (List)",
        "description": "Làm việc với danh sách trong Python",
        "code": '''\
# Danh sách (List) trong Python

# Tạo danh sách các loại trái cây
fruits = ["Táo", "Cam", "Xoài", "Chuối", "Dâu"]

print("Danh sách trái cây:", fruits)
print("Số lượng:", len(fruits))
print("Trái đầu tiên:", fruits[0])
print("Trái cuối cùng:", fruits[-1])

# Thêm trái cây mới
fruits.append("Nho")
print("\\nSau khi thêm Nho:", fruits)

# Duyệt danh sách
print("\\nCác loại trái cây:")
for i, fruit in enumerate(fruits, 1):
    print(f"  {i}. {fruit}")
''',
    },
    {
        "category": "Python cơ bản",
        "title": "Hàm (Function)",
        "description": "Tạo và sử dụng hàm",
        "code": '''\
# Hàm (Function) - tái sử dụng code

def greet(name):
    """Hàm chào hỏi."""
    return f"Xin chào {name}! Chúc bạn học tốt!"

def calculate_area(width, height):
    """Tính diện tích hình chữ nhật."""
    return width * height

def is_even(number):
    """Kiểm tra số chẵn."""
    return number % 2 == 0

# Sử dụng các hàm
print(greet("Neo"))
print(greet("Bạn"))

print(f"\\nDiện tích 5x3 = {calculate_area(5, 3)}")
print(f"Diện tích 10x7 = {calculate_area(10, 7)}")

# Kiểm tra số chẵn lẻ
for n in range(1, 11):
    status = "chẵn" if is_even(n) else "lẻ"
    print(f"  {n} là số {status}")
''',
    },

    # ── Turtle Graphics ──
    {
        "category": "Turtle Graphics",
        "title": "Vẽ hình vuông",
        "description": "Vẽ hình vuông đầu tiên với Turtle",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("cyan")

# Vẽ hình vuông
for i in range(4):
    t.forward(100)
    t.right(90)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Vẽ tam giác",
        "description": "Vẽ tam giác đều với Turtle",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)
t.pencolor("yellow")

# Vẽ tam giác đều (mỗi góc 120 độ)
for i in range(3):
    t.forward(120)
    t.left(120)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Ngôi sao 5 cánh",
        "description": "Vẽ ngôi sao nhiều màu sắc",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(3)

colors = ["red", "orange", "yellow", "green", "blue"]

# Vẽ ngôi sao 5 cánh
for i in range(5):
    t.pencolor(colors[i])
    t.forward(150)
    t.right(144)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Hình xoắn ốc",
        "description": "Tạo hình xoắn ốc đầy màu sắc",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]

# Vẽ hình xoắn ốc
for i in range(80):
    t.pencolor(colors[i % len(colors)])
    t.forward(i * 2)
    t.right(91)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Hình tròn và bông hoa",
        "description": "Vẽ bông hoa từ nhiều hình tròn",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

colors = ["red", "orange", "yellow", "pink", "purple", "cyan"]

# Vẽ bông hoa từ các hình tròn
for i in range(6):
    t.pencolor(colors[i])
    t.circle(60)
    t.right(60)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Nhiều hình vuông xoay",
        "description": "Tạo hoa văn đẹp từ các hình vuông xoay",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(1)

colors = ["red", "orange", "yellow", "green", "cyan", "blue"]

# Vẽ nhiều hình vuông xoay
for j in range(36):
    t.pencolor(colors[j % len(colors)])
    for i in range(4):
        t.forward(80)
        t.right(90)
    t.right(10)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Cây fractal đơn giản",
        "description": "Vẽ cây phân nhánh (fractal tree)",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)
t.pencolor("green")

# Đặt vị trí bắt đầu ở dưới
t.penup()
t.goto(0, -120)
t.pendown()
t.left(90)

def draw_branch(length):
    """Vẽ nhánh cây đệ quy."""
    if length < 10:
        return
    t.forward(length)
    t.left(25)
    draw_branch(length * 0.7)
    t.right(50)
    draw_branch(length * 0.7)
    t.left(25)
    t.backward(length)

draw_branch(80)

turtle.done()
''',
    },
    {
        "category": "Turtle Graphics",
        "title": "Ngôi nhà đơn giản",
        "description": "Vẽ ngôi nhà với mái và cửa",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)

# --- Vẽ thân nhà ---
t.pencolor("cyan")
t.penup()
t.goto(-60, -60)
t.pendown()

for i in range(2):
    t.forward(120)
    t.left(90)
    t.forward(100)
    t.left(90)

# --- Vẽ mái nhà ---
t.pencolor("red")
t.penup()
t.goto(-70, 40)
t.pendown()
t.goto(0, 90)
t.goto(70, 40)
t.goto(-70, 40)

# --- Vẽ cửa ---
t.pencolor("yellow")
t.penup()
t.goto(-15, -60)
t.pendown()
for i in range(2):
    t.forward(30)
    t.left(90)
    t.forward(50)
    t.left(90)

t.hideturtle()
turtle.done()
''',
    },

    # ── Nâng cao ──
    {
        "category": "Nâng cao",
        "title": "Hình đa giác tùy chọn",
        "description": "Hàm vẽ đa giác với số cạnh bất kỳ",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)

def draw_polygon(sides, size, color):
    """Vẽ đa giác đều với số cạnh, kích thước, màu tùy chọn."""
    t.pencolor(color)
    angle = 360 / sides
    for i in range(sides):
        t.forward(size)
        t.right(angle)

# Vẽ các hình đa giác khác nhau
shapes = [
    (3, 80, "red"),      # Tam giác
    (4, 70, "orange"),   # Hình vuông
    (5, 60, "yellow"),   # Ngũ giác
    (6, 50, "green"),    # Lục giác
    (8, 40, "cyan"),     # Bát giác
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
    },
    {
        "category": "Nâng cao",
        "title": "Vẽ hình với fill color",
        "description": "Sử dụng begin_fill/end_fill để tô màu",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(3)
t.pensize(2)

def filled_square(size, pen_color, fill_col):
    """Vẽ hình vuông có tô màu."""
    t.pencolor(pen_color)
    t.fillcolor(fill_col)
    t.begin_fill()
    for i in range(4):
        t.forward(size)
        t.right(90)
    t.end_fill()

# Vẽ 3 hình vuông tô màu
t.penup()
t.goto(-120, 30)
t.pendown()

filled_square(60, "white", "red")

t.penup()
t.forward(80)
t.pendown()

filled_square(60, "white", "blue")

t.penup()
t.forward(80)
t.pendown()

filled_square(60, "white", "green")

t.hideturtle()
turtle.done()
''',
    },
    {
        "category": "Nâng cao",
        "title": "Mandala pattern",
        "description": "Tạo hoa văn Mandala đẹp mắt",
        "code": '''\
import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(1)

colors = ["red", "orange", "yellow", "green",
          "cyan", "blue", "purple", "pink"]

# Vẽ Mandala
for i in range(72):
    t.pencolor(colors[i % len(colors)])
    t.circle(80, 90)
    t.right(90)
    t.circle(80, 90)
    t.right(185)

t.hideturtle()
turtle.done()
''',
    },
]
