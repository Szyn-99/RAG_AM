from pathlib import Path
import pathlib

path = Path('/', '.', "test", "another_test","__main__.py")
# Path('a/b/c').mkdir(parents=True, exist_ok=True)
# print(path.parent)
# print(Path.cwd())
# print(Path.home())
# for p in path.parents:
#     print(p)
print(Path('a/b').is_absolute())