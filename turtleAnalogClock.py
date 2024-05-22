import turtle
import time

# Switch to Logo mode - Up = 0 degrees, then go clockwise
turtle.mode("logo")

# Clock Hand Lengths
SECOND_HAND = 110
MINUTE_HAND = 80
HOUR_HAND = 60

# Create a Turtle screen
screen = turtle.Screen()
screen.bgcolor("white")
screen.tracer(0)

# Create a Turtle object
face = turtle.Turtle(visible=False)
face.speed(0)  # Set the drawing speed
hands = turtle.Turtle(visible=False)

# Function to draw a clock face with hands
def draw_clock_face():
    # Draw the clock outline
    face.clear()
    face.penup()
    face.goto(150, 0) # Adjust position due to switch to Logo mode
    face.setheading(0)
    face.pendown()
    face.circle(150)

    # Initialize the starting angle for number 12 at 90 degrees
    # Draw the clock numbers and balls
    for i in range(12):
        hour = 12 if i == 0 else i
        face.penup()
        face.goto(0,0)
        face.setheading(i*30) # angle in degrees
        face.forward(125)
        face.pendown()
        face.dot(15, "red" if hour in [3, 6, 9, 12] else "blue")
        face.setheading(180)
        face.penup()
        face.forward(25)
        face.color("black")  # Reset color to black for numbers
        face.write(str(hour), align="center", font=("Arial", 10, "normal"),)

# Function to draw clock hands
def draw_clock_hands():
    current_time = time.localtime()
    hands.clear() # Clear previous hands

    # Calculate angles for the hands
    second_angle = current_time.tm_sec * 6
    minute_angle = current_time.tm_min * 6 - current_time.tm_sec * 0.1
    hour_angle = (current_time.tm_hour % 12) * 30 + current_time.tm_min * 0.5
    #print(f"{hour_angle=}  {minute_angle=}   {second_angle=}")

    # Draw the second hand (black)
    hands.penup()
    hands.goto(0, 0)
    hands.pendown()
    hands.color("black")
    hands.setheading(second_angle)
    hands.pensize(1)
    hands.forward(SECOND_HAND)

    # Draw the minute hand (red)
    hands.penup()
    hands.goto(0, 0)
    hands.pendown()
    hands.color("red")
    hands.setheading(minute_angle)
    hands.pensize(3)
    hands.forward(MINUTE_HAND)

    # Draw the hour hand (green)
    hands.penup()
    hands.goto(0, 0)
    hands.pendown()
    hands.color("green")
    hands.setheading(hour_angle)
    hands.pensize(5)
    hands.forward(HOUR_HAND)

# Function to update the clock continuously
def update_clock():
    draw_clock_face() # Call the function to draw the clock face
    while True:
        draw_clock_hands()  # Draw the clock hands based on the current time
        screen.update()  # Update the screen
        time.sleep(1)  # Wait for 1 second before updating the clock again

if __name__ == "__main__":
    update_clock()  # Call the function to draw the clock hands
    screen.exitonclick() # Close the window when clicked
