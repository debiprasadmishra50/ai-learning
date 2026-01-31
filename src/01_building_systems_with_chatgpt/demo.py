# from enum import Enum


# class Eno(str, Enum):
#     A = "1"
#     B = "2"

#     def __str__(self):
#         return self.value


# def demo(a, b=Eno.B):
#     print("=" * 30)
#     # Handle both enum and string inputs
#     print(a, b.value if isinstance(b, Eno) else b)


# print(Eno.A)
# print(Eno.B)

# demo("A")
# demo("A", "B")


x = 1


def a():
    x = 2

    def b():
        nonlocal x
        print(x)
        x = 3

        print(x)

    return b


a()()
