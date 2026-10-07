import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.mjs";

// 🕋 لسان قريش — الملعب التفاعلي

let pyodide = null;
let isReady = false;

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

window.updateStatus = function updateStatus(text, نوع = "info") {
    const status = document.getElementById("status");
    const statusText = document.getElementById("status-text");
    if (status && statusText) {
        statusText.textContent = text;
        status.className = "info-banner " + نوع;
    }
}

window.loadExample = function loadExample(اسم) {
    document.getElementById("code").value = الأمثلة[اسم] || "";
}

window.clearOutput = function clearOutput() {
    document.getElementById("output").textContent = "في انتظار تشغيل الكود...";
}

window.runCode = async function runCode() {
    if (!isReady) {
        alert("⚠️ انتظر تحميل المفسّر...");
        return;
    }

    const code = document.getElementById("code").value;
    const output = document.getElementById("output");
    output.textContent = "⏳ جاري التشغيل...\n";

    try {
        pyodide.globals.set("_user_code", code);

        const نتيجة = await pyodide.runPythonAsync(`
import sys
from io import StringIO

_old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    from quraysh.evaluator import Quraysh
    q = Quraysh()
    code = _user_code
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
    } catch (error) {
        output.textContent = "❌ خطأ: " + error.message;
    }
}

async function initialize() {
    try {
        updateStatus("⏳ جاري تحميل Python (Pyodide)...", "info");

        pyodide = await loadPyodide();

        updateStatus("⏳ تحميل quraysh...", "info");

        const ملفات = [
            "lexer", "parser", "environment", "evaluator",
            "crypto", "networks", "sql", "files",
            "basic", "fortran", "cobol", "bigram", "tutor"
        ];

        pyodide.FS.writeFile("/tmp/__init__.py", "");

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
                pyodide.FS.writeFile(`/tmp/${ملف}.py`, كود);
                نجح++;
                updateStatus(`⏳ تحميل quraysh... (${نجح}/${ملفات.length})`, "info");
            } catch (e) {
                فشل.push(ملف);
            }
        }

        pyodide.runPython(`
import sys
sys.path.insert(0, "/tmp")
        `);

        try {
            pyodide.runPython(`
from quraysh.evaluator import Quraysh
q = Quraysh()
_ = q.eval_string('(+ 2 3)')
            `);
            updateStatus(`✅ جاهز! (${نجح}/${ملفات.length} ملف)`, "ready");
            isReady = true;
            document.getElementById("run").disabled = false;
        } catch (e) {
            updateStatus(`⚠️ ${نجح}/${ملفات.length} ملف، الاستيراد فشل: ${e.message}`, "error");
        }
    } catch (error) {
        updateStatus("❌ فشل التحميل: " + error.message, "error");
        alert("خطأ: " + error.message);
    }
}

initialize();
