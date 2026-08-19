def add(a, b):
    """Return the sum of two numbers."""
    return a + b


def main():
    # Ask the user for two numbers
    num1 = float(input("Enter the first number: "))
    num2 = float(input("Enter the second number: "))

    result = add(num1, num2)
    print(f"{num1} + {num2} = {result}")


if __name__ == "__main__":
    main()
