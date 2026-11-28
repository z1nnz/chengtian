#!/bin/sh
# DR12 樹皮片 L 的 Unity 檢查（不改 apps/game）：DR12Verify.cs 只在這次批次執行時複製進專案，跑完刪掉它、暫時的模型副本，並還原這次執行動到的 URP／專案設定。
#   UNITY=<Unity.exe 6000.3.28f1> sh art/source/d2-logs-b/unity/run_unity_dr12.sh   （在 repo 根目錄跑；期望值讀 art/exports/d2-logs-b/DR12_BarkSheet_L/model_info.json）
# 結果：art/previews/d2-logs-b/DR12_BarkSheet_L/unity/report.txt 與出圖；log 在 artifacts/unity-dr12.log。
set -e
U="${UNITY:?set UNITY to Unity.exe (6000.3.28f1)}";HERE=art/source/d2-logs-b/unity
ED=apps/game/Assets/YunJing/Editor;M=apps/game/Assets/YunJing/Models/D2LogsB
cleanup(){
  rm -f "$ED/DR12Verify.cs" "$ED/DR12Verify.cs.meta"; rm -rf "$M" "$M.meta"
  git checkout -- apps/game/Assets/WebGLTemplates.meta apps/game/ProjectSettings apps/game/Packages 2>/dev/null || true
}
trap cleanup EXIT
cp "$HERE/DR12Verify.cs" "$ED/"
mkdir -p artifacts
"$U" -batchmode -quit -projectPath apps/game -executeMethod YunJing.Editor.DR12Verify.Run -logFile artifacts/unity-dr12.log || true
grep -E "DR12_VERIFY|DR12 (PASS|FAIL|INFO)|error CS" artifacts/unity-dr12.log || echo "no verify line, see artifacts/unity-dr12.log"
