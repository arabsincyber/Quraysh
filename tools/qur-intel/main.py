import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from quraysh.intel import domain as domain_scanner
from quraysh.intel import url_scanner
from quraysh.intel import port_scanner
from quraysh.intel import ssl_scanner
from quraysh.intel import wallet_scanner

def cmd_domain(domain):
    print(f"[*] جاري فحص النطاق: {domain}")
    print("\n--- WHOIS ---")
    print(domain_scanner.get_whois(domain))
    print("\n--- DNS ---")
    print(domain_scanner.get_dns(domain))
    print("\n--- IP & Geo ---")
    print(domain_scanner.get_ip_info(domain))

def cmd_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    print(f"[*] جاري فحص الرابط: {url}\n")
    result = url_scanner.scan_url(url)
    print(f"🔗 الرابط: {result['url']}")
    print(f"📊 حالة الاستجابة: {result['status_code']}")
    print(f"🌐 الرابط النهائي: {result['final_url']}")
    print(f"🖥️  السيرفر: {result['server']}")
    print(f"🔒 SSL صالح: {'نعم' if result['ssl_valid'] else 'لا'}")
    if result['redirects']:
        print(f"\n🔄 التحويلات ({len(result['redirects'])}):")
        for r in result['redirects']:
            print(f"   {r['status']} → {r['to']}")
    print(f"\n⚠️  درجة الخطورة: {result['risk_level']} ({result['risk_score']}/100)")
    if result['warnings']:
        print(f"\n📋 التحذيرات:")
        for w in result['warnings']:
            print(f"   - {w}")

def cmd_ports(host):
    result = port_scanner.check_ports_report(host)
    print("\n--- تقرير المنافذ ---")
    print(f"المنافذ المفتوحة: {result.get('open_ports', 'لا يوجد')}")
    if 'warnings' in result:
        print("التحذيرات:")
        for w in result['warnings']:
            print(w)

def cmd_ssl(host):
    print(f"[*] جاري فحص شهادة SSL لـ: {host}\n")
    result = ssl_scanner.check_ssl(host)
    print(f"🖥️  المضيف: {result['host']}")
    print(f"🏢 الجهة المصدرة: {result['issuer'].get('organizationName', 'غير معروف')}")
    print(f"📅 صالحة من: {result['valid_from']}")
    print(f"📅 صالحة حتى: {result['valid_to']}")
    print(f"⏳ الأيام المتبقية: {result['days_left']}")
    print(f"🛡️  الحالة: {result['status']}")
    if result['warnings']:
        print("\n⚠️ التحذيرات:")
        for w in result['warnings']:
            print(f"   - {w}")

def cmd_wallet(address):
    print(f"[*] جاري فحص المحفظة: {address}\n")
    result = wallet_scanner.scan_wallet(address)
    print(f"📍 العنوان: {result['address']}")
    print(f"🏷️  النوع: {result['type']}")
    print(f"🌐 الشبكة: {result['network']}")
    print(f"💰 الرصيد: {result['balance']}")
    print(f"✅ صالح: {'نعم' if result['valid'] else 'لا'}")
    if result['warnings']:
        print("\n⚠️ التحذيرات:")
        for w in result['warnings']:
            print(f"   - {w}")

def main():
    parser = argparse.ArgumentParser(description="لسان قريش - أداة الفحص الاستخباراتي الدفاعي")
    subparsers = parser.add_subparsers(dest="command", help="الأوامر المتاحة")

    parser_domain = subparsers.add_parser("domain", help="فحص نطاق (WHOIS, DNS, IP)")
    parser_domain.add_argument("target", help="النطاق المراد فحصه")

    parser_url = subparsers.add_parser("url", help="فحص رابط مشبوه")
    parser_url.add_argument("target", help="الرابط المراد فحصه")

    parser_ports = subparsers.add_parser("ports", help="فحص المنافذ المفتوحة (دفاعياً)")
    parser_ports.add_argument("target", help="الهدف (IP أو اسم النطاق)")

    parser_ssl = subparsers.add_parser("ssl", help="فحص شهادة SSL لنطاق")
    parser_ssl.add_argument("target", help="النطاق المراد فحص شهادته")

    parser_wallet = subparsers.add_parser("wallet", help="فحص محفظة رقمية (BTC, ETH, TRX)")
    parser_wallet.add_argument("target", help="عنوان المحفظة")

    args = parser.parse_args()

    if args.command == "domain":
        cmd_domain(args.target)
    elif args.command == "url":
        cmd_url(args.target)
    elif args.command == "ports":
        cmd_ports(args.target)
    elif args.command == "ssl":
        cmd_ssl(args.target)
    elif args.command == "wallet":
        cmd_wallet(args.target)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
