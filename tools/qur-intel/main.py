import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from quraysh.intel import domain as domain_scanner
from quraysh.intel import url_scanner
from quraysh.intel import port_scanner

def cmd_domain(domain):
    print(f"[*] جاري فحص النطاق: {domain}")
    print("\n--- WHOIS ---")
    print(domain_scanner.get_whois(domain))
    print("\n--- DNS ---")
    print(domain_scanner.get_dns(domain))
    print("\n--- IP & Geo ---")
    print(domain_scanner.get_ip_info(domain))

def cmd_ports(host):
    result = port_scanner.check_ports_report(host)
    print("\n--- تقرير المنافذ ---")
    print(f"المنافذ المفتوحة: {result.get('open_ports', 'لا يوجد')}")
    if 'warnings' in result:
        print("التحذيرات:")
        for w in result['warnings']:
            print(w)

def main():
    parser = argparse.ArgumentParser(description="لسان قريش - أداة الفحص الاستخباراتي الدفاعي")
    subparsers = parser.add_subparsers(dest="command", help="الأوامر المتاحة")

    parser_domain = subparsers.add_parser("domain", help="فحص نطاق (WHOIS, DNS, IP)")
    parser_domain.add_argument("target", help="النطاق المراد فحصه")

    parser_url = subparsers.add_parser("url", help="فحص رابط مشبوه")
    parser_url.add_argument("target", help="الرابط المراد فحصه")

    parser_ports = subparsers.add_parser("ports", help="فحص المنافذ المفتوحة (دفاعياً)")
    parser_ports.add_argument("target", help="الهدف (IP أو اسم النطاق)")

    args = parser.parse_args()

    if args.command == "domain":
        cmd_domain(args.target)
    elif args.command == "url":
        cmd_url(args.target)
    elif args.command == "ports":
        cmd_ports(args.target)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
