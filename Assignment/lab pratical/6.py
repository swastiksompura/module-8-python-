# Q6. Introduction to exceptions and how to handle them using try, except, and finally. 

try:
    num = int(input("Enter a number: "))   # may raise ValueError
    result = 10 / num                      # may raise ZeroDivisionError
    print("Result:", result)

except ValueError:
    print(" You must enter a valid number.")

except ZeroDivisionError:
    print(" Cannot divide by zero.")

finally:
    print(" This block always runs (cleanup, closing files, etc.).")
