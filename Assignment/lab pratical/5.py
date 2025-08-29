# Q5. Write a Python program to write multiple strings into a file. 

# Program to write multiple strings into a file

# Open the file in write mode
file = open("myfile.txt", "w")

# Multiple strings
lines = [
    "Hello, welcome to Python file handling.\n",
    "This is the second line of the file.\n",
    "Python makes file operations easy!\n"
]

# Write all strings into the file
file.writelines(lines)

# Close the file
file.close()

print("Multiple strings written to 'myfile.txt' successfully!")
