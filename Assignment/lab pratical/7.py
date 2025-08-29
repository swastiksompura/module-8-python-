# Q7. Understanding multiple exceptions and custom exceptions. 


try:
    num = int(input("Enter a number: "))   # may raise ValueError
    result = 10 / num                      # may raise ZeroDivisionError
    print("Result:", result)

except ValueError:
    print(" Please enter a valid number.")

except ZeroDivisionError:
    print(" You cannot divide by zero.")

except Exception as e:   # generic exception (catches other errors)
    print(" An unexpected error occurred:", e)
