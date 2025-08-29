# Q3. Write a Python program to open a file in write mode, write some text, and then close it.

# Program to open a file in write mode, write text, and close it

# Open file in write mode
file = open("myfile.txt", "w")

# Write some text to the file
file.write("Hello, this is a test file.\n")
file.write("I am learning Python file handling.\n")

# Close the file
file.close()

print("Text written to 'myfile.txt' successfully!")



