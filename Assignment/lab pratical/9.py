# Q9. Write Python programs to demonstrate different types of inheritance (single, multiple, multilevel, etc.). 

# =============================
# Demonstrating Different Types of Inheritance
# =============================

# 1. Single Inheritance
class Parent:
    def parent_info(self):
        print("Single Inheritance → Parent class")

class Child(Parent):
    def child_info(self):
        print("Single Inheritance → Child class")


# 2. Multiple Inheritance
class Father:
    def father_info(self):
        print("Multiple Inheritance → Father class")

class Mother:
    def mother_info(self):
        print("Multiple Inheritance → Mother class")

class ChildMultiple(Father, Mother):
    def child_info(self):
        print("Multiple Inheritance → Child class")


# 3. Multilevel Inheritance
class Grandparent:
    def grandparent_info(self):
        print("Multilevel Inheritance → Grandparent class")

class ParentMulti(Grandparent):
    def parent_info(self):
        print("Multilevel Inheritance → Parent class")

class ChildMultiLevel(ParentMulti):
    def child_info(self):
        print("Multilevel Inheritance → Child class")


# 4. Hierarchical Inheritance
class CommonParent:
    def parent_info(self):
        print("Hierarchical Inheritance → Common Parent class")

class Child1(CommonParent):
    def child1_info(self):
        print("Hierarchical Inheritance → Child1 class")

class Child2(CommonParent):
    def child2_info(self):
        print("Hierarchical Inheritance → Child2 class")


# 5. Hybrid Inheritance
class A:
    def showA(self):
        print("Hybrid Inheritance → Class A")

class B(A):
    def showB(self):
        print("Hybrid Inheritance → Class B")

class C(A):
    def showC(self):
        print("Hybrid Inheritance → Class C")

class D(B, C):
    def showD(self):
        print("Hybrid Inheritance → Class D")


# =============================
# Running All Examples
# =============================

print("\n--- Single Inheritance ---")
obj_single = Child()
obj_single.parent_info()
obj_single.child_info()

print("\n--- Multiple Inheritance ---")
obj_multiple = ChildMultiple()
obj_multiple.father_info()
obj_multiple.mother_info()
obj_multiple.child_info()

print("\n--- Multilevel Inheritance ---")
obj_multilevel = ChildMultiLevel()
obj_multilevel.grandparent_info()
obj_multilevel.parent_info()
obj_multilevel.child_info()

print("\n--- Hierarchical Inheritance ---")
obj_child1 = Child1()
obj_child2 = Child2()
obj_child1.parent_info()
obj_child1.child1_info()
obj_child2.parent_info()
obj_child2.child2_info()

print("\n--- Hybrid Inheritance ---")
obj_hybrid = D()
obj_hybrid.showA()
obj_hybrid.showB()
obj_hybrid.showC()
obj_hybrid.showD()
