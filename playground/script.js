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
(اطبع (جذر_ن 144))`,

    crypto: `; مكتبة التشفير 🔐
(اطبع (بصمة_نص "لسان قريش"))
(اطبع (ترميز_base64 "قريش"))
(اطبع (تشفير_xor "لسان" "سر"))`,

    sql: `; قاعدة بيانات 🗄️
(أنشئ_جدول "طلاب" (قائمة "اسم" "عمر"))
(أدرج "طلاب" "اسم" "محمد" "عمر" 25)
(اعرض "طلاب")`
};

function updateStatus(text, نوع = "info") {
    const status = document.getElementById("status");
    const statusText = document.getElementById("status-text");
    statusText.textContent = text;
    status.className = "info-banner " + نوع;
}

function loadExample(اسم) {
    document.getElementById("code").value = الأمثلة[اسم] || "";
}

function clearOutput() {
    document.getElementById("output").textContent = "في انتظار تشغيل الكود...";
}

async function runCode() {
    if (!isReady) {
        alert("⚠️ انتظر تحميل المفسّر...");
        return;
    }

    const code = document.getElementById("code").value;
    const output = document.getElementById("output");
    output.textContent = "⏳ جاري التشغيل...\n";

    try {
        // ضع الكود في ملف مؤقت
        pyodide.FS.writeFile("/home/pyodide/_user_code.txt", code);

        const نتيجة = await pyodide.runPythonAsync(`
import sys
from io import StringIO

_old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    from quraysh.evaluator import Quraysh
    q = Quraysh()

    with open("/home/pyodide/_user_code.txt", "r", encoding="utf-8") as f:
        code = f.read()

    for line in code.split("\\n"):
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        try:
            r = q.eval_string(line)
            if r is not None:
                print(r)
        except Exception as e:
            print(f"❌ {e}")
except Exception as e:
    print(f"❌ خطأ: {e}")

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

async function initialize() {
    try {
        updateStatus("⏳ جاري تحميل Python (Pyodide)...", "info");

        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"
        });

        updateStatus("⏳ جاري تحميل لسان قريش (13 ملف)...", "info");

        // أنشئ مجلد quraysh في Pyodide FS
        pyodide.runPython(`
import os
os.makedirs("/home/pyodide/quraysh", exist_ok=True)
import sys
sys.path.insert(0, "/home/pyodide")
        `);

        const ملفات = [
            "lexer", "parser", "environment", "evaluator",
            "crypto", "networks", "sql", "files",
            "basic", "fortran", "cobol", "bigram", "tutor"
        ];

        let نجح = 0;
        let فشل = [];

        for (const ملف of ملفات) {
            try {
                const url = `https://raw.githubusercontent.com/arabsincyber/Quraysh/main/src/quraysh/${ملف}.py`;
                const response = await fetch(url);
                if (!response.ok) {
                    فشل.push(ملف);
                    continue;
                }
                const كود = await response.text();
                // اكتب الملف في نظام Pyodide
                pyodide.FS.writeFile(`/home/pyodide/quraysh/${ملف}.py`, كود);
                نجح++;
                updateStatus(`⏳ تحميل quraysh... (${نجح}/${ملفات.length})`, "info");
            } catch (e) {
                console.warn(`خطأ في ${ملف}:`, e.message);
                فشل.push(ملف);
            }
        }

        if (فشل.length > 0) {
            updateStatus(`⚠️ تحمّل ${نجح}/${ملفات.length} — فشل: ${فشل.join(", ")}`, "error");
        }

        // أنشئ ملف __init__.py فارغ
        pyodide.FS.writeFile("/home/pyodide/quraysh/__init__.py", "");

        // اختبر الاستيراد
        pyodide.runPython(`
import sys
sys.path.insert(0, "/home/pyodide")
from quraysh.evaluator import Quraysh
q = Quraysh()
test = q.eval_string('(اطبع "اختبار")')
        `);

        updateStatus(`✅ جاهز! تحمّل ${نجح}/${ملفات.length} ملف`, "ready");
        isReady = true;
        document.getElementById("run").disabled = false;
    } catch (error) {
        updateStatus("❌ فشل التحميل: " + error.message, "error");
        console.error("ERROR:", error); console.error("STACK:", error.stack); alert("خطأ: " + error.message);
    }
}

initialize();
