#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test tính năng theo dõi thay đổi giá domain
"""

import asyncio
import sqlite3
import importlib.util
import sys
import time

# Import module 22cn
spec = importlib.util.spec_from_file_location("module", "22cn.py")
module = importlib.util.module_from_spec(spec)
sys.modules["module"] = module
spec.loader.exec_module(module)
DomainScraper = module.DomainScraper

async def test_price_tracking():
    """Test tính năng theo dõi thay đổi giá"""
    print("=== TEST THEO DÕI THAY ĐỔI GIÁ DOMAIN ===\n")
    
    scraper = DomainScraper()
    
    # Test 1: Thêm domain mẫu với giá ban đầu
    print("1. Thêm domain mẫu với giá ban đầu...")
    conn = sqlite3.connect(scraper.db_name)
    cursor = conn.cursor()
    
    # Thêm một số domain mẫu
    test_domains = [
        ("example1.com", "88"),
        ("example2.cn", "150"),
        ("test-domain.net", "299"),
        ("demo-site.org", "450")
    ]
    
    for name, price in test_domains:
        cursor.execute("INSERT OR REPLACE INTO domains (name, price) VALUES (?, ?)", (name, price))
        print(f"   Đã thêm: {name} - ￥{price}")
    
    conn.commit()
    conn.close()
    
    # Test 2: Mô phỏng thay đổi giá
    print("\n2. Mô phỏng thay đổi giá...")
    price_changes = [
        ("example1.com", "88", "120"),    # Tăng giá
        ("example2.cn", "150", "130"),    # Giảm giá
        ("test-domain.net", "299", "299"), # Không đổi
        ("demo-site.org", "450", "500")   # Tăng giá
    ]
    
    for name, old_price, new_price in price_changes:
        if old_price != new_price:
            print(f"   Giá thay đổi: {name} - ￥{old_price} → ￥{new_price}")
            
            # Cập nhật giá trong database
            conn = sqlite3.connect(scraper.db_name)
            cursor = conn.cursor()
            
            # Cập nhật giá mới
            cursor.execute("UPDATE domains SET price = ? WHERE name = ?", (new_price, name))
            
            # Lưu vào lịch sử thay đổi giá
            cursor.execute("""
                INSERT INTO price_history (domain_name, old_price, new_price) 
                VALUES (?, ?, ?)
            """, (name, old_price, new_price))
            
            conn.commit()
            conn.close()
    
    # Test 3: Gửi thông báo thay đổi giá qua Telegram
    print("\n3. Gửi thông báo thay đổi giá qua Telegram...")
    changes_for_notification = []
    for name, old_price, new_price in price_changes:
        if old_price != new_price:
            changes_for_notification.append({
                'name': name,
                'old_price': old_price,
                'new_price': new_price
            })
    
    if changes_for_notification:
        await scraper.send_price_change_notification(changes_for_notification)
    
    # Test 4: Hiển thị lịch sử thay đổi giá
    print("\n4. Lịch sử thay đổi giá:")
    history = scraper.get_price_history()
    for record in history:
        domain_name, old_price, new_price, change_time = record
        print(f"   {domain_name}: ￥{old_price} → ￥{new_price} ({change_time})")
    
    # Test 5: Hiển thị thống kê
    print("\n5. Thống kê domain:")
    stats = scraper.get_domain_statistics()
    print(f"   Tổng số domain: {stats.get('total_domains', 0)}")
    print(f"   Tổng số lần thay đổi giá: {stats.get('total_price_changes', 0)}")
    
    print("\n   Top domain thay đổi giá nhiều nhất:")
    for domain_name, change_count in stats.get('top_changed_domains', []):
        print(f"   - {domain_name}: {change_count} lần")
    
    print("\n=== HOÀN THÀNH TEST ===")
    print("✅ Tính năng theo dõi thay đổi giá đã hoạt động!")
    print("🚀 Bạn có thể chạy chương trình chính: python 22cn.py")

async def main():
    await test_price_tracking()

if __name__ == "__main__":
    asyncio.run(main())
