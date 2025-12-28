# 📸 Image Upload Guide

## ✅ Image Support Added!

The `createProduct` and `updateProduct` mutations now support image uploads via base64 encoding.

---

## 🧪 Test Image Upload

### Option 1: Using Base64 String (Recommended for GraphiQL)

**Step 1:** Convert your image to base64
- Use an online tool: https://www.base64-image.de/
- Or use JavaScript: `btoa(imageFile)`
- Or use Python:
```python
import base64
with open('pizza.jpg', 'rb') as f:
    base64_string = base64.b64encode(f.read()).decode('utf-8')
    print(f"data:image/jpeg;base64,{base64_string}")
```

**Step 2:** Use in GraphQL mutation:

```graphql
mutation {
  createProduct(input: {
    name: "Test Pizza"
    basePrice: "12.99"
    categoryId: "1"
    image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
  }) {
    product {
      id
      name
      imageUrl
    }
    success
    message
  }
}
```

---

### Option 2: Simple Base64 (without data URI)

You can also pass just the base64 string:

```graphql
mutation {
  createProduct(input: {
    name: "Test Pizza"
    basePrice: "12.99"
    categoryId: "1"
    image: "iVBORw0KGgoAAAANSUhEUgAA..."
  }) {
    product {
      id
      name
      imageUrl
    }
    success
  }
}
```

---

## 📝 Supported Image Formats

- **PNG** (`.png`)
- **JPEG/JPG** (`.jpg`, `.jpeg`)
- **GIF** (`.gif`)
- **WebP** (`.webp`)

---

## 🔍 Query Product with Image

After creating a product with an image, query it:

```graphql
query {
  product(id: "1") {
    id
    name
    imageUrl
    basePrice
  }
}
```

The `imageUrl` will return the full URL like:
```
http://localhost:8000/media/products/uuid-filename.png
```

---

## ✏️ Update Product Image

```graphql
mutation {
  updateProduct(id: "1", input: {
    image: "data:image/png;base64,iVBORw0KGgo..."
  }) {
    product {
      id
      name
      imageUrl
    }
    success
    message
  }
}
```

---

## 💡 Frontend Implementation

### JavaScript/React Example:

```javascript
// Convert file to base64
const convertToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
};

// Upload product with image
const createProductWithImage = async (productData, imageFile) => {
  let imageBase64 = null;
  
  if (imageFile) {
    imageBase64 = await convertToBase64(imageFile);
  }
  
  const mutation = `
    mutation CreateProduct($input: ProductInput!) {
      createProduct(input: $input) {
        product {
          id
          name
          imageUrl
        }
        success
        message
      }
    }
  `;
  
  const variables = {
    input: {
      ...productData,
      image: imageBase64
    }
  };
  
  // Send to GraphQL endpoint
  const response = await fetch('http://localhost:8000/graphql/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      query: mutation,
      variables
    })
  });
  
  return response.json();
};
```

---

## 🎯 Quick Test

1. **Get a category ID first:**
```graphql
query {
  allCategories {
    id
    name
  }
}
```

2. **Create product with image:**
```graphql
mutation {
  createProduct(input: {
    name: "Margherita Pizza"
    basePrice: "14.99"
    categoryId: "1"
    image: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
  }) {
    product {
      id
      name
      imageUrl
    }
    success
  }
}
```

3. **Check the image URL:**
```graphql
query {
  product(id: "1") {
    name
    imageUrl
  }
}
```

---

## 📁 Image Storage

- Images are saved to: `pizza_store/media/products/`
- Each image gets a unique UUID filename
- Images are accessible at: `http://localhost:8000/media/products/filename.png`

---

**Note:** For production, consider using proper file upload libraries like `graphene-file-upload` for better performance with large files.

