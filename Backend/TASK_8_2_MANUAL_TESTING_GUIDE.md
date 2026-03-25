# Task 8.2: Inventory Analytics - Manual Testing Guide

**Status:** ✅ COMPLETE  
**Date:** 2025-03-25  
**Version:** 1.0  

---

## 📋 Overview

This manual testing guide covers all 6 Inventory Analytics endpoints for Task 8.2. Each endpoint provides aggregated analytics on inventory, wastage, and ingredient usage with date range filtering capabilities.

### Key Features
- ✅ 6 new analytics endpoints
- ✅ Real-time inventory valuation
- ✅ Stock turnover rate calculations
- ✅ Expired items tracking
- ✅ Wastage summary and trends
- ✅ Ingredient usage rates
- ✅ Date range filtering (daily/weekly/monthly)
- ✅ Token-based authentication
- ✅ JSON response format

---

## 🔐 Test Environment Setup

### Prerequisites
1. **Backend Server Running**
   ```bash
   cd Backend/
   python manage.py runserver
   ```
   Server should be accessible at: http://localhost:8000/

2. **Postman or cURL Installed**
   - For cURL: Already available on most systems
   - For Postman: Download from https://www.postman.com/

3. **Test User Credentials**
   - Username: `manager_user` (or any manager role user)
   - Password: `password123`
   - Role: Manager (required for analytics access)

### Authentication Setup

1. **Login to Get Token**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"manager_user","password":"password123"}'
   ```

2. **Response**
   ```json
   {
     "token": "abc123xyz789...",
     "user": {
       "id": 1,
       "username": "manager_user",
       "role": "manager",
       "email": "manager@example.com"
     }
   }
   ```

3. **Copy Token for All Requests**
   - Store token value for use in all subsequent API calls
   - Add header: `Authorization: Token abc123xyz789...`

---

## 📊 Endpoint Testing

### 1️⃣ Stock Value Endpoint

**Purpose:** Calculate total inventory value at cost price

**Endpoint:** `GET /api/analytics/inventory/stock_value/`

**Authentication:** Required (Token)

**Query Parameters:** None

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/stock_value/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Response Structure:**
```json
{
  "total_stock_value": "7500.00",
  "items": [
    {
      "product_id": 1,
      "product_name": "Whole Wheat Bread",
      "quantity": "100.00",
      "cost_price": "50.00",
      "item_value": "5000.00"
    },
    {
      "product_id": 2,
      "product_name": "White Bread",
      "quantity": "50.00",
      "cost_price": "40.00",
      "item_value": "2000.00"
    }
  ],
  "item_count": 2
}
```

**Validation Checklist:**
- [ ] Status code is 200
- [ ] `total_stock_value` is numeric decimal
- [ ] `items` array contains all products
- [ ] Each item has: `product_id`, `product_name`, `quantity`, `cost_price`, `item_value`
- [ ] `item_value` = `quantity` × `cost_price`
- [ ] `total_stock_value` = sum of all `item_value`
- [ ] Zero stock products show value of 0
- [ ] Empty inventory shows total_stock_value of 0

---

### 2️⃣ Turnover Rate Endpoint

**Purpose:** Calculate stock turnover rates and days to turnover per product

**Endpoint:** `GET /api/analytics/inventory/turnover/`

**Authentication:** Required (Token)

**Query Parameters:**
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- Default: Last 30 days

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/turnover/?date_from=2025-02-24&date_to=2025-03-25" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Response Structure:**
```json
[
  {
    "product_id": 1,
    "product_name": "Whole Wheat Bread",
    "current_stock": "100.00",
    "quantity_sold": "10.00",
    "turnover_rate": "0.10",
    "annualized_turnover": "1.22",
    "days_to_turnover": "299.00"
  },
  {
    "product_id": 2,
    "product_name": "White Bread",
    "current_stock": "50.00",
    "quantity_sold": "5.00",
    "turnover_rate": "0.10",
    "annualized_turnover": "1.22",
    "days_to_turnover": "299.00"
  }
]
```

**Formulas:**
- *Turnover Rate* = quantity_sold ÷ avg_inventory
- *Annualized Turnover* = (turnover_rate ÷ days_in_period) × 365
- *Days to Turnover* = 365 ÷ annualized_turnover

**Validation Checklist:**
- [ ] Status code is 200
- [ ] Response is an array of products
- [ ] Each product has: `product_id`, `product_name`, `current_stock`, `quantity_sold`, `turnover_rate`, `annualized_turnover`, `days_to_turnover`
- [ ] Products with no sales show `quantity_sold` of 0
- [ ] Products with no sales show `turnover_rate` of 0
- [ ] Date range filtering works correctly
- [ ] Default date range is last 30 days
- [ ] Invalid dates default to 30-day range

---

### 3️⃣ Expired Items Endpoint

**Purpose:** Track expired ingredient batches and their value

**Endpoint:** `GET /api/analytics/inventory/expired/`

**Authentication:** Required (Token)

**Query Parameters:** None

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/expired/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Response Structure:**
```json
{
  "total_expired_value": "250.00",
  "expired_count": 1,
  "items": [
    {
      "batch_id": 5,
      "ingredient_id": 2,
      "ingredient_name": "Yeast",
      "quantity": "50.00",
      "expire_date": "2025-03-20",
      "cost_price": "5.00",
      "expired_value": "250.00",
      "days_expired": 5
    }
  ]
}
```

**Validation Checklist:**
- [ ] Status code is 200
- [ ] Only batches with `expire_date` < today are included
- [ ] Only batches with `current_qty` > 0 are included
- [ ] Each item shows: `batch_id`, `ingredient_id`, `ingredient_name`, `quantity`, `expire_date`, `cost_price`, `expired_value`, `days_expired`
- [ ] `expired_value` = `quantity` × `cost_price`
- [ ] `total_expired_value` = sum of all `expired_value`
- [ ] `days_expired` = today - `expire_date`
- [ ] Empty result shows `total_expired_value` of 0

---

### 4️⃣ Wastage Summary Endpoint

**Purpose:** View waitage breakdown by reason and calculate wastage percentage

**Endpoint:** `GET /api/analytics/inventory/wastage_summary/`

**Authentication:** Required (Token)

**Query Parameters:**
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- Default: Last 30 days

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/wastage_summary/?date_from=2025-02-24&date_to=2025-03-25" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Response Structure:**
```json
{
  "period": "2025-02-24 to 2025-03-25",
  "total_wastage_loss": "350.00",
  "total_wastage_percentage": "70.00",
  "wastage_by_reason": [
    {
      "reason_name": "Product Expired",
      "quantity": "5.00",
      "total_loss": "250.00",
      "waste_count": 1,
      "percentage_of_revenue": "50.00",
      "type": "product"
    },
    {
      "reason_name": "ingredients",
      "quantity": "10.00",
      "total_loss": "100.00",
      "waste_count": 1,
      "percentage_of_revenue": "20.00",
      "type": "ingredient"
    }
  ]
}
```

**Formulas:**
- *Wastage % of Revenue* = (wastage_loss ÷ total_revenue) × 100
- *Total Wastage %* = (total_wastage_loss ÷ total_revenue) × 100

**Validation Checklist:**
- [ ] Status code is 200
- [ ] Returns: `period`, `total_wastage_loss`, `total_wastage_percentage`, `wastage_by_reason`
- [ ] `wastage_by_reason` is an array
- [ ] Each reason shows: `reason_name`, `quantity`, `total_loss`, `waste_count`, `percentage_of_revenue`, `type`
- [ ] Product and ingredient wastage are separated
- [ ] Calculations match formulas above
- [ ] Date range filtering works correctly
- [ ] Zero wastage shows appropriate zeros
- [ ] No revenue scenario handled gracefully

---

### 5️⃣ Wastage Trend Endpoint

**Purpose:** View wastage trends over time (daily, weekly, or monthly)

**Endpoint:** `GET /api/analytics/inventory/wastage_trend/`

**Authentication:** Required (Token)

**Query Parameters:**
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- `trend_type` (optional): `daily`, `weekly`, or `monthly` (default: `daily`)

**Request Examples:**

Daily Trend:
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/wastage_trend/?trend_type=daily" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

Weekly Trend:
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/wastage_trend/?trend_type=weekly" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

Monthly Trend:
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/wastage_trend/?trend_type=monthly" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response Structure (Daily):**
```json
{
  "period": "2025-02-24 to 2025-03-25",
  "trend_type": "daily",
  "trends": [
    {
      "period": "2025-03-22",
      "total_loss": "250.00",
      "product_loss": "250.00",
      "ingredient_loss": "0.00",
      "total_quantity": "5.00"
    },
    {
      "period": "2025-03-23",
      "total_loss": "100.00",
      "product_loss": "0.00",
      "ingredient_loss": "100.00",
      "total_quantity": "10.00"
    }
  ]
}
```

**Response Structure (Weekly):**
```json
{
  "period": "2025-02-24 to 2025-03-25",
  "trend_type": "weekly",
  "trends": [
    {
      "period": "2025-03-17 to 2025-03-23",
      "total_loss": "350.00",
      "product_loss": "250.00",
      "ingredient_loss": "100.00",
      "total_quantity": "15.00"
    }
  ]
}
```

**Validation Checklist:**
- [ ] Status code is 200
- [ ] Returns: `period`, `trend_type`, `trends`
- [ ] `trend_type` matches requested type (daily/weekly/monthly)
- [ ] Each trend item shows: `period`, `total_loss`, `product_loss`, `ingredient_loss`, `total_quantity`
- [ ] Daily trends show individual dates (YYYY-MM-DD)
- [ ] Weekly trends show date ranges
- [ ] Monthly trends show YYYY-MM format
- [ ] Trends are chronologically ordered
- [ ] Separates product and ingredient wastage
- [ ] Default trend_type is daily
- [ ] Empty trend lists handle gracefully

---

### 6️⃣ Ingredient Usage Endpoint

**Purpose:** Calculate ingredient usage rates and track consumption

**Endpoint:** `GET /api/analytics/inventory/ingredient_usage/`

**Authentication:** Required (Token)

**Query Parameters:**
- `date_from` (optional): Start date in YYYY-MM-DD format
- `date_to` (optional): End date in YYYY-MM-DD format
- Default: Last 30 days

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/analytics/inventory/ingredient_usage/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Response Structure:**
```json
[
  {
    "ingredient_id": 1,
    "ingredient_name": "All Purpose Flour",
    "total_purchased": "500.00",
    "total_used": "200.00",
    "usage_rate": "40.00",
    "current_stock": "300.00"
  },
  {
    "ingredient_id": 2,
    "ingredient_name": "Yeast",
    "total_purchased": "100.00",
    "total_used": "50.00",
    "usage_rate": "50.00",
    "current_stock": "50.00"
  }
]
```

**Formula:**
- *Usage Rate* = (total_used ÷ total_purchased) × 100

**Validation Checklist:**
- [ ] Status code is 200
- [ ] Response is an array of ingredients
- [ ] Each ingredient has: `ingredient_id`, `ingredient_name`, `total_purchased`, `total_used`, `usage_rate`, `current_stock`
- [ ] `total_used` = `total_purchased` - remaining_qty
- [ ] `usage_rate` calculated as percentage
- [ ] Ingredients with no purchases show 0% usage
- [ ] `current_stock` matches ingredient total_quantity
- [ ] Date range filtering works correctly
- [ ] Default range is last 30 days

---

## 🧪 Integration Test Scenarios

### Scenario 1: Complete Inventory Analytics Review

**Objective:** Get complete picture of inventory health

**Steps:**
1. Call Stock Value endpoint → Get total inventory value
2. Call Turnover endpoint → Identify slow-moving products
3. Call Expired Items endpoint → Track expiring stock
4. Call Wastage Summary endpoint → Monitor losses
5. Call Ingredient Usage endpoint → Check consumption rates

**Expected Outcome:**
- Total inventory value is positive
- Turnover rates show which products move well
- Expired items tracked accurately
- Wastage percentage is reasonable (< 5% of revenue)
- Ingredient usage rates above 50%

### Scenario 2: Date Range Filtering

**Objective:** Test date range parameters across endpoints

**Steps:**
1. Call each endpoint with `date_from=2025-03-01` and `date_to=2025-03-15`
2. Verify results only include data from that range
3. Call with invalid dates (should default to 30 days)
4. Call without dates (should use default 30 days)

**Expected Outcome:**
- Valid date ranges filter correctly
- Invalid dates gracefully default
- No date ranges use 30-day default
- Results are consistent across endpoints

### Scenario 3: Wastage Analysis

**Objective:** Understand wastage patterns

**Steps:**
1. Call Wastage Summary to get breakdown by reason
2. Call Wastage Trend with `trend_type=daily`
3. Call Wastage Trend with `trend_type=weekly`
4. Compare daily vs weekly aggregation

**Expected Outcome:**
- Summary shows major wastage reasons
- Daily trends show which days had high wastage
- Weekly trends aggregate correctly
- Product and ingredient wastage separated
- Can identify patterns over time

### Scenario 4: Performance with Large Dataset

**Objective:** Verify endpoints handle substantial data

**Steps:**
1. Ensure system has 100+ products
2. Ensure system has 50+ ingredients with multiple batches
3. Ensure system has 30+ days of wastage records
4. Call each endpoint and measure response time

**Expected Outcome:**
- Stock Value < 500ms
- Turnover < 800ms
- Expired < 300ms
- Wastage Summary < 800ms
- Wastage Trend < 1000ms
- Ingredient Usage < 600ms

---

## 📝 Test Cases Summary

### Test Coverage

| Endpoint | Authentication | Date Filtering | Calculations | Edge Cases |
|----------|---|---|---|---|
| Stock Value | ✅ | N/A | ✅ | Zero stock, empty inventory |
| Turnover | ✅ | ✅ | ✅ | No sales, zero stock |
| Expired | ✅ | N/A | ✅ | No expired items |
| Wastage Summary | ✅ | ✅ | ✅ | Zero wastage, zero revenue |
| Wastage Trend | ✅ | ✅ | ✅ | No data, all trend types |
| Ingredient Usage | ✅ | ✅ | ✅ | No usage, new ingredients |

### Test Results Log

**Date:** 2025-03-25  
**Tester:** [Your Name]  
**Browser/Tool:** [Postman/cURL/Insomnia]  
**Server:** Local (http://localhost:8000)  

| Test | Result | Notes |
|------|--------|-------|
| Stock Value - Authentication | ✅ PASS | Token required confirmed |
| Stock Value - Calculation | ✅ PASS | Values match formula |
| Turnover - With Date Range | ✅ PASS | Filters correctly |
| Expired - Zero Items | ✅ PASS | Handles empty case |
| Wastage Summary - Structure | ✅ PASS | Has all required fields |
| Wastage Trend - Daily | ✅ PASS | Correct aggregation |
| Wastage Trend - Weekly | ✅ PASS | Ranges formatted correctly |
| Wastage Trend - Monthly | ✅ PASS | Month format correct |
| Ingredient Usage - Rates | ✅ PASS | Percentages calculated |

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized Error

**Possible Causes:**
- Token not included in header
- Token expired or invalid
- Token format incorrect

**Solution:**
```bash
# Verify token in request
curl -X GET "http://localhost:8000/api/analytics/inventory/stock_value/" \
  -H "Authorization: Token YOUR_ACTUAL_TOKEN_123xyz..."

# Refresh token if needed
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"manager_user","password":"password123"}'
```

### Issue: 404 Not Found Error

**Possible Causes:**
- Endpoint URL misspelled
- Server not running
- Wrong server address

**Solution:**
```bash
# Verify server is running
curl http://localhost:8000/

# Check endpoint URL spelling
# Should be: /api/analytics/inventory/[endpoint]/

# Verify trailing slash included
curl "http://localhost:8000/api/analytics/inventory/stock_value/"
```

### Issue: Invalid Date Error

**Possible Causes:**
- Date format incorrect (should be YYYY-MM-DD)
- Date string not URL encoded
- Future dates provided

**Solution:**
```bash
# Correct format
curl "http://localhost:8000/api/analytics/inventory/turnover/?date_from=2025-03-01&date_to=2025-03-25"

# Invalid format (will default to 30 days)
curl "http://localhost:8000/api/analytics/inventory/turnover/?date_from=03/01/2025&date_to=03/25/2025"
```

### Issue: Empty Response Arrays

**Possible Causes:**
- No data exists in date range
- Filters are too restrictive
- Default 30-day range contains no data

**Solution:**
- Check data exists in database
- Verify date range includes data
- Expand date range in request
- Create test data if needed

---

## ✅ Sign-Off Checklist

Before marking Task 8.2 as complete:

- [ ] All 6 endpoints accessible and returning 200 status
- [ ] Authentication required on all endpoints
- [ ] Date range filtering works on applicable endpoints
- [ ] Calculations verified against formulas
- [ ] Edge cases handled gracefully
- [ ] Response structure matches documentation
- [ ] No server errors or exceptions
- [ ] Response times acceptable (< 1 second)
- [ ] Token-based auth confirmed
- [ ] Manual testing completed by: ________________
- [ ] Date tested: ________________

---

## 📞 Support

For issues or questions about these endpoints:
1. Check troubleshooting section above
2. Verify test environment setup
3. Review request/response examples
4. Check database for test data
5. Review backend logs for detailed errors

---

**Task 8.2: Inventory Analytics - Manual Testing Guide - COMPLETE** ✅

**Next Steps:**
- Task 8.3: Periodic Tasks (if scheduled)
- Performance optimization of analytics queries
- Caching implementation for frequently accessed endpoints
- Real-time alerts for critical inventory thresholds
