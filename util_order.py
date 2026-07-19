# util_order.py (excerpt – essential functions)
import re

def parse_sql(sql_query):
    # Extract WHERE clause
    match = re.search(r'WHERE (.+)', sql_query, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def extract_composite_expressions(expression):
    composite_expressions = []
    start = 0
    stack = 0
    for i, char in enumerate(expression):
        if char == '(':
            if stack == 0:
                start = i
            stack += 1
        elif char == ')':
            stack -= 1
            if stack == 0:
                composite_expressions.append(expression[start:i+1])
    return composite_expressions

def parse_input(input_text):
    attributes = {}
    attribute_blocks = input_text.strip().split('\n\n')
    for block in attribute_blocks:
        lines = block.strip().split('\n')
        name = lines[0].strip()
        key_sentences = []
        for line in lines[1:]:
            if ':' in line:
                key_sentences.append(line.split(':')[1].strip())
            else:
                key_sentences.append(line)
        attributes[name] = {'key_sentences': key_sentences}
    return attributes

def calculate_s(selectivity, key_sentences, formula='default'):
    total_tokens = sum(len(re.findall(r'\w+', sentence)) for sentence in key_sentences)
    if total_tokens == 0:
        return 0
    if formula == 'default':
        s_value = (1 - selectivity) / total_tokens
    else:
        s_value = selectivity / total_tokens
    return s_value

def calculate_composite_s(filters, filter_data, operator):
    selectivities = [filter_data[f]['selectivity'] for f in filters if f in filter_data]
    tokens = [len(re.findall(r'\w+', filter_data[f]['key_sentences'][0])) for f in filters if f in filter_data]
    if not tokens:
        return 0
    if operator == 'AND':
        composite_selectivity = 1
        for sel in selectivities:
            composite_selectivity *= sel
        composite_tokens = sum(tokens)
    elif operator == 'OR':
        composite_selectivity = 1
        for sel in selectivities:
            composite_selectivity *= (1-sel)
        composite_selectivity = 1 - composite_selectivity
        composite_tokens = sum(tokens)
    else:
        return 0
    return (1 - composite_selectivity) / composite_tokens if composite_tokens > 0 else 0

# Additional functions for Boolean evaluation (simplified versions used)
def parse_logical_expression(expression):
    # returns list of tokens
    tokens = re.split(r'(\s+AND\s+|\s+OR\s+|\(|\))', expression, flags=re.IGNORECASE)
    return [t.strip() for t in tokens if t.strip()]

def evaluate_logical_expression(expression_parts, filter_data):
    # Simplified evaluation: just return first part (for demo)
    # In real code, we would compute composite S value
    return expression_parts[0], 0.5

def handle_sql(where_clause, filter_data):
    # Simplified filter ordering: return filters sorted by selectivity descending
    # Full implementation would use composite expressions
    filters = list(filter_data.keys())
    sorted_filters = sorted(filters, key=lambda f: filter_data[f].get('selectivity', 0.5), reverse=True)
    return [(f, filter_data[f].get('s_value', 0.5)) for f in sorted_filters]