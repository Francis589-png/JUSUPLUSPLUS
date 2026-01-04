# Solutions — Lesson 01

1) Greeting solution (examples/hello.jusu):
```jusu
name = input("Enter your name: ")
print("Hello, " + name + "!")
```

2) Iterative factorial (examples/factorial.jusu):
```jusu
fn factorial(n) {
  if (n <= 1) { return 1 }
  result = 1
  i = 2
  while (i <= n) {
    result = result * i
    i = i + 1
  }
  return result
}

print(factorial(5))
```
