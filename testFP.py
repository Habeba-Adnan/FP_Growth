import time
import csv
import pandas as pd


# Function to load file and return lists of Transactions
def Load_data(file_name):
    file_ext = file_name.split(".")[1].lower()
    transaction = []

    if file_ext == "txt":
        with open(file_name) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        for i in range(0, len(content)):
            transaction.append(content[i].split())

    elif file_ext == "csv":
        with open(file_name, 'r') as file:
            csvreader = csv.reader(file, delimiter=',')
            for row in csvreader:
                row[0] = row[0].strip().replace('"', "")
                transaction.append(row[0].split(",")[1:])
    return transaction


# To convert initial transaction into frozenset
def create_initialset(dataset):
    ret_dict = {}
    for trans in dataset:
        ret_dict[frozenset(trans)] = 1
    return ret_dict


class TreeNode:
    def __init__(self, Node_name, counter, parentNode):
        self.name = Node_name
        self.count = counter
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def increment_counter(self, counter):
        self.count += counter

    def displayer(self):
        print(self.name)
        print(self.count)
        print(self.children)
        print(self.nodeLink)


# To create Headertable and ordered itemsets for FP Tree
def create_FPTree(dataset, minSupport):
    HeaderTable = {}
    # add each repeated value to the dictionary
    for transaction in dataset:
        for item in transaction:
            HeaderTable[item] = HeaderTable.get(item, 0) + dataset[transaction]

    # filter dictionary values according to minSupport
    for k in list(HeaderTable):
        if HeaderTable[k] < minSupport:
            del (HeaderTable[k])

    frequent_itemset = set(HeaderTable.keys())

    # To Create Header Table As a Dataframe
    items = list(frequent_itemset)

    if len(frequent_itemset) == 0:
        return None, None

    for k in HeaderTable:
        HeaderTable[k] = [HeaderTable[k], None]

    ret_tree = TreeNode('Null Set', 1, None)  # Node name, Counter, Parent node
    for itemset, count in dataset.items():
        frequent_transaction = {}
        for item in itemset:
            if item in frequent_itemset:
                frequent_transaction[item] = HeaderTable[item][0]
        if len(frequent_transaction) > 0:
            # to get ordered item sets form transactions
            ordered_itemset = [v[0] for v in sorted(frequent_transaction.items(), key=lambda p: p[1], reverse=True)]

            updateTree(ordered_itemset, ret_tree, HeaderTable, count)

    return ret_tree, HeaderTable


def create_ordered_items(dataset, minSupport):
    HeaderTable = {}
    # add each repeated value to the dictionary
    for transaction in dataset:
        for item in transaction:
            HeaderTable[item] = HeaderTable.get(item, 0) + dataset[transaction]

    # filter dictionary values according to minSupport
    for k in list(HeaderTable):
        if HeaderTable[k] < minSupport:
            del (HeaderTable[k])

    frequent_itemset = set(HeaderTable.keys())

    # To Create Header Table As a Dataframe
    items = list(frequent_itemset)
    frequency = list(HeaderTable.values())

    header_table_dict = {
        "items": items,
        "frequency": frequency
    }
    df = pd.DataFrame(header_table_dict, columns=["items", "frequency"]).sort_values(by=['frequency'],
                                                                                     ascending=False,
                                                                                     ignore_index=True)
    print("\n")
    print("** Header Table **")
    print("-" * 18)
    print(df)

    if len(frequent_itemset) == 0:
        return None, None

    for k in HeaderTable:
        HeaderTable[k] = [HeaderTable[k], None]
    print("\n")
    print("-" * 38)
    print(f"* F-List: {list(df['items'])} *")
    print("-" * 38)

    ret_tree = TreeNode('Null Set', 1, None)  # Node name, Counter, Parent node
    transaction_num = 0
    all_items = []
    for itemset, count in dataset.items():
        transaction_num += 1
        frequent_transaction = {}
        for item in itemset:
            if item in frequent_itemset:
                frequent_transaction[item] = HeaderTable[item][0]
        if len(frequent_transaction) > 0:
            # to get ordered item sets form transactions
            ordered_itemset = [v[0] for v in sorted(frequent_transaction.items(), key=lambda p: p[1], reverse=True)]

            updateTree(ordered_itemset, ret_tree, HeaderTable, count)

            all_items.append(ordered_itemset)

    ordered_items_dict = {
        "T_ID": [f"T{i}" for i in range(transaction_num)],
        "ordered_items": all_items
    }
    ordered_items_data = pd.DataFrame(ordered_items_dict, columns=["T_ID", "ordered_items"])

    print("\n** Ordered Items **")
    print("-" * 20)
    print(ordered_items_data)


# To create the FP Tree using ordered itemsets
def updateTree(itemset, FPTree, HeaderTable, count):
    if itemset[0] in FPTree.children:
        FPTree.children[itemset[0]].increment_counter(count)
    else:
        FPTree.children[itemset[0]] = TreeNode(itemset[0], count, FPTree)

        if HeaderTable[itemset[0]][1] == None:
            HeaderTable[itemset[0]][1] = FPTree.children[itemset[0]]
        else:
            update_NodeLink(HeaderTable[itemset[0]][1], FPTree.children[itemset[0]])

    if len(itemset) > 1:
        updateTree(itemset[1::], FPTree.children[itemset[0]], HeaderTable, count)


# To update the link of node in FP Tree
def update_NodeLink(Test_Node, Target_Node):
    while (Test_Node.nodeLink != None):
        Test_Node = Test_Node.nodeLink

    Test_Node.nodeLink = Target_Node


# To transverse FPTree in upward direction
def FPTree_uptransveral(leaf_Node, prefixPath):
    if leaf_Node.parent != None:
        prefixPath.append(leaf_Node.name)
        FPTree_uptransveral(leaf_Node.parent, prefixPath)


# To find conditional Pattern Bases
def find_prefix_path(basePat, TreeNode):
    Conditional_patterns_base = {}
    while TreeNode != None:
        prefixPath = []
        FPTree_uptransveral(TreeNode, prefixPath)
        if len(prefixPath) > 1:
            Conditional_patterns_base[frozenset(prefixPath[1:])] = TreeNode.count
        TreeNode = TreeNode.nodeLink

    return Conditional_patterns_base


# function to mine recursively conditional patterns base and conditional FP tree
def Mine_Tree(FPTree, HeaderTable, minSupport, prefix, frequent_itemset):
    bigL = [v[0] for v in sorted(HeaderTable.items(), key=lambda p: p[1][0])]
    for basePat in bigL:
        new_frequentset = prefix.copy()
        new_frequentset.add(basePat)
        # add frequent item set to final list of frequent item sets
        frequent_itemset.append(new_frequentset)
        # get all conditional pattern bases for item or item sets
        Conditional_pattern_bases = find_prefix_path(basePat, HeaderTable[basePat][1])
        # call FP Tree construction to make conditional FP Tree
        Conditional_FPTree, Conditional_header = create_FPTree(Conditional_pattern_bases, minSupport)

        if Conditional_header != None:
            Mine_Tree(Conditional_FPTree, Conditional_header, minSupport, new_frequentset, frequent_itemset)

        # print(Conditional_pattern_bases)


print("######################## START TEST ########################")

""" First Test """
filename = rf"FP1.csv"
min_Support = 3

""" Second Test """
# filename = rf"FP2.csv"
# min_Support = 3


""" Third Test """
# filename = rf"FP3.csv"
# min_Support = 4

""" Fourth Test """
# filename = rf"test_data.csv"
# min_Support = 7

""" Fifth Test as a Text File  """
# filename = rf"d.txt"
# min_Support = 4


initSet = create_initialset(Load_data(filename))
start = time.time()

create_ordered_items(initSet, min_Support)
FPtree, HeaderTable = create_FPTree(initSet, min_Support)

frequent_items = []
# call function to mine all frequent item sets
Mine_Tree(FPtree, HeaderTable, min_Support, set([]), frequent_items)
end = time.time()

token_time = end - start
print("\n")
print("*" * 25)
print("♪ All frequent item sets:")
print("*" * 25)
print(frequent_items)
for i in frequent_items:
    print(i)
print(f"\n==> Token Time Is: {token_time}")
