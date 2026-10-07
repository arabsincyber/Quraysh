# جرّب كل الإصدارات
for v in v0.25.1 v0.26.2 v0.27.0 v0.27.7 stable; do
    echo "== جرّب $v =="
    curl -s -o /dev/null -w "%{http_code}" "https://cdn.jsdelivr.net/pyodide/$v/full/pyodide.js"
    echo " ← $v"
done
