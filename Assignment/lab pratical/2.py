# Q2. Write a Python program to read a name and age from the user and print a formatted output.

# Program to read name and age from user and print formatted output

# Taking input from user
name = input("Enter your name: ")
age = int(input("Enter your age: "))

# Using f-string for formatted output
print(f"Hello {name}, you are {age} years old.")

# Using format() method
print("Hello {}, you are {} years old.".format(name, age))
