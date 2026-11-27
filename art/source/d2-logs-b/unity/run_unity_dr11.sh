#!/bin/sh
# DR11 根盤 B 的 Unity 檢查（不改 apps/game）：DR11Verify.cs 只在這次批次執行時複製進專案，跑完刪掉它、暫時的模型副本，並還原這次執行動到的 URP／專案設定。
#   UNITY=<Unity.exe 6000.3.28f1> DR11_VER=v002 DR11_EXPECT=<Blender 量好的期望值 json> sh art/source/d2-logs-b/unity/run_unity_dr11.sh   （在 repo 根目錄跑）
# 期望值 json：{"dims":[x,y,z], "min":[x,y,z], "tris":[LOD0,LOD1,LOD2（本體＋植物）], "col":碰撞殼面數}，從 blend/DR11_RootPlate_B_<版本>.blend 量。
# 結果：art/previews/d2-logs-b/DR11_RootPlate_B/unity_<版本>/report.txt 與出圖；log 在 artifacts/unity-dr11.log。
set -e
U="${UNITY:?set UNITY to Unity.exe (6000.3.28f1)}";HERE=art/source/d2-logs-b/unity
: "${DR11_EXPECT:?set DR11_EXPECT to the expected-values json}"
ED=apps/game/Assets/YunJing/Editor;M=apps/game/Assets/YunJing/Models/D2LogsB
cleanup(){
  rm -f "$ED/DR11Verify.cs" "$ED/DR11Verify.cs.meta"; rm -rf "$M" "$M.meta"
  git checkout -- apps/game/Assets/WebGLTemplates.meta apps/game/ProjectSettings apps/game/Packages 2>/dev/null || true
}
trap cleanup EXIT
cp "$HERE/DR11Verify.cs" "$ED/"
mkdir -p artifacts
"$U" -batchmode -quit -projectPath apps/game -executeMethod YunJing.Editor.DR11Verify.Run -logFile artifacts/unity-dr11.log || true
grep -E "DR11_VERIFY|DR11 (PASS|FAIL|INFO)|error CS" artifacts/unity-dr11.log || echo "no verify line, see artifacts/unity-dr11.log"
