# Code Block Test

This file tests code block rendering to ensure solid backgrounds.

## Python Code Block

```python
def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return "success"


# This is a comment
result = hello_world()
if result == "success":
    print("Function executed successfully")
else:
    print("Something went wrong")


# Multi-line code with various syntax elements
class MyClass:
    def __init__(self, name):
        self.name = name
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        return len(self.items)
```

## JavaScript Code Block

```javascript
function calculateSum(a, b) {
    // This is a comment
    const result = a + b;

    if (result > 100) {
        console.log("Large sum detected");
    }

    return result;
}

// Arrow function example
const multiply = (x, y) => {
    return x * y;
};

// Object example
const user = {
    name: "John Doe",
    age: 30,
    isActive: true
};
```

## HTML Code Block

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Hello World</h1>
    <p>This is a test paragraph.</p>
</div>
</body>
</html>
```

## CSS Code Block

```css
/* Modern CSS Grid Layout */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
}

.card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
}
```

The code blocks above should have solid dark backgrounds (#161b22) without any striped or alternating line colors.
