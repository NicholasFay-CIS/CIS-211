class Node:
    """Nodes in a treee"""

    def count_leaves(self):
        raise NotImplementedError("You better override this")

class Leaf(Node):
    def __init__(self, val):
        self.val = val

    def count_leaves(self):
        return 1

class Interior(Node):
    def __init__(self, left, right):
        """Left and right should be nodes"""
        self.left = left
        self.right = right

    def count_leaves(self):
        return self.left.count_leaves() + self.right.count_leaves()

    def count(self):
        leaflist = []
        for Node in :

            leaflist.add(Node.value())
        #add all the leaves together

        return leafcount



assert Interior(Interior(Leaf(7),Leaf(8)),Leaf(9)).count_leaves() == 3
print(Interior(Interior(Leaf(7),Leaf(8)),
               Interior(Leaf(3), Leaf(4))).count_leaves())