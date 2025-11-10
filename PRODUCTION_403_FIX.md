# Fixing 403 Forbidden Error on Document Generation

## Problem

The API logs show:
```
INFO:     100.64.0.2:62140 - "POST /api/v1/credits/deduct?document_type=formal HTTP/1.1" 200 OK
INFO:     100.64.0.2:62140 - "POST /api/v1/generate/document HTTP/1.1" 403 Forbidden
```

**Credits deduction succeeds**, but **document generation returns 403 Forbidden**.

## Root Cause

The 403 error is thrown by `get_current_active_user()` dependency when:
```python
if not current_user.is_active:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user"
    )
```

This means the user account has `is_active: false` in the database.

## Solution

### Option 1: Activate the User Account (Recommended)

Run this script to activate all user accounts:

```python
# activate_users.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def activate_all_users():
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.get_database("docgen")

    # Update all users to be active
    result = await db.users.update_many(
        {"is_active": False},
        {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
    )

    print(f"✅ Activated {result.modified_count} user accounts")

    # Show all users
    users = db.users.find({})
    print("\nCurrent users:")
    async for user in users:
        print(f"  - {user['email']}: active={user['is_active']}, credits={user['credits']}")

    client.close()

if __name__ == "__main__":
    asyncio.run(activate_all_users())
```

Run it:
```bash
cd /home/taliban/doc-gen/backend
source venv/bin/activate
python activate_users.py
```

### Option 2: Check Specific User

To check a specific user's status:

```python
# check_user.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_user(email):
    mongodb_url = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(mongodb_url)
    db = client.get_database("docgen")

    user = await db.users.find_one({"email": email})

    if user:
        print(f"User: {email}")
        print(f"  ID: {user['_id']}")
        print(f"  is_active: {user.get('is_active', 'NOT SET')}")
        print(f"  is_verified: {user.get('is_verified', 'NOT SET')}")
        print(f"  credits: {user.get('credits', 0)}")
    else:
        print(f"User not found: {email}")

    client.close()

if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else "test@rapiddocs.io"
    asyncio.run(check_user(email))
```

Run it:
```bash
cd /home/taliban/doc-gen/backend
source venv/bin/activate
python check_user.py user@example.com
```

### Option 3: Update Registration to Always Set is_active=True

Ensure new users are always created with `is_active=True`:

In `backend/app/routes/auth.py`, verify the registration creates users with:
```python
new_user = {
    "email": user_data.email,
    "username": user_data.username,
    "hashed_password": hashed_password,
    "full_name": user_data.full_name,
    "credits": 0,
    "is_active": True,  # ← Make sure this is True
    "is_verified": True,  # ← And this
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}
```

## Testing After Fix

1. **Check user is active:**
   ```bash
   python check_user.py your@email.com
   ```

2. **Try document generation:**
   ```bash
   curl -X POST https://rapiddocs.io/api/v1/generate/document \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -F "description=Test document" \
        -F "length=500" \
        -F "document_type=formal" \
        -F 'statistics=[]' \
        -F 'design_spec={"background_color":"#FFFFFF","foreground_color_1":"#2563EB","foreground_color_2":"#06B6D4"}'
   ```

3. **Check server logs:**
   - Should see 200 OK instead of 403 Forbidden
   - Look for: `INFO: ... "POST /api/v1/generate/document HTTP/1.1" 200 OK`

## Why This Happened

When users register, they must have both:
- `is_active: true` - Account is active
- `is_verified: true` - Email is verified (if email verification is required)

If either is false, the `get_current_active_user()` dependency will reject the request with 403 Forbidden.

## Prevention

1. **Always create users with is_active=True** (unless you want manual approval)
2. **Set is_verified=True** (or implement email verification)
3. **Don't accidentally set is_active=False** during updates
4. **Add logging** to see why users might become inactive:

```python
logger.info(f"User {user.email}: is_active={user.is_active}, is_verified={user.is_verified}")
```

## Quick Fix Command

```bash
# Activate all users
cd /home/taliban/doc-gen/backend
source venv/bin/activate
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def fix():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client.get_database('docgen')
    result = await db.users.update_many(
        {},
        {'\\$set': {'is_active': True, 'is_verified': True, 'updated_at': datetime.utcnow()}}
    )
    print(f'✅ Updated {result.modified_count} users')
    client.close()

asyncio.run(fix())
"
```

---

**Last Updated:** 2025-11-10
**Status:** Solution provided - activate user accounts
