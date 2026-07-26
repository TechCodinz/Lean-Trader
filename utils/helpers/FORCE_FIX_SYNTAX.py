
import sys

def fix_syntax(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    stack = [] # (indent_level, 'try')
    
    new_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Calculate indentation
        indent = 0
        for char in line:
            if char == ' ': indent += 1
            elif char == '\t': indent += 4
            else: break
            
        # Detect try block start
        if stripped.startswith('try:'):
            stack.append(indent)
            new_lines.append(line)
            continue
            
        # Detect except/finally (must be at same indent as last try)
        if stripped.startswith('except') or stripped.startswith('finally'):
            if stack and stack[-1] == indent:
                stack.pop() # Closed
            new_lines.append(line)
            continue
            
        # Check if indentation dropped back to stack level or less
        # AND we are in a stack
        # AND it's not a helper line (comment, blank)
        if stack and stripped and not stripped.startswith('#'):
             last_try_indent = stack[-1]
             
             if indent <= last_try_indent:
                 # We dropped indent, but didn't see except!
                 # Insert except block
                 spaces = ' ' * last_try_indent
                 print(f"Injecting except at line {i+1} (Indent {last_try_indent})")
                 new_lines.append(f"{spaces}except Exception as e_fixed_{i}: pass\n")
                 stack.pop()
                 
        new_lines.append(line)

    # If stack still open at end of file
    while stack:
        last_try_indent = stack.pop()
        spaces = ' ' * last_try_indent
        print(f"Injecting except at EOF (Indent {last_try_indent})")
        new_lines.append(f"{spaces}except Exception as e_fixed_eof: pass\n")
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
fix_syntax('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py')
