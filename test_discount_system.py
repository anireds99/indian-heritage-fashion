"""
Test suite for discount and coupon validation system
"""
import sys
sys.path.insert(0, '/Users/anirudhdev/FashionBrand')

from app import app, db
from models import Coupon, Order, User
from repositories import CouponRepository
from services import DiscountService

def test_coupon_validation():
    """Test coupon validation"""
    print("\n" + "="*60)
    print("TEST 1: Coupon Validation")
    print("="*60)
    
    with app.app_context():
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Valid coupon
        tests_total += 1
        coupon_repo = CouponRepository()
        validation = coupon_repo.validate_coupon('WELCOME10', 1000)
        if validation['valid']:
            print(f"✅ Valid coupon test passed")
            print(f"   Discount: ₹{validation['discount_amount']:.2f}")
            print(f"   Final Amount: ₹{validation['final_amount']:.2f}")
            tests_passed += 1
        else:
            print(f"❌ Valid coupon test failed: {validation['message']}")
        
        # Test 2: Minimum purchase amount not met
        tests_total += 1
        validation = coupon_repo.validate_coupon('WELCOME10', 300)
        if not validation['valid'] and 'Minimum' in validation['message']:
            print(f"✅ Minimum purchase validation test passed")
            print(f"   Message: {validation['message']}")
            tests_passed += 1
        else:
            print(f"❌ Minimum purchase validation failed")
        
        # Test 3: Expired coupon
        tests_total += 1
        validation = coupon_repo.validate_coupon('EXPIRED99', 5000)
        if not validation['valid']:
            print(f"✅ Expired coupon detection test passed")
            print(f"   Message: {validation['message']}")
            tests_passed += 1
        else:
            print(f"❌ Expired coupon detection failed")
        
        # Test 4: Non-existent coupon
        tests_total += 1
        validation = coupon_repo.validate_coupon('INVALID123', 1000)
        if not validation['valid'] and 'not found' in validation['message']:
            print(f"✅ Invalid coupon detection test passed")
            print(f"   Message: {validation['message']}")
            tests_passed += 1
        else:
            print(f"❌ Invalid coupon detection failed")
        
        # Test 5: Fixed discount
        tests_total += 1
        validation = coupon_repo.validate_coupon('SAVE100', 2000)
        if validation['valid'] and validation['discount_amount'] == 100:
            print(f"✅ Fixed discount calculation test passed")
            print(f"   Discount: ₹{validation['discount_amount']:.2f}")
            tests_passed += 1
        else:
            print(f"❌ Fixed discount calculation failed")
        
        # Test 6: Percentage discount with max limit
        tests_total += 1
        validation = coupon_repo.validate_coupon('SPECIAL20', 5000)
        if validation['valid'] and validation['discount_amount'] == 1000:  # 20% of 5000 = 1000, but max is 1000
            print(f"✅ Percentage discount with max limit test passed")
            print(f"   Discount: ₹{validation['discount_amount']:.2f} (capped at max)")
            tests_passed += 1
        else:
            print(f"❌ Percentage discount with max limit failed")
        
        print(f"\n✅ Passed: {tests_passed}/{tests_total}")
        return tests_passed == tests_total


def test_discount_service():
    """Test DiscountService"""
    print("\n" + "="*60)
    print("TEST 2: Discount Service")
    print("="*60)
    
    with app.app_context():
        tests_passed = 0
        tests_total = 0
        
        discount_service = DiscountService()
        
        # Test 1: Validate coupon through service
        tests_total += 1
        result = discount_service.validate_coupon('SUMMER15', 3000)
        if result['success']:
            print(f"✅ Service coupon validation test passed")
            print(f"   Discount: ₹{result['discount_amount']:.2f}")
            print(f"   Final Amount: ₹{result['final_amount']:.2f}")
            tests_passed += 1
        else:
            print(f"❌ Service coupon validation failed: {result['message']}")
        
        # Test 2: Invalid coupon through service
        tests_total += 1
        result = discount_service.validate_coupon('INVALID', 1000)
        if not result['success']:
            print(f"✅ Service invalid coupon detection test passed")
            tests_passed += 1
        else:
            print(f"❌ Service invalid coupon detection failed")
        
        # Test 3: Empty coupon code
        tests_total += 1
        result = discount_service.validate_coupon('', 1000)
        if not result['success'] and 'enter' in result['message'].lower():
            print(f"✅ Empty coupon code detection test passed")
            tests_passed += 1
        else:
            print(f"❌ Empty coupon code detection failed")
        
        print(f"\n✅ Passed: {tests_passed}/{tests_total}")
        return tests_passed == tests_total


def test_coupon_calculations():
    """Test discount calculations"""
    print("\n" + "="*60)
    print("TEST 3: Discount Calculations")
    print("="*60)
    
    with app.app_context():
        coupon_repo = CouponRepository()
        
        test_cases = [
            {
                'coupon': 'WELCOME10',
                'amount': 1000,
                'expected_discount': 100,
                'description': '10% of ₹1000'
            },
            {
                'coupon': 'WELCOME10',
                'amount': 5000,
                'expected_discount': 500,
                'description': '10% of ₹5000 (capped at ₹500)'
            },
            {
                'coupon': 'SAVE100',
                'amount': 2000,
                'expected_discount': 100,
                'description': 'Fixed ₹100 discount'
            },
            {
                'coupon': 'SPECIAL20',
                'amount': 3000,
                'expected_discount': 600,
                'description': '20% of ₹3000'
            },
            {
                'coupon': 'SUMMER15',
                'amount': 2000,
                'expected_discount': 300,
                'description': '15% of ₹2000 (capped at ₹750)'
            }
        ]
        
        passed = 0
        for test in test_cases:
            validation = coupon_repo.validate_coupon(test['coupon'], test['amount'])
            if validation['valid']:
                actual_discount = validation['discount_amount']
                expected = test['expected_discount']
                if abs(actual_discount - expected) < 0.01:  # Allow small floating point difference
                    print(f"✅ {test['description']}: ₹{actual_discount:.2f}")
                    passed += 1
                else:
                    print(f"❌ {test['description']}: Expected ₹{expected:.2f}, got ₹{actual_discount:.2f}")
            else:
                print(f"❌ {test['description']}: {validation['message']}")
        
        print(f"\n✅ Passed: {passed}/{len(test_cases)}")
        return passed == len(test_cases)


def test_database_integrity():
    """Test database integrity"""
    print("\n" + "="*60)
    print("TEST 4: Database Integrity")
    print("="*60)
    
    with app.app_context():
        try:
            coupons = Coupon.query.all()
            print(f"✅ Coupons table accessible")
            print(f"   Total coupons: {len(coupons)}")
            
            for coupon in coupons:
                status = "Active" if coupon.is_valid() else "Inactive/Expired"
                print(f"   • {coupon.code}: {coupon.description} ({status})")
            
            return True
        except Exception as e:
            print(f"❌ Database integrity check failed: {str(e)}")
            return False


def main():
    """Run all discount system tests"""
    print("\n" + "🧪 DISCOUNT & COUPON SYSTEM TEST SUITE 🧪".center(60))
    print("Testing coupon validation and discount calculations\n")
    
    results = []
    results.append(("Coupon Validation", test_coupon_validation()))
    results.append(("Discount Service", test_discount_service()))
    results.append(("Discount Calculations", test_discount_calculations()))
    results.append(("Database Integrity", test_database_integrity()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n✅ Total: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Discount system is ready to use.")
    else:
        print(f"\n⚠️ {total - passed} test suite(s) failed. Please review the output above.")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
