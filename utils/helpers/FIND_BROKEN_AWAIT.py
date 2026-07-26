#!/usr/bin/env python3
"""
Use AST to find 'await [list]' pattern
"""
import ast
import sys

filename = '/root/bot/EXCHANGE_SPAWN_MANAGER.py'

try:
    with open(filename, 'r') as f:
        code = f.read()

    tree = ast.parse(code)

    print(f"Analyzing {filename}...")

    class AwaitVisitor(ast.NodeVisitor):
        def visit_Await(self, node):
            # Check if awaiting a List directly: await [a, b]
            if isinstance(node.value, ast.List):
                print(f"FOUND await [list] at line {node.lineno}")
                print(f"  Line content: {code.splitlines()[node.lineno-1].strip()}")
            
            # Check if awaiting a generic Name (variable) - harder to prove it's a list, but useful context
            elif isinstance(node.value, ast.Name):
                # print(f"  Await variable '{node.value.id}' at line {node.lineno}")
                pass
            
            self.generic_visit(node)

    AwaitVisitor().visit(tree)
    print("Analysis complete.")

except Exception as e:
    print(f"Error: {e}")
