# Q4. Write a Python program to read the contents of a file and print them on the console. 

# Program to read the contents of a file and print them

# Open the file in read mode
file = open("myfile.txt", "r")

# Read the entire content
content = file.read()

# Print the content on console
print("File Contents:\n")
print(content)

# Close the file
file.close()
