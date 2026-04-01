"""
Create sample coupon codes for testing discount functionality
"""
import sys
sys.path.insert(0, '/Users/anirudhdev/FashionBrand')

from app import app, db
from models import Coupon
from datetime import datetime, timedelta, timezone

def create_sample_coupons():
    """Create sample coupons for testing"""
    print("\n" + "="*60)
    print("Creating Sample Coupons for Testing")
    print("="*60)
    
    with app.app_context():
        coupons_data = [
            {
                'code': 'WELCOME10',
                'description': 'Welcome discount - 10% off',
                'discount_type': 'percentage',
                'discount_value': 10,
                'valid_from': datetime.now(timezone.utc),
                'valid_until': datetime.now(timezone.utc) + timedelta(days=30),
                'max_uses': None,  # Unlimited
                'max_uses_per_user': 1,
                'min_purchase_amount': 500,
                'max_discount_amount': 500,
                'is_active': True
            },
            {
                'code': 'SAVE100',
                'description': 'Flat ₹100 discount',
                'discount_type': 'fixed',
                'discount_value': 100,
                'valid_from': datetime.now(timezone.utc),
                'valid_until': datetime.now(timezone.utc) + timedelta(days=60),
                'max_uses': 50,
                'max_uses_per_user': 2,
                'min_purchase_amount': 1000,
                'max_discount_amount': None,
                'is_active': True
            },
            {
                'code': 'SPECIAL20',
                'description': 'Special offer - 20% discount',
                'discount_type': 'percentage',
                'discount_value': 20,
                'valid_from': datetime.now(timezone.utc),
                'valid_until': datetime.now(timezone.utc) + timedelta(days=15),
                'max_uses': 25,
                'max_uses_per_user': 1,
                'min_purchase_amount': 2000,
                'max_discount_amount': 1000,
                'is_active': True
            },
            {
                'code': 'SUMMER15',
                'description': 'Summer sale - 15% off',
                'discount_type': 'percentage',
                'discount_value': 15,
                'valid_from': datetime.now(timezone.utc),
                'valid_until': datetime.now(timezone.utc) + timedelta(days=45),
                'max_uses': None,  # Unlimited
                'max_uses_per_user': 1,
                'min_purchase_amount': 0,
                'max_discount_amount': 750,
                'is_active': True
            },
            {
                'code': 'EXPIRED99',
                'description': 'Expired coupon (for testing)',
                'discount_type': 'percentage',
                'discount_value': 50,
                'valid_from': datetime.now(timezone.utc) - timedelta(days=60),
                'valid_until': datetime.now(timezone.utc) - timedelta(days=1),
                'max_uses': None,
                'max_uses_per_user': 1,
                'min_purchase_amount': 0,
                'max_discount_amount': None,
                'is_active': True
            }
        ]
        
        for coupon_data in coupons_data:
            try:
                existing = Coupon.query.filter_by(code=coupon_data['code']).first()
                if not existing:
                    coupon = Coupon(**coupon_data)
                    db.session.add(coupon)
                    db.session.commit()
                    print(f"✅ Created coupon: {coupon.code}")
                    print(f"   Description: {coupon.description}")
                    print(f"   Discount: {coupon.discount_value} ({coupon.discount_type})")
                    print(f"   Min Purchase: ₹{coupon.min_purchase_amount}")
                    print()
                else:
                    print(f"⚠️ Coupon already exists: {coupon_data['code']}")
            except Exception as e:
                print(f"❌ Error creating coupon {coupon_data['code']}: {str(e)}")
        
        # Print summary
        print("="*60)
        print("COUPON SUMMARY")
        print("="*60)
        total_coupons = Coupon.query.count()
        active_coupons = Coupon.query.filter_by(is_active=True).count()
        
        print(f"✅ Total Coupons: {total_coupons}")
        print(f"✅ Active Coupons: {active_coupons}")
        print("\n🎟️  Sample Coupons Created (Use these for testing):")
        print("   • WELCOME10 - 10% off (min ₹500)")
        print("   • SAVE100 - ₹100 flat discount (min ₹1000)")
        print("   • SPECIAL20 - 20% off (min ₹2000, max ₹1000)")
        print("   • SUMMER15 - 15% off (no minimum)")
        print("   • EXPIRED99 - Expired coupon (for testing)")
        print("="*60 + "\n")

if __name__ == '__main__':
    create_sample_coupons()
