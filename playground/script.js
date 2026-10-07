// 🕋 لسان قريش — الملعب التفاعلي
// =====================================

let pyodide = null;
let isReady = false;

// الأمثلة الجاهزة
const الأمثلة = {
    welcome: `; مرحبا بك في لسان قريش 🕋
(اطبع "السلام عليكم")
(تعريف مربع (لامدا (ن) (* ن ن)))
(اطبع (مربع 5))`,

    calc: `; حاسبة بسيطة
(اطبع "=== حاسبة ===")
(اطبع (ألّم 10 20))
(اطبع (جَلَد 5 6))
(اطبع (جذر_ن 144))
(اطبع (زوجي 8))`,

    crypto: `; مكتبة التشفير 🔐
(اطبع (بصمة_نص "لسان قريش"))
(اطبع (ترميز_base64 "قريش"))
(اطبع (تشفير_xor "لسان" "سر"))`,

    sql: `; قاعدة بيانات 🗄️
(أنشئ_جدول "طلاب" (قائمة "اسم" "عمر" "مدينة"))
(أدرج "طلاب" "اسم" "محمد" "عمر" 25 "مدينة" "الرياض")
(أدرج "طلاب" "اسم" "صالح" "عمر" 30 "مدينة" "جدة")
(اعرض "طلاب")`
};

// تحديث الحالة
function updateStatus(text, نوع = "info") {
    const status = document.getElementById("status");
    const statusText = document.getElementById("status-text");
    statusText.textContent = text;
    status.className = "info-banner " + نوع;
}

// تحميل مثال
function loadExample(اسم) {
    document.getElementById("code").value = الأمثلة[اسم] || "";
}

// مسح النتيجة
function clearOutput() {
    document.getElementById("output").textContent = "في انتظار تشغيل الكود...";
}

// تشغيل الكود
async function runCode() {
    if (!isReady) {
        alert("⚠️ انتظر تحميل المفسّر...");
        return;
    }

    const code = document.getElementById("code").value;
    const output = document.getElementById("output");

    output.textContent = "⏳ جاري التشغيل...\n";

    try {
        // نمرّر الكود إلى Python
        const نتيجة = await pyodide.runPythonAsync(`
import sys
from io import StringIO

# التقاط stdout
_old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    from quraysh.evaluator import Quraysh
    q = Quraysh()
    # نفّذ كل سطر
    for line in ${JSON.stringify(code)}.split("\\n"):
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        try:
            r = q.eval_string(line)
            if r is not None:
                print(r)
        except Exception as e:
            print(f"❌ خطأ: {e}")
except Exception as e:
    print(f"❌ خطأ في التحميل: {e}")

_result = sys.stdout.getvalue()
sys.stdout = _old_stdout
_result
        `);

        output.textContent = نتيجة || "(لا نتيجة)";
        output.className = "success";
    } catch (error) {
        output.textContent = "❌ خطأ: " + error.message;
        output.className = "error";
    }
}

// تحميل Pyodide + quraysh
async function initialize() {
    try {
        updateStatus("⏳ جاري تحميل Python (Pyodide)...", "info");

        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"
        });

        updateStatus("⏳ جاري تحميل لسان قريش...", "info");

        // نحمّل ملفات quraysh من GitHub
        const ملفات = [
            "lexer", "parser", "environment", "evaluator",
            "crypto", "networks", "sql", "files",
            "basic", "fortran", "cobol", "bigram", "tutor"
        ];

        // أنشئ الحزمة
        pyodide.runPython(`
import sys
import os
import types

# أنشئ حزمة quraysh
quraysh_pkg = types.ModuleType("quraysh")
quraysh_pkg.__path__ = ["/quraysh"]
sys.modules["quraysh"] = quraysh_pkg
        `);

        // حمّل كل ملف Python
        for (const ملف of ملفات) {
            const url = `https://raw.githubusercontent.com/arabsincyber/Quraysh/main/src/quraysh/${ملف}.py`;
            const response = await fetch(url);
            if (!response.ok) {
                console.warn(`⚠️ فشل تحميل: ${ملف}`);
                continue;
            }
            const كود = await response.text();
            try {
                pyodide.runPython(`
import sys
_كود = ${JSON.stringify(كود)}
exec(compile(_كود, "quraysh/${ملف}.py", "exec"), sys.modules["quraysh"].__dict__)
                `);
            } catch (e) {
                console.warn(`⚠️ خطأ في ${ملف}:`, e.message);
            }
        }

        updateStatus("✅ جاهز! اكتب كودك واضغط تشغيل", "ready");
        isReady = true;
        document.getElementById("run").disabled = false;
    } catch (error) {
        updateStatus("❌ فشل التحميل: " + error.message, "error");
        console.error(error);
    }
}

// بدء التحميل
initialize();
