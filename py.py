import ast

source = "def func(x) -> x:\n\treturn x ** 2"
tree = ast.parse(source)

print(tree)
print(ast.dump(tree, indent=4))
print(int('0928', base=7))