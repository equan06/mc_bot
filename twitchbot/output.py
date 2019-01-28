"""
Script to print from filename.
"""
file_name = 'file_name.txt'
with open(file_name, 'r') as f:
    d = eval(f.read())
    f.close()
for v in d.values():
    print(v)
    print()