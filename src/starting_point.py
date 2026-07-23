import fire
import sys
def hello(name):
  return f'Hello {name}!'

class A:
  def __init__(self, name):
    self.name = name
  def salute(self, sue):
    print(f'{sue}\n')
    return self
  def greet(self, jj):
    print(f'{jj}\n')
    return self
  def to_stop(self):
    pass
  def __str__(self):
    return f'hello {self.name}'

if __name__ == '__main__':
  fire.Fire()
