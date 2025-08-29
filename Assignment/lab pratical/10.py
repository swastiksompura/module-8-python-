# Q10. Write Python programs to demonstrate method overloading and method overriding.
 
# ==============================
# Method Overloading (simulated in Python)
# ==============================
class Calculator:
    # Same method name, flexible number of arguments
    def add(self, a=0, b=0, c=0):
        return a + b + c


# ==============================
# Method Overriding
# ==============================
class Animal:
    def sound(self):
        print("Animals make different sounds.")

class Dog(Animal):  # inherits from Animal
    def sound(self):  # overriding the parent method
        print("Dog barks: Woof! Woof!")


# ==============================
# Running both examples
# ==============================

print("--- Method Overloading Example ---")
calc = Calculator()
print("add(2) =", calc.add(2))           # One argument
print("add(2, 3) =", calc.add(2, 3))     # Two arguments
print("add(2, 3, 4) =", calc.add(2, 3, 4))  # Three arguments

print("\n--- Method Overriding Example ---")
animal = Animal()
dog = Dog()
animal.sound()   # Parent class method
dog.sound()      # Overridden method

