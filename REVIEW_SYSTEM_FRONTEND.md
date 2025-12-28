# Review System - Frontend Integration Guide

## Overview

Complete GraphQL API documentation for the product review system. This includes queries for fetching reviews and mutations for submitting, approving, and managing reviews.

---

## 📋 **GraphQL Types**

### **ProductReviewType**

```graphql
type ProductReviewType {
  id: ID!
  customerName: String!
  customerEmail: String!
  rating: Int!                    # 1-5 stars
  ratingDisplay: String!          # Visual stars (e.g., "★★★★☆")
  comment: String!
  isApproved: Boolean!
  createdAt: DateTime!
  product: ProductType             # Product this review is for
}
```

---

## 🔍 **Queries**

### 1. Get Product Reviews (Public)

Get approved reviews for a specific product.

```graphql
query GetProductReviews($productId: ID!, $approvedOnly: Boolean) {
  productReviews(productId: $productId, approvedOnly: $approvedOnly) {
    id
    customerName
    rating
    ratingDisplay
    comment
    createdAt
    product {
      id
      name
    }
  }
}
```

**Variables:**
```json
{
  "productId": "1",
  "approvedOnly": true
}
```

**Response:**
```json
{
  "data": {
    "productReviews": [
      {
        "id": "1",
        "customerName": "John Doe",
        "rating": 5,
        "ratingDisplay": "★★★★★",
        "comment": "Amazing pizza!",
        "createdAt": "2024-01-15T10:30:00Z",
        "product": {
          "id": "1",
          "name": "Margherita Pizza"
        }
      }
    ]
  }
}
```

---

### 2. Get Pending Reviews (Admin/Staff Only)

Get all reviews awaiting approval (moderation queue).

```graphql
query GetPendingReviews {
  pendingReviews {
    id
    customerName
    customerEmail
    rating
    ratingDisplay
    comment
    product {
      id
      name
      imageUrl
    }
    createdAt
  }
}
```

**Response:**
```json
{
  "data": {
    "pendingReviews": [
      {
        "id": "5",
        "customerName": "Jane Smith",
        "customerEmail": "jane@example.com",
        "rating": 4,
        "ratingDisplay": "★★★★☆",
        "comment": "Good but could be better",
        "product": {
          "id": "2",
          "name": "Pepperoni Pizza",
          "imageUrl": "/media/products/..."
        },
        "createdAt": "2024-01-16T14:20:00Z"
      }
    ]
  }
}
```

---

### 3. Get All Reviews (Admin/Staff Only)

Get all reviews with optional filters.

```graphql
query GetAllReviews(
  $approvedOnly: Boolean
  $productId: ID
  $rating: Int
) {
  allReviews(
    approvedOnly: $approvedOnly
    productId: $productId
    rating: $rating
  ) {
    id
    customerName
    customerEmail
    rating
    ratingDisplay
    comment
    isApproved
    product {
      id
      name
    }
    createdAt
  }
}
```

**Variables Examples:**

**Get all unapproved reviews:**
```json
{
  "approvedOnly": false
}
```

**Get all 5-star reviews:**
```json
{
  "approvedOnly": true,
  "rating": 5
}
```

**Get all reviews for a product:**
```json
{
  "productId": "1"
}
```

---

### 4. Get Single Review (Admin/Staff Only)

Get a specific review by ID.

```graphql
query GetReview($id: ID!) {
  review(id: $id) {
    id
    customerName
    customerEmail
    rating
    ratingDisplay
    comment
    isApproved
    product {
      id
      name
      basePrice
    }
    createdAt
  }
}
```

**Variables:**
```json
{
  "id": "1"
}
```

---

## ✏️ **Mutations**

### 1. Submit Review (Public)

Submit a new product review (requires admin approval).

```graphql
mutation SubmitReview($input: ProductReviewInput!) {
  submitReview(input: $input) {
    review {
      id
      customerName
      rating
      comment
    }
    success
    message
  }
}
```

**Variables:**
```json
{
  "input": {
    "productId": "1",
    "customerName": "John Doe",
    "customerEmail": "john@example.com",
    "rating": 5,
    "comment": "Best pizza I've ever had!"
  }
}
```

**Response:**
```json
{
  "data": {
    "submitReview": {
      "review": {
        "id": "10",
        "customerName": "John Doe",
        "rating": 5,
        "comment": "Best pizza I've ever had!"
      },
      "success": true,
      "message": "Review submitted successfully. It will be visible after approval."
    }
  }
}
```

**Input Type:**
```graphql
input ProductReviewInput {
  productId: ID!              # Required
  customerName: String!        # Required
  customerEmail: String!       # Required
  rating: Int!                 # Required (1-5)
  comment: String              # Optional
}
```

---

### 2. Approve/Reject Review (Admin/Staff Only)

Approve or reject a review.

```graphql
mutation ApproveReview($id: ID!, $approve: Boolean!) {
  approveReview(id: $id, approve: $approve) {
    review {
      id
      isApproved
      rating
      comment
    }
    success
    message
  }
}
```

**Variables (Approve):**
```json
{
  "id": "5",
  "approve": true
}
```

**Variables (Reject):**
```json
{
  "id": "5",
  "approve": false
}
```

**Response:**
```json
{
  "data": {
    "approveReview": {
      "review": {
        "id": "5",
        "isApproved": true,
        "rating": 4,
        "comment": "Good but could be better"
      },
      "success": true,
      "message": "Review approved"
    }
  }
}
```

---

### 3. Delete Review (Admin/Staff Only)

Delete a review permanently.

```graphql
mutation DeleteReview($id: ID!) {
  deleteReview(id: $id) {
    success
    message
  }
}
```

**Variables:**
```json
{
  "id": "5"
}
```

**Response:**
```json
{
  "data": {
    "deleteReview": {
      "success": true,
      "message": "Review deleted successfully"
    }
  }
}
```

---

## 💡 **Frontend Implementation Examples**

### React/TypeScript Example

```typescript
// Submit Review
const submitReview = async (
  productId: string,
  customerName: string,
  customerEmail: string,
  rating: number,
  comment: string
) => {
  const response = await graphqlClient.mutate({
    mutation: SUBMIT_REVIEW_MUTATION,
    variables: {
      input: {
        productId,
        customerName,
        customerEmail,
        rating,
        comment
      }
    }
  });
  
  return response.data.submitReview;
};

// Get Product Reviews
const getProductReviews = async (productId: string) => {
  const response = await graphqlClient.query({
    query: GET_PRODUCT_REVIEWS_QUERY,
    variables: {
      productId,
      approvedOnly: true
    }
  });
  
  return response.data.productReviews;
};

// Get Pending Reviews (Admin)
const getPendingReviews = async () => {
  const response = await graphqlClient.query({
    query: GET_PENDING_REVIEWS_QUERY
  });
  
  return response.data.pendingReviews;
};

// Approve Review (Admin)
const approveReview = async (reviewId: string, approve: boolean) => {
  const response = await graphqlClient.mutate({
    mutation: APPROVE_REVIEW_MUTATION,
    variables: {
      id: reviewId,
      approve
    }
  });
  
  return response.data.approveReview;
};
```

---

## 🎨 **UI Display Examples**

### Review Card Component

```typescript
const ReviewCard = ({ review }) => {
  return (
    <div className="review-card">
      <div className="review-header">
        <h4>{review.customerName}</h4>
        <div className="rating">
          {review.ratingDisplay} ({review.rating}/5)
        </div>
      </div>
      <p className="review-comment">{review.comment}</p>
      <span className="review-date">
        {new Date(review.createdAt).toLocaleDateString()}
      </span>
    </div>
  );
};
```

### Review Form Component

```typescript
const ReviewForm = ({ productId, onSubmit }) => {
  const [formData, setFormData] = useState({
    customerName: '',
    customerEmail: '',
    rating: 5,
    comment: ''
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await submitReview(
      productId,
      formData.customerName,
      formData.customerEmail,
      formData.rating,
      formData.comment
    );
    
    if (result.success) {
      alert(result.message);
      onSubmit();
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Your Name"
        value={formData.customerName}
        onChange={(e) => setFormData({...formData, customerName: e.target.value})}
        required
      />
      <input
        type="email"
        placeholder="Your Email"
        value={formData.customerEmail}
        onChange={(e) => setFormData({...formData, customerEmail: e.target.value})}
        required
      />
      <select
        value={formData.rating}
        onChange={(e) => setFormData({...formData, rating: parseInt(e.target.value)})}
      >
        <option value={5}>5 Stars</option>
        <option value={4}>4 Stars</option>
        <option value={3}>3 Stars</option>
        <option value={2}>2 Stars</option>
        <option value={1}>1 Star</option>
      </select>
      <textarea
        placeholder="Your Review"
        value={formData.comment}
        onChange={(e) => setFormData({...formData, comment: e.target.value})}
      />
      <button type="submit">Submit Review</button>
    </form>
  );
};
```

### Moderation Queue (Admin)

```typescript
const ModerationQueue = () => {
  const { data, loading, refetch } = useQuery(GET_PENDING_REVIEWS_QUERY);
  const [approveReview] = useMutation(APPROVE_REVIEW_MUTATION);
  
  const handleApprove = async (reviewId: string, approve: boolean) => {
    await approveReview({
      variables: { id: reviewId, approve }
    });
    refetch();
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="moderation-queue">
      <h2>Pending Reviews ({data.pendingReviews.length})</h2>
      {data.pendingReviews.map(review => (
        <div key={review.id} className="pending-review">
          <div className="review-info">
            <h4>{review.customerName}</h4>
            <p>{review.ratingDisplay} - {review.product.name}</p>
            <p>{review.comment}</p>
          </div>
          <div className="review-actions">
            <button onClick={() => handleApprove(review.id, true)}>
              Approve
            </button>
            <button onClick={() => handleApprove(review.id, false)}>
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
```

---

## 🔐 **Permissions**

| Operation | Public | Staff | Admin |
|-----------|--------|-------|-------|
| Submit Review | ✅ | ✅ | ✅ |
| View Approved Reviews | ✅ | ✅ | ✅ |
| View Pending Reviews | ❌ | ✅* | ✅ |
| View All Reviews | ❌ | ✅* | ✅ |
| Approve/Reject Review | ❌ | ✅* | ✅ |
| Delete Review | ❌ | ✅* | ✅ |

*Requires `can_manage_reviews` permission

---

## ⚠️ **Error Handling**

### Common Errors

**1. "Product not found"**
- Product ID doesn't exist
- Product has been deleted

**2. "Rating must be between 1 and 5"**
- Rating value is invalid

**3. "You don't have permission to..."**
- User not authenticated
- User doesn't have review management permission

**4. "Review not found"**
- Review ID doesn't exist
- Review has been deleted

### Error Response Format

```json
{
  "errors": [
    {
      "message": "You don't have permission to view pending reviews",
      "locations": [{"line": 2, "column": 3}],
      "path": ["pendingReviews"]
    }
  ],
  "data": null
}
```

---

## 📊 **Rating Calculation**

- Product ratings are automatically calculated from approved reviews
- Average rating is updated when:
  - A review is approved
  - A review is rejected
  - A review is deleted
- Only approved reviews count toward the average

---

## ✅ **Best Practices**

1. **Display Reviews:**
   - Show `ratingDisplay` for visual stars
   - Format dates using `createdAt`
   - Only show approved reviews to public users

2. **Submit Reviews:**
   - Validate rating (1-5) on frontend
   - Show success message after submission
   - Inform users that reviews require approval

3. **Moderation:**
   - Show pending review count badge
   - Display product info with each review
   - Provide quick approve/reject actions

4. **Error Handling:**
   - Check for authentication errors
   - Handle permission errors gracefully
   - Show user-friendly error messages

---

## 📝 **Complete GraphQL Operations**

### All Queries

```graphql
# Get product reviews
query GetProductReviews($productId: ID!, $approvedOnly: Boolean) {
  productReviews(productId: $productId, approvedOnly: $approvedOnly) {
    id
    customerName
    rating
    ratingDisplay
    comment
    createdAt
  }
}

# Get pending reviews (admin/staff)
query GetPendingReviews {
  pendingReviews {
    id
    customerName
    customerEmail
    rating
    ratingDisplay
    comment
    product {
      id
      name
    }
    createdAt
  }
}

# Get all reviews (admin/staff)
query GetAllReviews($approvedOnly: Boolean, $productId: ID, $rating: Int) {
  allReviews(approvedOnly: $approvedOnly, productId: $productId, rating: $rating) {
    id
    customerName
    rating
    ratingDisplay
    comment
    isApproved
    createdAt
  }
}

# Get single review (admin/staff)
query GetReview($id: ID!) {
  review(id: $id) {
    id
    customerName
    rating
    comment
    isApproved
    product {
      id
      name
    }
    createdAt
  }
}
```

### All Mutations

```graphql
# Submit review
mutation SubmitReview($input: ProductReviewInput!) {
  submitReview(input: $input) {
    review {
      id
      customerName
      rating
      comment
    }
    success
    message
  }
}

# Approve/reject review
mutation ApproveReview($id: ID!, $approve: Boolean!) {
  approveReview(id: $id, approve: $approve) {
    review {
      id
      isApproved
    }
    success
    message
  }
}

# Delete review
mutation DeleteReview($id: ID!) {
  deleteReview(id: $id) {
    success
    message
  }
}
```

---

## 🚀 **Ready to Use!**

All GraphQL operations are ready for frontend integration. The review system supports:
- ✅ Public review submission
- ✅ Admin/staff moderation
- ✅ Filtering and searching
- ✅ Automatic rating calculation
- ✅ Permission-based access control

Happy coding! 🎉

