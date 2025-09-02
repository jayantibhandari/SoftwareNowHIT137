import turtle
import math

def draw_edge(length, depth):
    """Recursively draw a line segment with indentation."""
    if depth == 0:
        turtle.forward(length)
    else:
        # Divide the line into 3 segments
        draw_edge(length / 3, depth - 1)
        turtle.left(60)   # Turn to create inward triangle
        draw_edge(length / 3, depth - 1)
        turtle.right(120)
        draw_edge(length / 3, depth - 1)
        turtle.left(60)
        draw_edge(length / 3, depth - 1)

def draw_polygon(sides, length, depth):
    """Draw a polygon with recursive edges."""
    angle = 360 / sides
    for _ in range(sides):
        draw_edge(length, depth)
        turtle.right(angle)

def main():
    # User inputs
    sides = int(input("Enter number of sides: "))
    length = float(input("Enter side length (pixels): "))
    depth = int(input("Enter recursion depth: "))

    # Turtle setup
    turtle.speed(0)
    turtle.hideturtle()
    turtle.penup()
    turtle.goto(-length/2, length/2)  # Start near top-left
    turtle.pendown()

    # Draw polygon
    draw_polygon(sides, length, depth)

    turtle.done()

if __name__ == "__main__":
    main()
