import time
import logging
import datetime
from dataclasses import dataclass
from typing import Dict, Any, List

logger = logging.getLogger("qur-intel")

@dataclass
class ScanResult:
    target: str
    module: str
    status: str
    data: Any = None
    source: str = ""
    error: str = ""
    duration: float = 0.0

class IntelCore:
    def __init__(self, target: str, authorized: bool = False):
        if not authorized:
            raise PermissionError("⚠️ يجب تأكيد التصريح (--authorized) لبدء الفحص.")
        self.target = target
        self.results: List[ScanResult] = []
        self.start_time = time.time()

    def run_module(self, module_name: str, scan_func, source: str = "Direct"):
        print(f"[*] جاري فحص {module_name} ...", end=" ", flush=True)
        start = time.time()
        try:
            data = scan_func(self.target)
            duration = time.time() - start
            print("✅")
            self.results.append(ScanResult(target=self.target, module=module_name, status="success", data=data, source=source, duration=duration))
            return data
        except Exception as e:
            duration = time.time() - start
            print("❌")
            self.results.append(ScanResult(target=self.target, module=module_name, status="failed", error=str(e), source=source, duration=duration))
            return None

    def calculate_risk(self) -> int:
        """حساب درجة خطورة تقريبية من 100"""
        score = 0
        for res in self.results:
            if res.module == "WHOIS" and res.status == "success":
                if "1998" not in str(res.data.get("creation_date", "")):
                    score += 20 # نطاق جديد (حديث) يعتبر مشبوهاً
            if res.module == "SSL Certificate" and res.status == "success":
                if "Let's Encrypt" in str(res.data.get("issuer", "")):
                    score += 10 # شهادات مجانية (شائعة في التصيد)
            if res.module == "IP & Geo Info" and res.status == "success":
                country = res.data.get("country", "")
                if country in ["Russia", "China", "Iran"]:
                    score += 30 # دول عليها حظر أو اشتباه
        return min(score, 100) # الحد الأقصى 100

    def export_markdown(self, filename: str):
        """حفظ التقرير في ملف Markdown"""
        summary = self.get_summary()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# تقرير الفحص الاستخباراتي: {self.target}\n")
            f.write(f"**تاريخ الفحص:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**درجة الخطورة:** {self.calculate_risk()}/100 ⚠️\n\n")
            f.write("## 📊 النتائج التفصيلية\n")
            for res in self.results:
                f.write(f"### {res.module}\n")
                if res.status == "success":
                    for k, v in res.data.items():
                        f.write(f"- **{k}:** {v}\n")
                else:
                    f.write(f"- ❌ فشل: {res.error}\n")
                f.write("\n")
            f.write("---\n")
            f.write("*تم التوليد بواسطة أداة لسان قريش الاستخباراتية (qur-intel)*\n")
        print(f"✅ تم حفظ التقرير بنجاح في الملف: {filename}")

    def get_summary(self) -> Dict:
        success = sum(1 for r in self.results if r.status == "success")
        failed = sum(1 for r in self.results if r.status == "failed")
        return {"target": self.target, "total_modules": len(self.results), "success": success, "failed": failed, "total_time": round(time.time() - self.start_time, 2), "results": self.results}
