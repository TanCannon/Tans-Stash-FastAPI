# FLOW DIAGRAM
```
USER
  |
  | clicks buy
  v

FRONTEND
  |
  | POST /create-order
  v

BACKEND
  |
  | creates Razorpay order
  v

RAZORPAY
  |
  | returns order_id
  v

BACKEND
  |
  | sends order_id to frontend
  v

FRONTEND
  |
  | opens Razorpay popup
  v

USER PAYS
  |
  v

RAZORPAY
  |
  | returns payment_id + signature
  v

FRONTEND
  |
  | POST /verify-payment
  v
{
  "plan_id": "pro_monthly",
  "order_id": "order_xxx",
  "payment_id": "pay_xxx",
  "signature": "mock_signature"
}
  |
  |
  v

BACKEND
  |
  | verifies signature
  |
  | activates subscription
  v

SUCCESS
```

# MORAL OF THE STORY

1. /verify-payment api will do both, verify signature and create the subscription.

