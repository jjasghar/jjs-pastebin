#!/usr/bin/env python3
"""
Test file for JJ Pastebin Vim Plugin
This file demonstrates the plugin functionality.
"""


def hello_world():
    """A simple hello world function."""
    print("Hello from JJ Pastebin!")
    print("This code was pasted from Vim!")


def fibonacci(n):
    """Generate fibonacci sequence up to n."""
    a, b = 0, 1
    result = []
    while a < n:
        result.append(a)
        a, b = b, a + b
    return result


if __name__ == "__main__":
    hello_world()
    print("Fibonacci numbers less than 100:")
    print(fibonacci(100))
