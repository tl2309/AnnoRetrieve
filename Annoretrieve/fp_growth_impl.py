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
    """将数据集转换为字典格式"""
    retDict = {}
    for trans in dataset:
        retDict[frozenset(trans)] = 1
    return retDict

def create_fptree(dataset, min_support):
    """构建FP树"""
    # 第一次扫描：统计每个项的出现次数
    header_table = {}
    for trans in dataset:
        for item in trans:
            header_table[item] = header_table.get(item, 0) + 1
    
    # 移除支持度小于min_support的项
    header_table = {k: v for k, v in header_table.items() if v >= min_support}
    frequent_items = set(header_table.keys())
    
    # 如果没有频繁项，返回None
    if len(frequent_items) == 0:
        return None, None
    
    # 扩展header_table，添加指向第一个出现项的指针
    for k in header_table:
        header_table[k] = [header_table[k], None]
    
    # 创建根节点
    root = FPNode('Null Set', 1, None)
    
    # 第二次扫描：构建FP树
    for trans in dataset:
        # 过滤并排序事务
        filtered_items = [item for item in trans if item in frequent_items]
        filtered_items.sort(key=lambda x: header_table[x][0], reverse=True)
        
        # 更新FP树
        if len(filtered_items) > 0:
            update_tree(filtered_items, root, header_table, 1)
    
    return root, header_table

def update_tree(items, in_tree, header_table, count):
    """更新FP树"""
    if items[0] in in_tree.children:
        # 如果项已经存在，增加计数
        in_tree.children[items[0]].increment(count)
    else:
        # 否则，创建新节点
        in_tree.children[items[0]] = FPNode(items[0], count, in_tree)
        
        # 更新header_table中的链接
        if header_table[items[0]][1] is None:
            header_table[items[0]][1] = in_tree.children[items[0]]
        else:
            update_header(header_table[items[0]][1], in_tree.children[items[0]])
    
    # 递归处理剩余项
    if len(items) > 1:
        update_tree(items[1:], in_tree.children[items[0]], header_table, count)

def update_header(node_to_test, target_node):
    """更新header表中的节点链接"""
    while node_to_test.next is not None:
        node_to_test = node_to_test.next
    node_to_test.next = target_node

def ascend_tree(leaf_node, prefix_path):
    """从叶节点向上遍历FP树，收集路径"""
    if leaf_node.parent is not None:
        prefix_path.append(leaf_node.item)
        ascend_tree(leaf_node.parent, prefix_path)

def find_prefix_path(base_pat, tree_node):
    """查找所有以base_pat为结尾的前缀路径"""
    cond_pats = {}
    while tree_node is not None:
        prefix_path = []
        ascend_tree(tree_node, prefix_path)
        if len(prefix_path) > 1:
            cond_pats[frozenset(prefix_path[1:])] = tree_node.count
        tree_node = tree_node.next
    return cond_pats

def mine_tree(in_tree, header_table, min_support, pre_fix, freq_item_list):
    """挖掘FP树，生成频繁项集"""
    # 按支持度升序排序所有频繁项
    sorted_items = [v[0] for v in sorted(header_table.items(), key=lambda p: p[1][0])]
    
    # 遍历每个频繁项
    for item in sorted_items:
        new_freq_set = pre_fix.copy()
        new_freq_set.add(item)
        
        # 将频繁项集添加到结果列表
        freq_item_list.append(new_freq_set)
        
        # 查找以当前项为结尾的所有前缀路径
        cond_patt_bases = find_prefix_path(item, header_table[item][1])
        
        # 构建条件FP树
        my_cond_tree, my_head = create_fptree(cond_patt_bases, min_support)
        
        # 如果条件FP树不为空，递归挖掘
        if my_head is not None:
            mine_tree(my_cond_tree, my_head, min_support, new_freq_set, freq_item_list)

def find_frequent_itemsets(transactions, min_support):
    """主函数：查找所有频繁项集"""
    # 转换数据集格式
    init_set = create_initial_set(transactions)
    
    # 构建FP树
    myFPtree, myHeaderTab = create_fptree(init_set, min_support)
    
    # 挖掘频繁项集
    freq_items = []
    if myFPtree is not None:
        mine_tree(myFPtree, myHeaderTab, min_support, set(), freq_items)
    
    return freq_items
