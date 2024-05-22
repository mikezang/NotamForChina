import time
import datetime
import turtle

def drawGap():
    turtle.penup()
    turtle.fd(5)

def drawLine(draw):
    drawGap()
    turtle.pendown() if draw else turtle.penup()
    turtle.fd(40)
    drawGap()
    turtle.right(90)

def drawDigit(d):
    drawLine(True) if d in [2,3,4,5,6,8,9,'A','P'] else drawLine(False)
    drawLine(True) if d in [0,1,3,4,5,6,7,8,9,'A'] else drawLine(False)
    drawLine(True) if d in [0,2,3,5,6,8,9] else drawLine(False)
    drawLine(True) if d in [0,2,6,8,'A','P'] else drawLine(False)
    turtle.left(90)
    drawLine(True) if d in [0,4,5,6,8,9,'A','P'] else drawLine(False)
    drawLine(True) if d in [0,2,3,5,6,7,8,9,'A','P'] else drawLine(False)
    drawLine(True) if d in [0,1,2,3,4,7,8,9,'A','P'] else drawLine(False)
    turtle.left(180)
    turtle.penup()
    turtle.fd(20)

def drawLineVerticle(draw, down=True):
    turtle.right(90) if down else turtle.right(-90)
    drawGap()
    turtle.pendown() if draw else turtle.penup()
    turtle.fd(40)
    drawGap()
    turtle.right(-90) if down else turtle.right(90)

def drawLineHorizon(draw, right=True):
    None if right else turtle.right(180)
    drawGap()
    turtle.pendown() if draw else turtle.penup()
    turtle.fd(40) 
    drawGap()
    None if right else turtle.right(-180)

def drawDigitNew(d):
    x, y = turtle.pos()
    match d:
        case 1:
            drawLineHorizon(False)
            drawLineVerticle(True)
            drawLineVerticle(True)
        case 2:
            drawLineHorizon(True)
            drawLineVerticle(True)
            drawLineHorizon(True, False)
            drawLineVerticle(True)
            drawLineHorizon(True)
        case 3:
            drawLineHorizon(True)
            drawLineVerticle(True)
            drawLineHorizon(True, False)
            drawLineHorizon(False)
            drawLineVerticle(True)
            drawLineHorizon(True, False)
        case 4:
            drawLineVerticle(True)
            drawLineHorizon(True)
            drawLineVerticle(False, False)
            drawLineVerticle(True)
            drawLineVerticle(True)
        case 5:
            drawLineVerticle(True)
            drawLineHorizon(True)
            drawLineVerticle(True)
            drawLineHorizon(True, False)
            drawLineVerticle(False, False)
            drawLineVerticle(False, False)
            drawLineHorizon(True)
        case 6:
            drawLineHorizon(False)
            drawLineHorizon(True, False)
            drawLineVerticle(True)
            drawLineVerticle(True)
            drawLineHorizon(True)
            drawLineVerticle(True, False)
            drawLineHorizon(True, False)
        case 7:
            drawLineHorizon(True)
            drawLineVerticle(True)
            drawLineVerticle(True)
        case 8:
            drawLineHorizon(False)
            drawLineVerticle(False)
            drawLineVerticle(True, False)
            drawLineHorizon(True, False)
            drawLineVerticle(True)
            drawLineHorizon(True)
            drawLineVerticle(True)
            drawLineHorizon(True, False)
            drawLineVerticle(True, False)
        case 9:
            drawLineHorizon(False)
            drawLineVerticle(False)
            drawLineVerticle(True, False)
            drawLineHorizon(True, False)
            drawLineVerticle(True)
            drawLineHorizon(True)
            drawLineVerticle(True)
            drawLineHorizon(True, False)
        case 0:
            drawLineVerticle(True)
            drawLineVerticle(True)
            drawLineHorizon(True)
            drawLineVerticle(True, False)
            drawLineVerticle(True, False)
            drawLineHorizon(True, False)
    turtle.goto(x, y)
    turtle.penup()
    turtle.fd(70)

def drawDate():
    date = time.strftime('%Y-%m=%d+', time.gmtime())
    # date = '5555-56=78+'
    turtle.pencolor('red')
    for i in date:
        if i == '-':
            turtle.write('年', font=('Arial', 18, 'normal'))
            turtle.pencolor('green')
            turtle.fd(40)
        elif i == '=':
            turtle.write('月', font=('Arial', 18, 'normal'))
            turtle.pencolor('blue')
            turtle.fd(40)
        elif i == '+':
            turtle.write('日', font=('Arial', 18, 'normal'))
        else:
            drawDigitNew(eval(i))

def AP():
    hour = datetime.datetime.now().hour
    drawDigit('P') if hour >= 12 else drawDigit('A')

def drawTime():
    time = datetime.datetime.now().strftime('%H-%M=%S')
    turtle.pencolor('orange')
    for i in time:
        if i =='-':
            turtle.seth(-90)
            turtle.fd(80)
            turtle.write(':',font=('Arisl',70,'normal'))
            turtle.seth(90)
            turtle.fd(80)
            turtle.seth(0)
            turtle.fd(30)
        elif i =='=':
            turtle.seth(-90)
            turtle.fd(80)
            turtle.write(':', font=('Arisl', 70, 'normal'))
            turtle.seth(90)
            turtle.fd(80)
            turtle.seth(0)
            turtle.fd(30)
        else:
            drawDigitNew(eval(i))
    turtle.hideturtle()
    turtle.done()

if __name__ == '__main__':
    turtle.speed(0)
    turtle.pensize(5)
    turtle.penup()
    turtle.setup(760, 400, 100, 100)
    turtle.goto(-330, 150)
    drawDate()
    turtle.goto(-250, -20)
    drawTime()
