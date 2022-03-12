from typing import Any, List

class Node:
    children: List[Any] = []
    data: int
    
    def __init__(self, data: int):
        self.data = data

class BinaryTreeArrayCreator:

    num_internal_nodes = 0
    root_node: Node

    def __init__(self, array: List[int]):
        value = array.index(-1)
        if value is None:
            raise Exception('Root of tree not found!')
        self.root_node = Node(value)
        self.create_tree(array)

    def get_first_item(self, array: List[Node]):
        try:
            return array[0]
        except:
            return None

    def create_tree(self, array: List[int]):
        create_tree_filo: List[Node] = []
        create_tree_filo.append(self.root_node)
        while True:
            first_node = self.get_first_item(create_tree_filo)
            if first_node is None:
                break
            if len(first_node.children) > 0:
                create_tree_filo.remove(first_node)
            else:
                children = self.get_children(array, first_node.data)
                if len(children) > 0:
                    first_node.children = children
                    self.num_internal_nodes = self.num_internal_nodes + 1
                    create_tree_filo[:0] = children
                else:
                    create_tree_filo.remove(first_node)

    def get_children(self, array: List[int], value: int) -> List[Node]:
        return [Node(i) for i, x in enumerate(array) if x == value]

def find_internal_nodes_num(tree):
    binary_tree_creator = BinaryTreeArrayCreator(tree)
    return binary_tree_creator.num_internal_nodes

my_tree = [4, 4, 1, 5, -1, 4, 5]
print(find_internal_nodes_num(my_tree))