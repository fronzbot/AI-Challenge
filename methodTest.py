import time
from math import sqrt

def TimingTest(iterations):
    start = time.time()
    for i in range(iterations):
        x = abs(71-38)
        y = abs(42-87)
        z = sqrt(x*x + y*y)
    end = time.time()

    timeTestOne = end-start

    start = time.time()
    for i in range(iterations):
        x = abs(71-38)
        y = abs(42-87)
        z = int(sqrt(x*x + y*y))
    end = time.time()

    timeTestTwo = end-start

    start = time.time()
    for i in range(iterations):
        x = 71-38
        y = 42-87
        z = sqrt(x*x + y*y)
    end = time.time()

    timeTestThree = end-start

    start = time.time()
    for i in range(iterations):
        x = 71-38
        y = 42-87
        z = int(sqrt(x*x + y*y))
    end = time.time()
    
    timeTestFour = end-start

    start = time.time()
    for i in range(iterations):
        x = max(71,38) - min(71,38)
        y = max(42,87) - min(42,87)
        z = int(sqrt(x*x + y*y))
    end = time.time()
    
    timeTestFive = end-start

    f = open('timings.txt','a')
    f.write("Iterations: "+str(iterations)+"\n")
    f.write("-------------------\n")
    f.write("Method No int(): " + str(timeTestOne) + "\n")
    f.write("Method int(), abs(): " + str(timeTestTwo) + "\n")
    f.write("Method no abs() or int()" + str(timeTestThree) + "\n")
    f.write("Method no abs(), with int() " + str(timeTestFour) + "\n")
    f.write("Method max(), min(), int(): " + str(timeTestFive) + "\n\n")
    f.close()



    
    
        
