# Q8. Write a Python program to create a class and access its properties using an object. 

# Define a class
class Student:
    # Properties (attributes)
    def __init__(self, name, age, course):
        self.name = name
        self.age = age
        self.course = course

    # Method to display details
    def display_info(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Course: {self.course}")


# Create an object of the class
student1 = Student("Alice", 22, "Python Programming")

# Access properties using the object
print("Accessing properties directly:")
print(student1.name)
print(student1.age)
print(student1.course)

print("\nAccessing properties using method:")
student1.display_info()
