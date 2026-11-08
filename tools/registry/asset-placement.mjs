// 承天物件整合清冊。只讀現有檔案與場景配置；不把「有檔案」當成「遊戲裡看得到」。
// node tools/registry/asset-placement.mjs [--check]
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, relative, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const out = join(root, 'docs', 'registry', 'asset-placement.md');
const exportsRoot = join(root, 'art', 'exports');
const unityRoot = join(root, 'apps', 'game', 'Assets');
const read = p => readFileSync(p, 'utf8');
const norm = p => p.replaceAll('\\', '/');
const esc = value => String(value ?? '').replaceAll('|', '\\|').replaceAll('\n', ' ');

function files(dir, suffix) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? files(path, suffix) : entry.name.toLowerCase().endsWith(suffix) ? [path] : [];
  });
}

function origins() {
  const map = new Map();
  const source = join(root, 'docs', 'registry', 'folders.md');
  if (!existsSync(source)) return map;
  for (const line of read(source).split('\n')) {
    const match = line.match(/^\| `art\/exports\/([^`]+)` \| ([^|]+) \| ([^|]+) \|/);
    if (match) map.set(match[1], { owner: match[2].trim(), pr: match[3].match(/#\d+/)?.[0] ?? '—' });
  }
  for (const name of ['sky-and-distance-v1', 'valley-and-home-v1']) map.set(name, { owner: 'Codex（舊分支交付）', pr: '尚無 PR' });
  for (const name of ['elder-trees-v1', 'qingxi-ground-v1']) map.set(name, { owner: '核心組', pr: '待查' });
  return map;
}

const plannedBlocks = {
  'aptitude-plaza-v1': 'B2', 'creek-repair-b': 'A3／D3', 'creek-repair-b-props': 'A1／A3／D3',
  'elder-trees-v1': 'A1／D1', 'elder-world-tree-hero-v1': 'D2', 'giant-tree-v1': 'D2',
  'harvest-market-b': 'A1', 'irrigation-v1': 'A6', 'irrigation-v2': 'A6',
  'modelling-basics-c': 'A1／A2／A3／D1／D3', 'qingxi-alchemy-b': 'A1', 'qingxi-alchemy-table-v1': 'A1',
  'qingxi-day12-c': 'A1／A2', 'qingxi-day34-c': 'A3／D3', 'qingxi-encounter-a': 'D1',
  'qingxi-gathering-visual-kit-v1': 'A1／D1', 'qingxi-ground-v1': 'A1／A2／A3／D1／D3',
  'qingxi-mountain-rabbit-v003': 'D1', 'qingxi-return-c': 'A1', 'qingxi-training-yard-v1': 'A1',
  'qingxi-village-signs-v1': 'A1', 'qingxi-water-report-c': 'A1', 'qingxi-waterhead-a': 'A3／D3',
  'qingxi-waterworks-b': 'A1／A3', 'qingxi-world-ruins-b': 'A2／A3／D3',
  'tea-brewing-b': 'A4', 'tea-terraces-b': 'A4', 'territory-backyard-a': '屬領地',
  'territory-interior-b': '屬領地', 'world-props-a': 'A1／A2／A3／D1／D3', 'zhuo-boar-a': 'D1',
};

const placementFiles = [join(root, 'tools', 'qingxi-terrain', 'novice-village.json'), ...files(join(root, 'tools', 'qingxi-terrain', 'blocks'), '.json')];
const placements = [];
for (const path of placementFiles) {
  const data = JSON.parse(read(path));
  const block = data.block ?? 'A1';
  for (const entry of [...(data.placements ?? []), ...(data.crossingSlots ?? [])]) {
    placements.push({ ...entry, block, file: norm(relative(root, path)) });
  }
}

const unityModels = files(unityRoot, '.fbx');
const byName = new Map();
for (const path of unityModels) {
  const key = basename(path).toLowerCase();
  if (!byName.has(key)) byName.set(key, []);
  byName.get(key).push('Assets/' + norm(relative(unityRoot, path)));
}

const scriptText = files(join(unityRoot, 'YunJing', 'Editor'), '.cs').map(read).join('\n');
const setup = origins();
const fbx = files(exportsRoot, '.fbx');
const fbxStems = new Set(fbx.map(p => p.slice(0, -4).toLowerCase()));
const models = [...fbx, ...files(exportsRoot, '.glb').filter(p => !fbxStems.has(p.slice(0, -4).toLowerCase()))]
  .sort((a, b) => norm(a).localeCompare(norm(b)));
const rows = models.map(path => {
  const exportPath = norm(relative(root, path));
  const set = norm(relative(exportsRoot, path)).split('/')[0];
  const filename = basename(path);
  const unity = byName.get(filename.toLowerCase()) ?? [];
  const direct = placements.filter(p => p.model && unity.includes(p.model));
  const referenced = unity.filter(p => scriptText.includes(p));
  const info = setup.get(set) ?? { owner: '待查', pr: '—' };
  const family = norm(relative(exportsRoot, path)).split('/')[1];
  const planned = direct.length ? [...new Set(direct.map(p => p.block))].join('／')
    : set === 'valley-and-home-v1' ? (/^FE/.test(family) ? 'A5' : 'A6')
    : plannedBlocks[set] ?? '待指定';
  let state = '素材檔；未證實匯入';
  if (unity.length) state = 'Unity 已匯入；未證實擺放';
  if (referenced.length) state = '生成程式引用；未截圖確認';
  if (direct.length) state = '區塊資料配置；未截圖確認';
  return { set, exportPath, unity, direct, referenced, planned, state, ...info };
});

// 空格位也要列出；它們是目前場景密度的缺口，不可從模型清單反推成已完成。
const gaps = placements.filter(p => !p.model || p.status === 'needed');
const counts = new Map(readdirSync(exportsRoot, { withFileTypes: true })
  .filter(entry => entry.isDirectory())
  .map(entry => [entry.name, { total: 0, imported: 0, placed: 0 }]));
for (const row of rows) {
  if (!counts.has(row.set)) counts.set(row.set, { total: 0, imported: 0, placed: 0 });
  const c = counts.get(row.set); c.total++;
  if (row.unity.length) c.imported++;
  if (row.direct.length || row.referenced.length) c.placed++;
}

const lines = [
  '# 物件整合清冊', '',
  '> 由 `node tools/registry/asset-placement.mjs` 從目前分支的 FBX（另補只含 GLB 的物件）、Unity 模型檔、區塊 JSON 與 Editor 程式產生。這是靜態證據；「配置」仍須遊戲截圖驗收。來源 PR 採 `docs/registry/folders.md`，新交付而尚無 PR 的資料夾標待查。', '',
  `模型檔 ${rows.length} 件；Unity 同名匯入 ${rows.filter(r => r.unity.length).length} 件；有資料配置或生成程式引用 ${rows.filter(r => r.direct.length || r.referenced.length).length} 件；空格位 ${gaps.length} 件。`, '',
  '## 素材組總覽', '',
  '| 素材組 | 作者／組別 | 來源 PR | 模型檔 | Unity 同名 | 配置或程式引用 |',
  '|---|---|---|---:|---:|---:|',
];
for (const [set, count] of [...counts].sort((a, b) => a[0].localeCompare(b[0]))) {
  const o = setup.get(set) ?? { owner: '待查', pr: '—' };
  lines.push(`| \`${set}\` | ${esc(o.owner)} | ${esc(o.pr)} | ${count.total} | ${count.imported} | ${count.placed} |`);
}
lines.push('', '## 逐件證據', '', '| 素材檔 | 作者／組別 | PR | 預定區塊 | Unity 模型 | 已配格位 | 狀態 |', '|---|---|---|---|---|---|---|');
for (const row of rows) {
  const slots = row.direct.map(p => `${p.block}:${p.id}`).join('、') || (row.referenced.length ? 'Editor 程式引用' : '—');
  lines.push(`| \`${row.exportPath}\` | ${esc(row.owner)} | ${esc(row.pr)} | ${esc(row.planned)} | ${row.unity.map(p => `\`${p}\``).join('、') || '—'} | ${esc(slots)} | ${row.state} |`);
}
lines.push('', '## 尚未接模型的區塊格位', '', '| 區塊 | 格位 | 物件／角色 | 負責 | 配置檔 |', '|---|---|---|---|---|');
for (const gap of gaps.sort((a, b) => (a.block + a.id).localeCompare(b.block + b.id))) {
  lines.push(`| ${gap.block} | \`${esc(gap.id)}\` | ${esc(gap.role)} | ${esc(gap.owner)} | \`${gap.file}\` |`);
}
lines.push('', '## 查核限制', '',
  '- 同名 Unity FBX 與輸出 FBX 只證明檔名相同；素材版本、渲染、碰撞與實際可達性須進 Unity 確認。',
  '- 生成程式可能在執行時條件式放置；程式引用不等於遊戲畫面已看見。',
  '- 本清冊逐一列出 FBX 與無對應 FBX 的 GLB，包含舊版與變體；數量不是可獨立擺放物件數。',
  '- 只有貼圖、JSON 或原始檔的素材組列於總覽，沒有模型檔可對位，須另外判定。', '');

const markdown = lines.join('\n');
if (process.argv.includes('--check')) {
  if (!existsSync(out) || read(out) !== markdown) { console.error('asset-placement.md is stale'); process.exit(1); }
  console.log(`asset-placement.md up to date (${rows.length} models, ${gaps.length} gaps)`);
} else {
  writeFileSync(out, markdown);
  console.log(`wrote ${norm(relative(root, out))} (${rows.length} models, ${gaps.length} gaps)`);
}
