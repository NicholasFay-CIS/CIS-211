#OOP Practice
"""
class List_Of_Numbers(object):
    def __init__(self, forum, age):
        self.forum = age
        self.age = age

    def print_age_add_values(self, forum, age):
        x = self.forum
        y = self. age
        z = 0
        for item in x:
            if item == int(item):
                z = z + item
                print z

            else:
                z = z + 0
                print z
        for age in self.age:
            print age
"""

"""Lets count the family members"""


class Family(object):
    """Abstract base class"""
    def members(self):
        """How many members are in a family"""
        raise NotImplementedError("You need to overide this ")


class Children(Family):
    def __init__(self, members):
        self.members_of_children = members

    def members(self):
        return self.members_of_children

class Parents(Family):
    def __init__(self, members):
        self.members_of_parents = members

    def members(self):
        return self.members_of_parents


class FullF(Family):
    def __init__(self, members):
        self.members = members

    def members(self):
        total = 0
        for person in self.members:
            total += person.members()
        return total


child = Children(10)
parent = Parents(1)
family = FullF(child)
print(child.members())



"""Mask and Shift"""
class Food(object):
    """Abstract base class"""
    def calories(self):
        """How many calories in this food, per portion"""
        raise NotImplementedError("Hey, you need to override this")

class AtomicFood(Food):
    def __init__(self, calories):
        self.calories_per_portion = calories

    def calories(self):
        return self.calories_per_portion

class ComposedFood(Food):
    def __init__(self, ingredients):
        self.ingredients = ingredients
    def calories(self):
        total = 0
        for food in self.ingredients:
            total += food.calories()
        return total

noodles = AtomicFood(100)
cheese = AtomicFood(250)
mac_n_cheese = ComposedFood([noodles, cheese])
dough = AtomicFood(45)
sauce = AtomicFood(50)
terrible_pizza = ComposedFood([dough, sauce, mac_n_cheese, cheese])

print(terrible_pizza.calories())


#linked list

class LinkedList(object):
    pass
class EmptyList(LinkedList):
    def __init__(self):
        return
    def length(self):
        return 0
    def __str__(self):
        return "."

class NonEmptyList(LinkedList):
    def __init__(self, item, li):
        self.item = item
        self.rest = li
    def length(self):
        return 1 + self.rest.length()

    def __str__(self):
        return "{}, {}".format(self.item, self.rest)


li = EmptyList()
li = NonEmptyList(1, li)
li = NonEmptyList(2, li)
li = NonEmptyList(3, li)
print(li.length())
print(li)


class Animal:
    def __init__(self, kind):
        self.kind = kind
        self.animals = []
    def add_kind(self, kind):
        self.animals.append(kind)

d = Animal("dog")
c = Animal("cat")
h = Animal("horse")
d.add_kind("German Sheapard")
print(d.animals)


class Who(object):
    def __init__(self, who):
        self.who = who
        self.dramalist = {}

    def people(self, who):
        dramalist = self.dramalist
        for person in self.who:
            dramalistupdate(person)
        return dramalist
    def drama(self, drama):
        dramalist = self.dramalist
        drama = self.drama
        return dramalist.update(drama)



marta = Who("Marta")
print(marta.drama)
marta.drama("Telling me she cant come")
print(marta.drama)