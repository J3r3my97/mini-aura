#!/usr/bin/env python3
"""
Test script for credit system
Run this to manually test credit logic without needing Stripe
"""
import asyncio
import sys
from google.cloud import firestore
from app.routes.generate import check_and_deduct_credit
from app.utils.firestore import get_user, create_user
from config import FREE_CREDITS

# Initialize Firestore
db = firestore.Client()


async def test_credit_system():
    """Test the credit deduction logic"""
    print("=" * 60)
    print("CREDIT SYSTEM TEST")
    print("=" * 60)

    test_user_id = "test_user_123"
    test_email = "test@example.com"

    print(f"\n1. Creating test user: {test_user_id}")
    try:
        # Delete if exists
        db.collection("users").document(test_user_id).delete()

        # Create fresh user
        await create_user(test_user_id, test_email)
        user = await get_user(test_user_id)
        print(f"✅ User created:")
        print(f"   - credits: {user.get('credits', 0)}")
        print(f"   - free_credits_used: {user.get('free_credits_used', 0)}")
        print(f"   - total_generated: {user.get('total_generated', 0)}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return

    # Test 1: Use free credit
    print(f"\n2. Test 1: Generate with free credit (should have watermark)")
    try:
        result = await check_and_deduct_credit(test_user_id)
        print(f"✅ Free credit used:")
        print(f"   - has_watermark: {result['has_watermark']}")
        user = await get_user(test_user_id)
        print(f"   - free_credits_used: {user.get('free_credits_used', 0)}/{FREE_CREDITS}")
        print(f"   - total_generated: {user.get('total_generated', 0)}")

        if not result['has_watermark']:
            print("❌ ERROR: Should have watermark for free credit!")
        else:
            print("✅ Watermark flag set correctly")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Try using another free credit (should fail)
    print(f"\n3. Test 2: Try generating again (should fail - no credits)")
    try:
        result = await check_and_deduct_credit(test_user_id)
        print(f"❌ ERROR: Should have failed! Got result: {result}")
    except Exception as e:
        if "No credits available" in str(e):
            print(f"✅ Correctly rejected: {e}")
        else:
            print(f"❌ Unexpected error: {e}")

    # Test 3: Add paid credits
    print(f"\n4. Test 3: Add 5 paid credits")
    try:
        db.collection("users").document(test_user_id).update({
            "credits": firestore.Increment(5)
        })
        user = await get_user(test_user_id)
        print(f"✅ Credits added:")
        print(f"   - credits: {user.get('credits', 0)}")
        print(f"   - free_credits_used: {user.get('free_credits_used', 0)}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4: Use paid credit
    print(f"\n5. Test 4: Generate with paid credit (no watermark)")
    try:
        result = await check_and_deduct_credit(test_user_id)
        print(f"✅ Paid credit used:")
        print(f"   - has_watermark: {result['has_watermark']}")
        user = await get_user(test_user_id)
        print(f"   - credits: {user.get('credits', 0)}")
        print(f"   - total_generated: {user.get('total_generated', 0)}")

        if result['has_watermark']:
            print("❌ ERROR: Should NOT have watermark for paid credit!")
        else:
            print("✅ No watermark flag - correct for paid credit")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 5: Use remaining credits
    print(f"\n6. Test 5: Use remaining 4 credits")
    for i in range(4):
        try:
            result = await check_and_deduct_credit(test_user_id)
            user = await get_user(test_user_id)
            print(f"   Generation {i+2}/5: credits={user.get('credits', 0)}, total={user.get('total_generated', 0)}")
        except Exception as e:
            print(f"❌ Error on generation {i+2}: {e}")

    user = await get_user(test_user_id)
    print(f"\n✅ Final state:")
    print(f"   - credits: {user.get('credits', 0)}")
    print(f"   - free_credits_used: {user.get('free_credits_used', 0)}")
    print(f"   - total_generated: {user.get('total_generated', 0)}")

    # Test 6: Try again with no credits
    print(f"\n7. Test 6: Try generating with no credits (should fail)")
    try:
        result = await check_and_deduct_credit(test_user_id)
        print(f"❌ ERROR: Should have failed!")
    except Exception as e:
        if "No credits available" in str(e):
            print(f"✅ Correctly rejected: {e}")
        else:
            print(f"❌ Unexpected error: {e}")

    # Cleanup
    print(f"\n8. Cleaning up test user...")
    try:
        db.collection("users").document(test_user_id).delete()
        print("✅ Test user deleted")
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_credit_system())
