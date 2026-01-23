# FP-Growth Algorithm Implementation for Python 3

class FPNode:
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.next = None
    
    def increment(self, count):
        self.count += count
    
    def display(self, ind=1):
        print('  ' * ind, self.item, ':', self.count)
        for child in self.children.values():
            child.display(ind + 1)

def create_initial_set(dataset):
    """Convert dataset to dictionary format"""
    retDict = {}
    for trans in dataset:
        retDict[frozenset(trans)] = 1
    return retDict

def create_fptree(dataset, min_support):
    """Build FP-tree"""
    # First scan: count occurrence of each item
    header_table = {}
    for trans in dataset:
        for item in trans:
            header_table[item] = header_table.get(item, 0) + 1
    
    # Remove items with support less than min_support
    header_table = {k: v for k, v in header_table.items() if v >= min_support}
    frequent_items = set(header_table.keys())
    
    # Return None if no frequent items
    if len(frequent_items) == 0:
        return None, None
    
    # Extend header_table, add pointer to first occurrence of item
    for k in header_table:
        header_table[k] = [header_table[k], None]
    
    # Create root node
    root = FPNode('Null Set', 1, None)
    
    # Second scan: build FP-tree
    for trans in dataset:
        # Filter and sort transaction
        filtered_items = [item for item in trans if item in frequent_items]
        filtered_items.sort(key=lambda x: header_table[x][0], reverse=True)
        
        # Update FP-tree
        if len(filtered_items) > 0:
            update_tree(filtered_items, root, header_table, 1)
    
    return root, header_table

def update_tree(items, in_tree, header_table, count):
    """Update FP-tree"""
    if items[0] in in_tree.children:
        # Increment count if item already exists
        in_tree.children[items[0]].increment(count)
    else:
        # Create new node otherwise
        in_tree.children[items[0]] = FPNode(items[0], count, in_tree)
        
        # Update links in header_table
        if header_table[items[0]][1] is None:
            header_table[items[0]][1] = in_tree.children[items[0]]
        else:
            update_header(header_table[items[0]][1], in_tree.children[items[0]])
    
    # Recursively process remaining items
    if len(items) > 1:
        update_tree(items[1:], in_tree.children[items[0]], header_table, count)

def update_header(node_to_test, target_node):
    """Update node links in header table"""
    while node_to_test.next is not None:
        node_to_test = node_to_test.next
    node_to_test.next = target_node

def ascend_tree(leaf_node, prefix_path):
    """Traverse FP-tree upward from leaf node to collect path"""
    if leaf_node.parent is not None:
        prefix_path.append(leaf_node.item)
        ascend_tree(leaf_node.parent, prefix_path)

def find_prefix_path(base_pat, tree_node):
    """Find all prefix paths ending with base_pat"""
    cond_pats = {}
    while tree_node is not None:
        prefix_path = []
        ascend_tree(tree_node, prefix_path)
        if len(prefix_path) > 1:
            cond_pats[frozenset(prefix_path[1:])] = tree_node.count
        tree_node = tree_node.next
    return cond_pats

def mine_tree(in_tree, header_table, min_support, pre_fix, freq_item_list):
    """Mine FP-tree to generate frequent itemsets"""
    # Sort all frequent items by support in ascending order
    sorted_items = [v[0] for v in sorted(header_table.items(), key=lambda p: p[1][0])]
    
    # Iterate through each frequent item
    for item in sorted_items:
        new_freq_set = pre_fix.copy()
        new_freq_set.add(item)
        
        # Add frequent itemset to result list
        freq_item_list.append(new_freq_set)
        
        # Find all prefix paths ending with current item
        cond_patt_bases = find_prefix_path(item, header_table[item][1])
        
        # Build conditional FP-tree
        my_cond_tree, my_head = create_fptree(cond_patt_bases, min_support)
        
        # Recursively mine if conditional FP-tree is not empty
        if my_head is not None:
            mine_tree(my_cond_tree, my_head, min_support, new_freq_set, freq_item_list)

def find_frequent_itemsets(transactions, min_support):
    """Main function: find all frequent itemsets"""
    # Convert dataset format
    init_set = create_initial_set(transactions)
    
    # Build FP-tree
    myFPtree, myHeaderTab = create_fptree(init_set, min_support)
    
    # Mine frequent itemsets
    freq_items = []
    if myFPtree is not None:
        mine_tree(myFPtree, myHeaderTab, min_support, set(), freq_items)
    
    return freq_items
