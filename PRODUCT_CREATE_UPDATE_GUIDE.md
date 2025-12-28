# Product Create/Update - Frontend to Backend Mapping

## Frontend Sends vs Backend Expects

### Field Name Mapping

| Frontend Field | Backend GraphQL Field | Required | Type | Notes |
|----------------|----------------------|----------|------|-------|
| name | name | ✅ Yes | String | Product name |
| shortDescription | short_description | ✅ Yes | String | Max 255 chars |
| description | description | ❌ No | String | Full description |
| basePrice | base_price | ✅ Yes | Decimal | Must be string in GraphQL: "14.99" |
| categoryId | category_id | ✅ Yes | ID | Category ID |
| imageUrl | image | ❌ No | String | Base64 data URL format |
| tagIds | tag_ids | ❌ No | [ID] | Array of tag IDs |
| ingredientIds | ingredient_ids | ❌ No | [ID] | Array of ingredient IDs |
| sizeIds | size_ids | ❌ No | [ID] | Array of size IDs |
| toppingIds | topping_ids | ❌ No | [ID] | Array of topping IDs |
| includedItemIds | included_item_ids | ❌ No | [ID] | Array of included item IDs |
| isAvailable | is_available | ❌ No | Boolean | Default: true |
| isFeatured | is_featured | ❌ No | Boolean | Default: false |
| isCombo | is_combo | ❌ No | Boolean | Default: false |
| prepTimeMin | prep_time_min | ❌ No | Int | Minutes, default: 15 |
| prepTimeMax | prep_time_max | ❌ No | Int | Minutes, default: 20 |
| calories | calories | ❌ No | Int | Can be null |

## Important Notes

### 1. Field Name Conversion
- Frontend uses camelCase (basePrice, categoryId)
- Backend GraphQL uses snake_case (base_price, category_id)
- GraphQL automatically converts camelCase to snake_case

### 2. Price Format
- Frontend sends: number (14.99)
- Backend expects: string ("14.99")
- Frontend must convert number to string before sending

### 3. Image Field
- Frontend sends: imageUrl
- Backend expects: image
- Must be base64 data URL: "data:image/jpeg;base64,..."

### 4. Array Fields
- All array fields can be empty arrays []
- If not provided, backend treats as empty
- Backend accepts null or empty array

### 5. Optional Number Fields
- prepTimeMin, prepTimeMax, calories can be null
- Backend handles null values correctly
- Defaults applied if not provided

## Required Fields Summary

**Minimum Required to Create Product:**
- name
- shortDescription
- basePrice (as string)
- categoryId

**All Other Fields Are Optional**

## GraphQL Mutation for Frontend

### Create Product Mutation

**Mutation Name:** createProduct

**Input Structure:**
- name: String (required)
- short_description: String (required)
- description: String (optional)
- base_price: Decimal (required) - send as string
- category_id: ID (required)
- image: String (optional) - base64 data URL
- tag_ids: [ID] (optional)
- ingredient_ids: [ID] (optional)
- size_ids: [ID] (optional)
- topping_ids: [ID] (optional)
- included_item_ids: [ID] (optional)
- is_available: Boolean (optional)
- is_featured: Boolean (optional)
- is_combo: Boolean (optional)
- prep_time_min: Int (optional)
- prep_time_max: Int (optional)
- calories: Int (optional)

**Response Fields:**
- product: { id, name, basePrice, imageUrl, ... }
- success: Boolean
- message: String

### Update Product Mutation

**Mutation Name:** updateProduct

**Input Structure:**
- id: ID (required) - product ID to update
- Same input structure as createProduct
- Only send fields you want to update
- Array fields: null = keep existing, [] = clear all, [IDs] = replace

**Response Fields:**
- product: { id, name, basePrice, imageUrl, ... }
- success: Boolean
- message: String

## Data Validation

### Backend Validates:
- ✅ Category exists
- ✅ All tag IDs exist
- ✅ All ingredient IDs exist
- ✅ All size IDs exist
- ✅ All topping IDs exist
- ✅ All included item IDs exist
- ✅ base_price is positive number
- ✅ prep_time_min <= prep_time_max (if both provided)
- ✅ rating is 1-5 (for reviews)

### Frontend Should Validate:
- ✅ name is not empty
- ✅ shortDescription is not empty (max 255 chars)
- ✅ basePrice is positive number
- ✅ categoryId is valid
- ✅ Array fields are arrays
- ✅ Boolean fields are boolean
- ✅ Number fields are numbers or null

## Complete Coverage Check

### ✅ All Frontend Fields Covered:
- name → name ✅
- shortDescription → short_description ✅
- description → description ✅
- basePrice → base_price ✅
- categoryId → category_id ✅
- imageUrl → image ✅
- tagIds → tag_ids ✅
- ingredientIds → ingredient_ids ✅
- sizeIds → size_ids ✅
- toppingIds → topping_ids ✅
- includedItemIds → included_item_ids ✅
- isAvailable → is_available ✅
- isFeatured → is_featured ✅
- isCombo → is_combo ✅
- prepTimeMin → prep_time_min ✅
- prepTimeMax → prep_time_max ✅
- calories → calories ✅

**Result: All fields are covered and mapped correctly!**

## Frontend Action Items

1. Convert basePrice from number to string before sending
2. Map imageUrl field name to image in GraphQL mutation
3. Convert all camelCase to snake_case (or let GraphQL handle it)
4. Handle null values for optional number fields
5. Send empty arrays [] instead of null for array fields (optional)

## Backend Status

✅ All required fields are defined
✅ All optional fields are defined
✅ Field types match frontend data
✅ Validation is in place
✅ Error handling is implemented

**Backend is ready to receive frontend data!**

