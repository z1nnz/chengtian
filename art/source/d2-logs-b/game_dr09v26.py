# DR09 斷枝堆 v026（L 樣品）：以 v025 另存（v025 及以前全部保留）。大幅修整版：
#   比例：規格 L＝4.0 × 2.2 × 1.1 m，v025 長 4.15、寬 2.27 已超出；參考正面高寬比約 0.30，限高 1.1 m 下主體長約 3.65 m。
#     → 全部構件的平面位置等比收到 0.883（x）、0.93（y），高度依參考重新指定（不是非等比壓扁或拉高）；半徑 ×0.94。
#   主要形體（前景主幹 A、中央主拱 B、最高主枝 T1、右枝 T2、右下落地枝 R1）依參考正面特徵點（同寬換算）重新給控制點（NEW26）。
#   斷口、樹皮、苔、地衣、蘑菇、落葉見檔尾 v026 區段。
# DR09 斷枝堆 v025（L 樣品）：以 v024 另存（v024 及以前全部保留）。保留前景小拱洞、中央拱枝、蘑菇與材質；本輪只修兩處，其他物件與散布結果凍結（亂數種子不變）：
#   一、左端斷口：依參考正面外輪廓，裂片改成少數主要長裂片（沿木紋往左、上緣跟著主幹頂面、不往中心收）＋少量次要裂片；
#       主要長裂片外徑貼齊樹皮並埋入主幹，裸木與樹皮交接往右退；根部寬厚、末端薄碎，深度與長短不同。
#   二、右上最高主枝 T1：保留 v024 上抬方向；末段越近端部越陡（參考末段往上彎），端部改成不對稱的長撕裂口
#       （上側一長裂片往右上、外側帶樹皮、內側暖色裸木；其餘短齒），斜撕裂面，不是平切或規整尖錐；限高 1.1 m。
# DR09 斷枝堆 v024（L 樣品）：以 v023 另存（v023 及以前全部保留）。本輪只修三處形體，材質、蘑菇、中央主拱與其餘枝葉配置不動（亂數種子不變）：
#   一、前景主幹下的小拱洞：DR9PARTS=1 時把每個面的所屬構件寫進網格（own 屬性），逐件單獨顯示找出遮擋物件，再局部移動。
#   二、右上最高主枝 T1：末段明顯往右上抬升（根部粗壯、中段自然彎折），末端撕裂斷面＋暖色裸木。
#   三、左端斷口：保留主幹連接位置，裂片改成不等厚、帶扭曲的撕裂片，從主幹不同深度長出、長短錯落，以參考的整體破口輪廓為準。
# DR09 斷枝堆 v023（L 樣品）：以 v022 另存（v022 及以前全部保留）。只做有明確對照依據的修改：
#   一、中央空洞（v022 偏大、偏三角形）：既有中層粗枝 B3 改成由中央偏下往右上斜穿（在主拱 B 右腿後方、T1 下方），
#       把一個大三角洞分成前後遮擋、大小不同的空洞；主拱 B 的高度與主要曲線不動。
#   二、前景主幹下的小拱洞（參考寬度 0.55–0.90 m、高 0.02–0.16 m）：主拱左腳與 L2 起點移出該範圍（正面看穿過去不被擋）、主幹下緣在該處上收。
#   三、右上主枝 T1：加粗、少收細；折斷端改成不對稱撕裂分叉（兩長、三短的裂片），不用細纖維尖錐。受 1.1 m 限高，末端略降。
#   四、左端斷口局部重建：三片主要裂片沿木紋往左延長、變薄；主幹左端相應收短，斷口整體位置不變。
#   五、地衣：主幹前側由連續的一排斑片改成三塊醒目斑片，斑片內有樹皮孔洞穿插。
# DR09 斷枝堆 v022（L 樣品）：以 v021 另存（v021 及以前全部保留）。本輪以主要形體對齊為優先：
#   第一階段（灰模對照，align_dr09.py＋dr09_ref_features.json：參考與成品各裁到物件外框、等比同寬、底線對齊）依對照修改主枝：
#     前景主幹 A：隆起段放低（上緣 0.72→約 0.53 m），主幹下的空洞縮小到參考的低矮縫。
#     中央主拱 B：起拱點右移到寬度約 1.0 m（原 0.45 m，拱的左腳不再橫在 A 上方）、拱頂約 0.88 m 在 1.3–1.7 m、往右下落到約 2.85 m。
#     右上主枝 T1：從主拱後方較低處長出（左下端搭在 L3 上、中段被 B 壓住），往右上到 3.2 m 折斷端；上叉在 2.0 m、右側叉在 2.95 m。
#     右枝 T2：往右上翹到 3.65 m、0.8 m（原本幾乎水平）。右下落地枝 R1 落點往右；N1、N2、D、R2、N5 收短（打開右下貼地空洞）；
#     B3 中段放低（打開主拱右下的中右空洞）。
#   第二階段：左端斷口裂片改成根部厚、末端薄且不規則尖裂（2～3 個尖齒＋縱向劈裂）、輕微扭曲、各自小角度偏離，從主幹內部長出。
#   第三階段：前景厚苔毯延伸到斷口後方、加厚；地衣與裸木沿用 v021 的做法。
# DR09 斷枝堆 v021（L 樣品）：以 v020 另存（v020 及以前全部保留）。保留中央拱形、主要空洞與蘑菇配置；本輪：
#   一、左端斷口：移除圓錐狀尖刺與細纖維，裂片改成沿主幹木紋往左撕開的扁薄木片——截面不規則扁楔形（寬、薄、一側厚一側薄），
#       根部寬厚、末端寬度收到約 50%、厚度約 20%，末端是參差破碎的平口（不收成一點）；方向沿主幹，不外張不抬升；
#       少數長片構成輪廓，中短片在不同深度穿插；保留深裂縫、局部樹皮與暖黃裸木。
#   二、苔毯：A 頂面一塊主苔毯（連續）＋一小塊次苔；材質對苔層加遮罩銳化，邊緣破碎、逐漸消退。地衣：斑片半徑恢復並大小不一。
#   三、右上主枝：依同寬對照（參考右上主枝較直、較粗、到折斷端前不變細；上叉在寬度約 0.55 處、梢端分成 Y）——
#       T1 改成平順的上升弧、加粗、末端不收細；T1a 上叉移到 T1 前段、較陡、末端 Y 分叉；T2 加粗、少收細。
#       俯視：細枝 22→12，主枝附近的小分叉移除，讓粗枝交錯順序清楚。
# DR09 斷枝堆 v020（L 樣品）：以 v019 另存（v019 及以前全部保留）。保留蘑菇配置與拱下透空；本輪改大型形體，不加細枝：
#   一、左端斷口：改成立體裂塊（staves）——主幹截面的扇環沿主幹方向伸出，3 片主長片＋4 片中＋3 片短，起點深度、方位、粗細、長度各不同，
#       末段收薄、尖端偏一側；外側根部保留不規則樹皮；側面／內面深色裂縫權重（同為暖米黃裸木但有深淺）。原本的扇形薄片減為少量細纖維。
#   二、粗枝位置：依 feat_dr09.py（參考與成品正面剪影等比同寬、底部對齊）的差異修改——
#       T1 上叉移到 T1 前段（參考上叉在寬度 0.56 處）、T2 右叉降低；拱枝 B 拱頂往左 0.12 m（中央拱下空洞對齊參考）；
#       B2 放低（打開中央偏右的空洞）；右下 E、F2、M5、N5、R2 收短（打開右下貼地空洞）。總高仍守 1.1 m（不為高寬比加高）。
#   三、苔：前景主幹頂面連續苔毯，往兩側的範圍沿長度起伏（不是等寬綠帶）；墊狀厚度。
#   四、地衣：雜訊式地衣用中頻雜訊切成大小不一的斑、指定斑片半徑各異、內部破碎；不在頂面成白條。
# DR09 斷枝堆 v019（L 樣品）：以 v018 另存（v018 及以前全部保留）。保留 v018 的蘑菇配置與拱下透空；這輪只修三點：
#   一、左端斷口與樹皮交界：樹皮沿不同長度剝落（PEELW：每個方向的剝皮長度＝底長＋幾條長短不一的「舌」），交界不再是一圈整齊的環；
#       裸木裂縫加長、往主幹內部延伸；裂片改成三條方向不同的主長片＋中短碎片散在不同方位（不排成同一扇面）。
#   二、右上主枝：T1 改成「先升、平一段、再上挑」的折彎；T1a、T2b 改成明確往上的分叉（對齊參考正面的兩支上叉位置），
#       分叉與 T1c 梢端加撕裂斷端。細枝不增加。
#   三、苔與地衣：苔殼厚度加大低頻起伏（墊狀隆起 1–5 cm）；地衣改成指定位置的灰白扁平斑片（A 前側、拱枝 B／B3 側面），
#       邊緣不規則；原本雜訊式的零星白點減量。
# DR09 斷枝堆 v018（L 樣品）：以 v017 另存（v017 及以前全部保留）。保留 v017 的拱形、拱下空隙、枝端收尖；這輪修：
#   一、左前端斷口（最高優先）：改成「長斜撕裂面＋沿木紋往左延伸的纖維」。撕裂長邊在後下方（tear 0.60，撕裂面朝前左上方、正面與斜視看得到），斷面從底部往左拉長約 0.3 m，
#       纖維基部散佈在整個斜撕裂面上（不是同一中心放射），少數長片定方向（0.25–0.35 m）、中短碎片補層次；薄（厚約寬的 0.3–0.4）、
#       末端收薄破碎；裂縫三道切進木芯（深色）；殘留樹皮唇在後側。裸木換暖米黃偏淡赭（DR09_FreshWood_v018_Albedo）。
#   二、主幹 A、拱枝 B：節瘤／膨大加強、截面扁壓加強（沿生長方向連續，不加噪聲）。
#   三、右上 T1／T2：梢端改成不規則斷面＋撕裂纖維（兩根斜度、纖維數不同，不是同一種尖錐）；T2 中段加一個側向折彎。
#   四、苔：A 頂面兩塊主次分明的大苔塊（中間露樹皮）、拱枝兩肩、潮濕凹處；薄層幾何 1.4–4 cm 帶細小起伏；苔貼圖加低頻色差（橄欖、黃綠、暗綠）。
#       地衣：扁平、邊界清楚的灰白／灰綠斑（DR09_Lichen_v018_Albedo，法線改用樹皮法線＝順樹皮貼附）。
#   五、蘑菇：取消卡片小傘林，改成 A 頂面三朵實體主傘＋一朵小的（菌柄短、傘寬、暖赭棕傘面、淺色傘緣與菌柄，根部埋進木頭／苔裡）。
#   六、細枝 32→22、不高於 0.7 m；落葉更集中在木頭邊、懸空與斜面上的葉逐片以三維位置檢查刪除。
# DR09 斷枝堆 v017（L 樣品）：以 v016 另存（v016 及以前全部保留）。這輪只修形體與主要材質分區：
#   一、左端斷口：改成沿木紋撕裂的長纖維（50 條鋪滿斷面、順木紋大致平行、撕裂側長對側短、末端鈍而參差），不用厚板狀尖片；A 左端最後一段改水平，斷面朝左不再下垂；
#       裸木換暖米黃（DR09_FreshWood_v017_Albedo，tex_dr09v17.py 產生），裂縫記在頂點上、用 Inner 層保留深色。
#   二、前景主幹 A：維持拱形，隆起段軸心再抬 3–4 cm，並把隆起段的下緣往上收（UND，只收下半圈、不整體縮細），拱下空隙變大。
#   三、右上主要枝 T1／T2：控制點改成連續彎曲、梢端漸細（tp 0.64），各加一根不對稱的外張分叉；梢端改長斜撕裂＋細纖維，不再是平截圓木端。
#   四、苔：A 頂面成厚苔區（薄層幾何 1–3 cm、順著表面起伏、邊緣收薄破碎），拱頂次之；地衣改成側面與頂面可辨識的灰白斑（不在苔上）。
#   五、蘑菇：前景主菌蓋放大，兩張十字卡轉 45°，正面與斜 45° 都看得到菌傘。
#   六、落葉卡：逐片檢查中心下方 2.5 cm 內有沒有木頭或地面，沒有依附的刪掉；細枝 55→32、不長到 0.8 m 以上（不擋主輪廓）。
# DR09 斷枝堆 v016（L 樣品）：以 v015 另存，保留枝量、主要堆疊、斷口去刺束、中後方粗枝上伸（v015 及以前全部保留）。只精修三部位＋苔：
#   一、前側粗木 A：左段到中段明顯隆起（軸心 .24→.40→.13）、粗細不對稱（knots 有正有負）、截面扭轉加大；
#       墊木 C2 移到 x≈-0.9 加粗，A 底下形成左高右低、兩段不等的低矮空隙（不是單一規整拱）。
#   二、中央拱枝 B：控制點曲率不均（陡升→平頂→折下）、粗細起伏、偏心截面加大；新增根部外張的側分枝 Bc（crotch 連續過渡）。
#   三、左端斷口：木芯＋三塊長裂片＋一塊短片，各自繞木紋軸轉不同角度（rot，不再平行疊板）、埋入深度不同（emb），
#       兩道順紋深裂縫切進同一塊木芯（cracks），樹皮邊局部保留。
#   苔：只在 A 頂面與拱枝 B 頂部成主要覆蓋區（依離軸線距離限定），邊緣破碎；斷口 0.6 m 內不長苔；薄層幾何沿用 v005 finish_body。
# DR09 斷枝堆 v015（L 樣品）：以 v014 為基礎另存，保留拱枝連續彎曲與蘑菇；不做全面重排，只修三項（v014 及以前全部保留）：
#   一、A 左端斷口：移除刺束狀細長裂片；改為斜向撕裂面（cap tilt）＋寬厚殘留木芯＋五塊長短寬窄厚薄不同的寬裂片（splinter slab 模式：
#       基部從斷面內部接入木芯、前段保持寬厚、只有末段收尖），只在撕裂那一側，上緣保留樹皮邊與對側缺角。
#   二、前側主幹 A：abs 設計軸心——左端低、在蘑菇處局部隆起、往右下沉，截面扭轉（twr／twk）與局部扁鼓（ek），底部留不規則空隙。
#   三、中後層主斜枝：T1（粗 20 cm）從中央後方 B2 上斜伸到右上主峰（約 x 1.0）、T2 往右上到第二峰（約 x 1.6）；B2／B3 放低讓 T1 通過。
#   總高 ≤ 1.1 m：V['H'] = 1.00（分叉 ≤ 1.05、細枝 ≤ 1.08），實測見 previews/v015/*_measure.json。
# DR09 斷枝堆 v014（L 樣品）：以 v013 為基礎另存，保留 v013 的整體交疊結構（v013 及以前全部保留）。
# v014 修正：一、高度限制在 1.1 m 內（LOD0 木質網格實測，見 previews/v014/*_measure.json）；
#   二、中央拱下洞口（B 改成兩腳落地的全拱）與前側低洞（A 左段架在 C2／C 上，後方 G／L2／L3／N8 右移讓出視線）；
#   三、A 左端斷口改為順木紋、長短錯落、往外散開的不規則薄片木刺＋較厚木芯（splinter 重寫為 6 點截面、多段、扭轉、鋸齒收尖）；
#   四、中層枝加彎度與局部分叉（B3／R1／R2／M6／N2 bow、R2b／M6b／R1c）；五、蘑菇改為每叢 2–3 張卡、主菌蓋放大。
#   每根枝依名稱各自重設亂數，改一根不會牽動其他根。
# 以下為 v013 原說明：
# DR09 斷枝堆 v013（L 樣品）：整體重構。原始參考（三視圖 L 列、情境圖、近景圖）為主，v012 只當工具來源（v012 及以前全部保留）。
# 不再沿用 v006–v012 的擺法；以參考圖可辨識的構件重新排：
#   底層：C（A 下面的支撐木，A 左段因此離地留一道縫）、後方倒木 G／D、右前低木 E、外圍中細枝（前 F1／F2、後 L1／L2）。
#   前側主木 A：最粗（直徑約 33 cm）、左端大撕裂斷口朝左前、上面成片的苔與一叢蘑菇。
#   拱形枝 B／B2／B3：本身彎曲的枝，從後左跨過 A 上方再落到右前／右側，正面看是一層層的拱，拱下透空。
#   斜挑枝 T1／T2：從堆中段往右後上方斜挑，梢端是撕裂斷口（T1 為最高點，約 1.2 m）。
#   往右下落地的枝 R1／R2、M5／M6，斜跨的中型枝 X2，左後填量 L3，中下層補量 N1–N7，俯視左後／右後補量 N8／N9。
#   材質：苔集中在粗木頂面、成片但邊緣破碎（重定義 finish_body_base 的門檻）；蘑菇在 A 左段頂面兩叢、尺寸放大（重定義 make_cards）。
# 擺放：每根用 3D 控制點（x, y, 彎曲高度）描述自己的彎曲；整根剛體落下到第一個支點，再繞它朝重心那側倒到第二個支點
#  （保留枝本身的弧度，不是被地形捏成波浪）；最後只做局部抬升避開穿插。
# 用法：
#   blender -b --python art/source/d2-logs-b/game_dr09v18.py -- L 1   （灰模：blend/…_v018_greybox.blend）
#   blender -b --python art/source/d2-logs-b/game_dr09v18.py -- L 2   （完整：匯出 FBX／GLB、存 blend/…_v018.blend）
import sys, os, math, types, random, traceback, json, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
H5 = {'__name__': 'dr09_v5_for_v26', '__file__': HERE + '/game_dr09v5.py'}
exec(compile(open(H5['__file__'], encoding='utf-8').read(), H5['__file__'], 'exec'), H5)
ns = H5['ns']
ns['VER'] = 'v026'
ns['VARIANTS']['L'].update(twigs=12, litter=8, seed=91313, L=3.65, W=2.05, margin=.36)   # v026：規格內（4.0 × 2.2 × 1.1）
LAYOUT = json.loads(os.environ.get('DR9LAYOUT', '{}'))       # 迭代用：覆寫個別構件的參數（不改程式）
# v014：中層最像直棍的幾根（B3、R1、R2、M6、N2）給明確、各不相同的弓彎與 S 彎（不套同一種圓弧），環境變數可再覆寫
for _k, _bw in (('B3', (.09, .0)), ('R1', (.12, -.05)), ('R2', (-.11, .04)), ('M6', (-.12, .06)), ('N2', (.10, -.04))):
    LAYOUT.setdefault(_k, {}).setdefault('bow', _bw)


def CAPC(rec):
    return rec.get('capc', .16 if rec.get('heavy') else .50)


def smooth_r(r, n=15):
    k = np.hanning(n)
    k /= k.sum()
    return np.convolve(np.pad(r, n // 2, mode='edge'), k, 'valid')


def XS(rec, s, th):
    x = rec.get('xs')
    if not x:
        return 1.0
    ph = th - x['tw0'] - x['twr'] * s
    for c, a, w in x.get('twk', ()):
        ph -= a / (1 + math.exp(-(s - c) / w))
    e = x['e']
    for c, a, w in x.get('ek', ()):
        e *= 1 + a * math.exp(-((s - c) / w) ** 2)
    return 1 - e * (1 - math.cos(2 * ph)) - x['h3'] * .5 * (1 - math.cos(3 * ph + x['p3']))


def plan(v):
    global V, SEG, OWN, RECS, CONTACTS
    assert v == 'L', 'v026 先做 L 樣品'
    V = dict(VARIANTS[v], v=v)
    V['H'] = 1.00          # v015：分叉頂端上限 H×1.05、細枝 H×1.08（總高 1.1 m 內）
    SEG, OWN, RECS, CONTACTS = np.zeros((0, 8)), np.zeros(0, int), [], []
    R = random.Random(V['seed'])
    NAMED = {}

    def end_caps(rec, e_list):
        for e in e_list:
            tc = rec['tear'][e]
            rr = float(rec['r'][0 if e == 0 else -1])
            kind_ = R.choice(('notch', 'fiber', 'slant', 'fiber'))
            rec['cap'][e] = dict(tilt=U(R, .25, .55), notch=tc + math.pi * U(R, .6, 1.1), nw=U(R, .6, 1.0) if kind_ != 'slant' else .2,
                                 tooth=U(R, .3, .6), lip=tc - math.pi * U(R, .4, .7), lw=U(R, .4, .6), lipl=U(R, .15, .30))
            n = {'notch': 1, 'fiber': 3, 'slant': 0}[kind_]
            rec['splint'][e] = [dict(th=tc + U(R, -.7, .7), len=rr * U(R, 1.0, 2.6), w=max(.012, rr * U(R, .30, .48)),
                                     out=U(R, 0, .06), tk=U(R, .50, .65)) for _ in range(n)]

    def zpath(ctrl3):
        C3 = np.array(ctrl3, float)
        Q, s = spline_path(C3[:, :2].tolist())
        idx = [int(np.argmin(np.linalg.norm(Q - c[:2], axis=1))) for c in C3]
        sc = np.array([s[i] for i in idx], float)
        sc[0], sc[-1] = 0.0, float(s[-1])
        sc = np.maximum.accumulate(sc)
        z = np.interp(s, sc, C3[:, 2])
        k = max(5, int(.30 / STEP)) | 1
        w = np.hanning(k)
        w /= w.sum()
        z = np.convolve(np.pad(z, k // 2, mode='edge'), w, 'valid')
        return Q, s, z

    def rest3(Q, s, r, zs, mode, sink, excl, maxtilt=.9):
        thin = {x['id'] for x in RECS if x['kind'] in ('twig', 'litter')}
        g = r * (1 - sink)
        sup = np.maximum(g, support(Q, r, set(excl) | thin))
        if mode == 'abs':
            z = zs.copy()
        elif mode == 'never':
            z = zs
        elif mode == 'shift':
            # 盡量保留設計：z = 設計 + a + b·s，(a, b) 取（支撐 − 設計）上凸包的某一段（兩點搭靠），
            # 在各段裡挑「和設計差最少」的；重心不在兩個支點之間的加罰（會翻倒）。
            h = sup - zs
            hull = upper_hull(list(s), list(h))
            w = r ** 2
            sc = float((w * s).sum() / w.sum())
            best_, bk = None, None
            cand = list(zip(hull, hull[1:])) + [(p_, p_) for p_ in hull]
            for (x0, y0), (x1, y1) in cand:
                if x1 - x0 > 1e-6:
                    b_ = (y1 - y0) / (x1 - x0)
                    a_ = y0 - b_ * x0
                    stable = x0 - .05 <= sc <= x1 + .05
                else:                                # 只有一個支點：平移（設計斜率）
                    b_, a_ = 0.0, y0 - 0 * x0
                    stable = False
                if abs(b_) > maxtilt:
                    continue
                z_ = zs + a_ + b_ * s
                if (z_ < sup - 1e-4).any():
                    continue
                key = float(np.abs(a_ + b_ * s).mean()) + (0 if stable else .15)
                if bk is None or key < bk:
                    best_, bk = z_, key
            z = best_ if best_ is not None else zs + float(h.max())
        else:
            # 剛體靜置：枝本身的彎（zs 去掉線性部分）不變；在（支撐 − 彎）的上凸包上取重心所在那一段，
            # 等於兩個支點夾住重心、重心最低的擺法（不會因為壓到某個高點就整根被抬高）。
            A_ = np.c_[s, np.ones_like(s)]
            shape = zs - A_ @ np.linalg.lstsq(A_, zs, rcond=None)[0]
            hull = upper_hull(list(s), list(sup - shape))
            w = r ** 2
            sc = float((w * s).sum() / w.sum())
            seg = (*hull[0], *hull[-1])
            for (x0, y0), (x1, y1) in zip(hull, hull[1:]):
                if x0 - 1e-9 <= sc <= x1 + 1e-9:
                    seg = (x0, y0, x1, y1)
            x0, y0, x1, y1 = seg
            slope = (y1 - y0) / max(x1 - x0, 1e-6)
            z = y0 + float(np.clip(slope, -maxtilt, maxtilt)) * (s - x0) + shape
            z = z + max(0.0, float((sup - z).max()))
            z = np.maximum(z, g)
        P = np.c_[Q, z]
        for _ in range(40):
            cc = clearance(P, r, set(excl))
            if cc.min() > -.002:
                break
            if os.environ.get('DR9DBG'):
                _i = int(cc.argmin()); _a, _b = SEG[:, :3], SEG[:, 3:6]; _ab = _b - _a
                _u = np.clip(((P[_i] - _a) * _ab).sum(1) / ((_ab ** 2).sum(1) + 1e-12), 0, 1)
                _dd = np.linalg.norm(P[_i] - (_a + _u[:, None] * _ab), axis=1) - r[_i] - (SEG[:, 6] + (SEG[:, 7] - SEG[:, 6]) * _u)
                _o = RECS[int(OWN[int(_dd.argmin())])]
                print('    LIFTBY', _o.get('name') or f"{_o['kind']}{_o['id']}", np.round(P[_i], 2).tolist(), round(float(cc.min()), 3))
            up = np.maximum(-cc + .003, 0)
            kk = 15                                                         # v026：避讓抬升不過衝（原 21 點 ×2.2 會把整段連帶抬高、再撞上更上層的枝）
            P[:, 2] += np.convolve(np.pad(up, kk // 2, mode='edge'), np.hanning(kk) / np.hanning(kk).sum(), 'valid') * 1.3
        cc = clearance(P, r, set(excl))
        tch = ((P[:, 2] - g) < .012) | (cc < .012)
        runs = int(np.sum(np.diff(np.r_[0, tch.astype(int)]) == 1))
        # 接觸點分別落在哪幾根上（地面 = ground），方便調整設計高度
        who = []
        for i in np.nonzero(tch)[0][::4]:
            if P[i, 2] - g[i] < .012:
                nm = 'ground'
            else:
                d_ = np.linalg.norm(SEG[:, None, :3] * 0 + 0, axis=2) if False else None
                a_, b_ = SEG[:, :3], SEG[:, 3:6]
                ab = b_ - a_
                u = np.clip(((P[i] - a_) * ab).sum(1) / ((ab ** 2).sum(1) + 1e-12), 0, 1)
                dd = np.linalg.norm(P[i] - (a_ + u[:, None] * ab), axis=1) - r[i] - (SEG[:, 6] + (SEG[:, 7] - SEG[:, 6]) * u)
                o = RECS[int(OWN[int(dd.argmin())])]
                nm = o.get('name') or f"{o['kind']}{o['id']}"
            if not who or who[-1][0] != nm:
                who.append((nm, round(float(s[i]), 2)))
        print('    REST_ON', who)
        return P, runs

    def log(name, ctrl3, r0, tp=.50, mode='rest', sink=.10, knots=(), lumps=2, e=(.10, .16), ends=('break', 'break'),
            excl=(), main=False, splint=()):
        R.seed(V['seed'] * 7919 + zlib.crc32(name.encode()))
        o = LAYOUT.get(name, {})
        ctrl3 = o.get('c', ctrl3)
        r0, mode, tp = o.get('r0', r0), o.get('mode', mode), o.get('tp', tp)
        if name in NEW26:                                                   # v026：依參考重新設計的主要形體（新座標）
            ctrl3, r0, tp = NEW26[name]['c'], NEW26[name].get('r0', r0 * SR26), NEW26[name].get('tp', tp)
            knots, mode = NEW26[name].get('knots', knots), NEW26[name].get('mode', mode)
        else:                                                               # 其餘：平面等比收、高度依參考比例
            ctrl3 = [(x * SX26, y * SY26, z * SZ26) for x, y, z in ctrl3]
            r0 = r0 * SR26
        Q, s, zs = zpath(ctrl3)
        t = s / s[-1]
        Lc = float(s[-1])
        bw = o.get('bow', (U(R, .06, .13) * R.choice((-1, 1)) * min(1.0, Lc / 1.6), U(R, -.045, .045) * min(1.0, Lc / 1.6)))
        dch = Q[-1] - Q[0]
        nrm = np.array((-dch[1], dch[0])) / (np.linalg.norm(dch) + 1e-9)
        Q = Q + nrm[None] * (bw[0] * np.sin(math.pi * t) + bw[1] * np.sin(2 * math.pi * t))[:, None]      # 側向弓彎＋S 彎
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
        t = s / s[-1]
        if mode == 'rest':
            zs = zs + U(R, .0, .05) * np.sin(math.pi * t) ** 1.5                                         # 貼地木略拱，下面留縫
        lump = heavy_radius(R, s, 1.0, 0, lumps)
        r = r0 * (1 - tp * t ** .85) * (1 + .16 * np.exp(-t / .05)) * lump
        for c, a in knots:
            r = r * (1 + a * np.exp(-((t - c) / .06) ** 2))
        r = smooth_r(r, 9)
        P, runs = rest3(Q, s, r, zs, mode, sink, excl)
        rec = new_rec(R, 'branch', P, s, r, ends, main=main)
        rec['name'] = name
        L = float(s[-1])
        rec['xs'] = xs_params(R, e)
        rec['xs']['h3'] = U(R, .05, .09)
        rec['xs']['twr'] = U(R, .06, .18) * R.choice((-1, 1))
        rec['xs']['twk'] = [(U(R, .2, .8) * L, U(R, .5, .9) * R.choice((-1, 1)), .10) for _ in range(R.randint(1, 2))]
        rec['xs']['ek'] = [(U(R, .2, .8) * L, U(R, -.4, .5), .25)]
        rec['ext'] = [1.0, 1.0]
        rec['heavy'] = r0 > .06
        cap_params(R, rec)
        end_caps(rec, [k for k in (0, 1) if ends[k] == 'break'])
        for e_, n_, l_ in splint:
            heavy_splinters(R, rec, e_, n_, l_)
        add_seg(rec)
        NAMED[name] = rec
        top = P[:, 2] + r
        print('  LOG', name, 'd_cm', round(r0 * 200, 1), 'len', round(L, 2), 'ends', round(float(P[0, 2] - r[0]), 2),
              round(float(P[-1, 2] - r[-1]), 2), 'top', round(float(top.max()), 2), 'at_x', round(float(P[int(top.argmax()), 0]), 2), 'contact_runs', runs)
        return rec

    def crotch(rec, t, side, fl, up, frac, swing=(.55, .80), wob=.10, name='', tip='break', flare=.72):
        P, s, r = rec['P'], rec['s'], rec['r']
        fl = fl * SX26                                                      # v026：分叉長度跟著等比收
        i = int(len(P) * t)
        T, N0, B0 = frame_at(P, i)
        rp = float(r[i])
        a = math.atan2(T[1], T[0]) + side * U(R, *swing)
        d1 = np.array((math.cos(a), math.sin(a), T[2] * .45 + up))
        d1 /= np.linalg.norm(d1)
        n = max(8, int(fl / STEP))
        sf = np.linspace(0, fl, n + 1)
        L0 = min(rp * 3.2, fl * .45)
        w = np.clip(sf / L0, 0, 1)
        w = w * w * (3 - 2 * w)
        Pf = [P[i].copy()]
        for k in range(1, n + 1):
            d = (1 - w[k]) * T + w[k] * d1
            d /= np.linalg.norm(d)
            Pf.append(Pf[-1] + d * (sf[k] - sf[k - 1]))
        Pf = np.array(Pf)
        lat = np.cross(d1, (0, 0, 1.0))
        lat /= np.linalg.norm(lat) + 1e-9
        Pf += lat[None] * (np.sin(sf / fl * math.pi * U(R, .9, 1.4)) * fl * U(R, -wob, wob) * w)[:, None]
        tf = sf / fl
        rf = rp * frac * (1 - .58 * tf ** .9) + .002
        rf = rf * (1 + (min(flare, frac * 1.55) / frac - 1) * np.exp(-sf / (rp * 1.3)))
        Pf = bend_up(Pf, rf, {rec['id']})
        cmin = float(clearance(Pf, rf, {rec['id']}).min())
        if cmin < .002 or (Pf[:, 2] + rf).max() > V['H'] * 1.05 or not inside(Pf, .1) or (Pf[:, 2] - rf).min() < -.01:
            print('  CROTCH_FAIL', name, round(cmin, 3), round(float((Pf[:, 2] + rf).max()), 2), inside(Pf, .1))
            return None
        f = new_rec(R, 'fork', Pf, sf, rf, ('open', tip), parent=rec['id'])
        f['name'] = name
        f['xs'] = xs_params(R, (.08, .14))
        f['ext'] = [1.0, 1.0]
        f['heavy'] = float(rf[0]) > .05
        if tip == 'break':
            cap_params(R, f)
            end_caps(f, (1,))
        rec['bulge'].append((float(s[i]) + L0 * .35, .14))
        add_seg(f)
        return f

    def fork_any(key, rec, ts, side, fl, up, frac, big=True, **k):
        R.seed(V['seed'] * 7919 + zlib.crc32(key.encode()))
        for t_ in ts:
            for sd in (side, -side):
                f = crotch(rec, t_, sd, fl, up, frac, name=key, **k) if big else add_fork(R, rec, t_, sd, fl, up, (frac * .9, frac * 1.1))
                if f is not None:
                    if not big:
                        f['name'] = key
                        if R.random() < .6:
                            f['ends'][1] = 'break'
                    return f
        print('  FORK_MISSING', key)
        return None

    # ------------------------------------------------------------------ 底層（先擺，後面的木頭搭在上面）
    # 高度欄是設計的軸心高度（依參考正面圖量的），擺放時整根上下平移到剛好接觸；只有一處接觸才會繞支點傾倒。
    C = log('C', [(-.70, .36, 0), (-.64, .00, 0), (-.58, -.40, 0), (-.51, -.78, 0)], .040, .35, sink=.30, lumps=2, e=(.06, .12))
    C2 = log('C2', [(-1.02, -.06, 0), (-.96, -.34, 0), (-.90, -.62, 0), (-.84, -.88, 0)], .070, .30, sink=.26, lumps=2, e=(.10, .16))   # v016：A 中段下的粗墊木（A 底下分成兩段不等的低空隙）
    G = log('G', [(-.95, .62, 0), (-.58, .70, .03), (-.22, .76, 0)], .090, .35, sink=.18, lumps=2)   # v022：讓開 B3 起點
    D = log('D', [(.40, .86, 0), (.90, .76, .03), (1.42, .64, 0)], .085, .40, sink=.16, lumps=2)   # v022：起點右移（讓開 B3 起點）
    E = log('E', [(.45, -.80, 0), (.90, -.70, .02), (1.38, -.56, 0)], .065, .45, sink=.12)   # v020：收短（右下貼地空洞）
    L1 = log('L1', [(-.45, .40, 0), (-.20, .50, .04), (.05, .56, .02)], .045, .55, e=(.05, .10))
    L2 = log('L2', [(-1.08, .95, 0), (-.70, .99, .03), (-.30, .99, 0)], .042, .55, e=(.05, .10))   # v023：讓出主幹下的拱洞   # v022：讓開 B3 起點
    F1 = log('F1', [(-1.00, -.93, 0), (-.55, -.85, .03), (-.15, -.82, .02), (.12, -.88, 0)], .048, .55, e=(.05, .10))
    F2 = log('F2', [(.70, -.99, 0), (1.05, -.94, .02), (1.40, -.88, 0)], .040, .55, e=(.05, .10))
    # ------------------------------------------------------------------ 前側主木 A（最粗，左端大斷口朝左前；左段搭在 C 上離地，下面一道縫）
    A = log('A', [(-1.68, -.50, .235), (-1.58, -.47, .26), (-1.46, -.44, .30), (-1.28, -.40, .35), (-1.10, -.36, .36), (-.86, -.30, .33), (-.55, -.23, .24), (-.20, -.15, .18), (.25, -.03, .13), (.85, .12, .09)],   # v022：隆起段放低（同寬對照：上緣約 0.53 m）
            .165, .42, sink=.20, knots=((.10, .13), (.24, .15), (.37, -.09), (.52, .10), (.68, -.08), (.84, .05)), lumps=3, e=(.14, .20), main=True, mode='abs')   # v016：左段到中段隆起、粗細不對稱
    A['xs']['twr'] = .28                                                   # 截面扭轉加大
    A['xs']['twk'] = [(.49, 1.1, .10), (1.06, -.9, .12), (1.63, .6, .14)]
    A['xs']['ek'] = [(.40, .55, .20), (.93, -.30, .20), (1.41, .45, .22), (1.99, .35, .27)]  # 扁、鼓交替，底緣不規則（v018 右段再壓扁）
    A['und'] = UND26   # v024：負值＝下緣往下長（拱洞右腳）   # v023：主幹下小拱洞處下緣上收                      # v022：主幹下低矮縫（參考 0.55–0.90 m）                      # v017：隆起段下緣往上收（s 中心、寬、收的比例），上緣不動
    # v018：左前端斷口＝長斜撕裂面（長邊在前下方、往左拉長）＋沿木紋往左的纖維（基部散在整個撕裂面上，不是同一中心放射）
    A['peel'][0] = 1.9
    torn_end19(A, 0, .60, .15, (), 0, 0, 92020, Ls=(.20, .30), Lm=(.07, .12), Lsh=(.03, .06), W=(.032, .050), lift=(-.03, .10))   # v020：斷面幾乎不斜（不再是外凸的扇形面），只留少量細纖維；輪廓由裂塊決定
    A['capce'][0], A['capj'][0] = -.30, .14                               # v021：斷面中央往內凹（深裂、不是圓頭），中間點前後錯開
    A['staves'] = {0: STAVES_A}                                            # v020：立體裂塊
    A['jag'] = {0: dict(base=.22, tongues=[(.60, 2.9, .30), (.60 + 1.45, 1.6, .22), (.60 - 1.20, 2.2, .20), (.60 + 2.70, .9, .28), (.60 - 2.35, 1.3, .18), (.60 + .75, .6, .15)])}   # v019：剝皮長度（倍 r0）
    # 中下層補量（參考圖正面下半部是實的、俯視也很密）
    N1 = log('N1', [(.20, -.55, .10), (.55, -.40, .14), (.85, -.26, .10), (1.05, -.19, .03)], .045, .55)
    N2 = log('N2', [(.45, .35, .10), (.75, .28, .14), (1.05, .20, .12), (1.35, .12, .04)], .042, .55)
    N3 = log('N3', [(-.20, .26, .04), (.10, .36, .10), (.40, .44, .12), (.70, .52, .08), (.98, .60, .03)], .048, .55)
    N4 = log('N4', [(.50, .97, .03), (.80, .92, .10), (1.10, .86, .04)], .045, .55)   # v022：移到後方 D 上（讓開 B3）
    N5 = log('N5', [(1.20, .40, .25), (1.33, .27, .18), (1.45, .14, .10)], .040, .60)
    N6 = log('N6', [(.15, -.98, .02), (.45, -.92, .08), (.75, -.86, .04)], .040, .55)
    N7 = log('N7', [(-.75, .70, .06), (-.45, .66, .12), (-.18, .62, .06)], .045, .55)   # v022：收短（讓開 B3）
    L3 = log('L3', [(-.85, .30, .05), (-.65, .42, .10), (-.45, .54, .08)], .052, .55, e=(.05, .11))
    X2 = log('X2', [(-.70, 1.00, .03), (-.62, .82, .10), (-.52, .66, .05)], .055, .55)   # v022：讓開 B3 起點
    # ------------------------------------------------------------------ 拱形枝（本身彎，跨過 A 上方，拱下透空）
    B2 = log('B2', [(-.32, .03, .42), (-.12, .08, .32), (.08, .13, .18), (.26, .16, .08), (.40, .17, .03)],   # v022：提早落地（B3 不再被墊高，打開中右空洞）
             .080, .50, knots=((.45, .05),), e=(.10, .15), mode='abs')
    B = log('B', [(-1.06, .15, .07), (-1.02, .11, .27), (-.97, .06, .48), (-.88, .02, .67), (-.72, -.02, .81), (-.50, -.05, .84), (-.25, -.06, .80), (-.02, -.10, .71),
                  (.22, -.20, .65), (.46, -.28, .50), (.70, -.31, .31), (.90, -.33, .15), (1.04, -.33, .05)], .100, .68,   # v022：主拱右腿較緩、落點右移到寬度約 3.15 m   # v022：起拱點右移到寬度 1.0 m、拱頂 1.3–1.7 m
            knots=((.12, .10), (.20, .13), (.34, -.10), (.48, .09), (.62, -.05), (.72, -.08), (.82, .08)), lumps=3, e=(.17, .23), splint=(), mode='abs')   # v016：陡升→平頂→折下、粗細起伏
    B3 = log('B3', [(-.40, .30, .12), (-.14, .24, .24), (.12, .14, .37), (.30, .02, .48), (.46, -.13, .55), (.60, -.28, .56)],   # v023：中央偏下往右上斜穿，上端搭在主拱右腿上
             .090, .52, knots=((.30, .06), (.55, .05)), e=(.10, .16), mode='abs')   # v022：B3 照設計高度（不被 N1 抬高）
    B['xs']['twr'] = -.22
    B['xs']['twk'] = [(.8, -1.0, .12), (1.75, .8, .12)]
    B['xs']['ek'] = [(.6, .45, .22), (1.4, -.30, .20), (2.0, .40, .22)]    # 偏心截面（扁、鼓交替）
    # ------------------------------------------------------------------ 右側往下落地、斜跨
    R1 = log('R1', [(1.06, .06, .57), (1.36, .01, .43), (1.68, -.04, .24), (2.00, -.08, .03)], .072, .60, knots=((.45, .06),), mode='abs')
    R2 = log('R2', [(1.00, .62, .32), (1.18, .55, .22), (1.36, .47, .10), (1.50, .40, .02)], .066, .60, knots=((.40, .06),))
    M5 = log('M5', [(.70, -.40, .36), (.95, -.47, .30), (1.20, -.55, .18), (1.45, -.62, .05)], .060, .55, mode='shift')
    M6 = log('M6', [(.30, .95, .05), (.70, .80, .30), (1.10, .70, .40), (1.32, .64, .22), (1.48, .60, .05)], .068, .55, knots=((.50, .06),))
    # ------------------------------------------------------------------ 斜挑枝（最高點），梢端撕裂斷口
    T1 = log('T1', [(-.98, .40, .17), (-.80, .37, .27), (-.52, .30, .41), (-.27, .17, .56), (-.05, .08, .68), (.20, .14, .72), (.45, .20, .745), (.63, .25, .785), (.77, .27, .835), (.87, .27, .88), (.94, .27, .92)], .125, .30,   # v022：左下端搭 L3、中段被主拱 B 壓住
             knots=((.30, .05), (.62, -.04)), e=(.10, .15), mode='abs')        # v021：平順上升弧、加粗、到折斷端前不變細        # v017：先陡後緩的連續彎、側向 S 彎、漸細
    T2 = log('T2', [(.48, -.06, .335), (.76, -.06, .45), (1.04, .03, .60), (1.24, -.01, .67), (1.40, -.05, .72), (1.56, .00, .78)], .078, .70, knots=((.30, .05), (.62, -.04)), mode='abs')   # v017：拱起再略垂、漸細
    # v018：兩根粗枝的折斷端各不相同：T1 斜撕裂＋8 條纖維、T2 較平的參差斷面＋5 條短纖維（不是同一種尖錐）
    T1['staves'] = {1: STAVES_T1}                                          # v023：不對稱撕裂分叉
    torn_end(T1, 1, T1['tear'][1], .45, 0, 0, 0, 8801, Ls=(.10, .16), Lm=(.05, .09), Lsh=(.02, .05), W=(.014, .026), lift=(.0, .10))
    T1['capce'][1], T1['capj'][1] = -.10, .20                            # v024：T1 斷面內凹撕裂、不是斜削尖頭
    torn_end(T2, 1, T2['tear'][1], .28, 1, 2, 2, 8802, Ls=(.07, .11), Lm=(.04, .07), Lsh=(.02, .04), W=(.012, .022), lift=(.0, .08))
    # 俯視 X 形交叉：左後→右前、右後→左前兩根中型彎枝，跨在中層上（補俯視空白、中層體積）
    N8 = log('N8', [(-.98, .98, .02), (-.80, .82, .06), (-.62, .66, .10)], .055, .55, mode='rest')
    N9 = log('N9', [(1.62, .92, .05), (1.38, .80, .15), (1.15, .62, .22), (.95, .50, .20)], .052, .55, mode='rest')
    # ------------------------------------------------------------------ 分叉（大的用連續外張的 crotch，小的用 add_fork）
    fork_any('Aa', A, (.58, .52, .64), 1, .70, .22, .45, swing=(.50, .75))
    fork_any('Ba', B, (.70, .64, .76), -1, .45, -.08, .50)
    fork_any('Bc', B, (.42, .38, .48), 1, .42, .02, .52, swing=(.55, .80), flare=.80)   # v016：拱頂往後的自然側分枝，根部外張連續過渡
    fork_any('B2a', B2, (.55, .48, .62), 1, .50, -.04, .50)
    fork_any('B3a', B3, (.45, .40, .52), -1, .45, -.02, .50)
    T1a_ = fork_any('T1a', T1, (.30, .34, .27, .38), -1, .42, 1.15, .66, swing=(.10, .25), flare=.82, wob=.12)   # v021：上叉移到 T1 前段、較陡   # v019：明確往上的分叉（參考正面中段上叉）   # v014：往上翹得少一點（總高 1.1 m 內）
    T1c_ = fork_any('T1c', T1, (.72, .68, .76, .64, .80), 1, .24, .30, .55, swing=(.30, .50), flare=.82)   # v017：梢端前的不對稱分叉（短、粗、外張）
    T2b_ = fork_any('T2b', T2, (.55, .50, .60, .64), -1, .44, .35, .64, swing=(.18, .36), flare=.80, wob=.22)   # v019：右側往上彎的分叉     # v017
    fork_any('T1b', T1, (.86, .82, .90), 1, .32, -.10, .50)                  # v021：主枝中段往右的側叉（粗、短）
    if T1a_ is not None:                                                    # v021：上叉梢端 Y 分叉（參考上叉末端分兩支）
        fork_any('T1aa', T1a_, (.62, .58, .68), 1, .20, .10, .60, big=False)
    for _f, _sd, _tl in ((T1a_, 9101, .55), (T1c_, 9102, .40), (T2b_, 9103, .65)):   # v019：上叉梢端撕裂（每根斜度不同）
        if _f is not None:
            _f['ends'][1] = 'break'
            torn_end(_f, 1, _f['tear'][1], _tl, 1, 2, 2, _sd, Ls=(.06, .10), Lm=(.03, .06), Lsh=(.015, .03), W=(.010, .018), lift=(.0, .08))

    fork_any('R1a', R1, (.45, .40, .52), -1, .40, -.06, .50)
    fork_any('R2b', R2, (.35, .30, .42), -1, .40, .12, .50)                  # v014：中層補外張分叉
    fork_any('M6b', M6, (.42, .36, .50), 1, .42, .10, .50)
    fork_any('R1c', R1, (.30, .25, .36), 1, .36, .10, .48)
    for nm_, rec_ in (('Ea', E), ('F1a', F1), ('F2a', F2), ('Da', D), ('Ga', G), ('L3a', L3), ('N4a', N4), ('N6a', N6), ('M5a', M5), ('N1a', N1)):   # v021：中層小分叉移除（俯視遮住粗枝交錯）   # v017：N5a、N9a（右上碎枝）不長
        fork_any(nm_, rec_, (.60, .50, .70), R.choice((-1, 1)), U(R, .28, .40), U(R, .05, .18), .45, big=False)
    for nm_, rec_ in (('L1a', L1), ('L2a', L2)):
        fork_any(nm_, rec_, (U(R, .35, .80),), R.choice((-1, 1)), U(R, .25, .40), U(R, .05, .15), .50, big=False)
    for rec_, n_ in ((A, 3), (B, 0), (T1, 2), (B2, 1), (B3, 1), (D, 1), (G, 1), (C, 1), (R1, 1)):
        add_stubs(R, rec_, n_)

    br = [x for x in RECS if x['kind'] in ('branch', 'fork')]
    for a in range(len(br)):
        for b in range(a + 1, len(br)):
            Ar, Br = br[a], br[b]
            if Ar.get('parent') == Br['id'] or Br.get('parent') == Ar['id']:
                continue
            Pa, Pb = Ar['P'][::2], Br['P'][::2]
            d = np.linalg.norm(Pa[:, None] - Pb[None], axis=2) - Ar['r'][::2][:, None] - Br['r'][::2][None]
            i, j = np.unravel_index(d.argmin(), d.shape)
            if d[i, j] < .03:
                CONTACTS.append(((Pa[i] + Pb[j]) / 2).tolist())
    if PHASE >= 2:
        twigs(R, [x for x in RECS if x['kind'] == 'fork' and x.get('name') not in ('T1c', 'T2b', 'Bc', 'T1a', 'T1aa', 'T1b', 'Ba', 'B2a', 'B3a')] + [L1, L2, F1, F2, E, D, G, N6, N8])   # v021：主枝上的分叉不長細枝   # v017：右上主枝不長細枝（輪廓乾淨）
        litter(R)
    print('PLAN', v, 'phase', PHASE, {k: sum(1 for x in RECS if x['kind'] == k) for k in ('branch', 'fork', 'stub', 'twig', 'litter')},
          'contacts', len(CONTACTS))
    return RECS


for _f in (plan, CAPC, smooth_r, XS):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)

# v013 材質分區：依參考圖，苔集中在主木 A 頂面與拱枝上緣、成片但邊緣破碎；蘑菇在 A 左段頂面成一叢、尺寸放大到參考比例。
#   做法：取 v5 的 finish_body_base、v4 的 make_cards 原始碼，只改門檻與尺寸常數後在同一命名空間重新定義（不改舊檔）。
import re as _re


def _redef(path, fname, reps):
    src = open(path, encoding='utf-8').read()
    i = src.index(f'def {fname}(')
    j = src.index('\ndef ', i + 10)
    k = src.find('\nfor f in (', i + 10)
    if 0 < k < j:
        j = k
    body = src[i:j]
    for x, y in reps:
        assert body.count(x) == 1, (fname, x)
        body = body.replace(x, y)
    exec(compile(body, path + f'::{fname}@v026', 'exec'), ns)


_redef(HERE + '/game_dr09v5.py', 'finish_body_base', [
    ("    patch = sm(nzA + .45 * nzB, -.04, .18) * sm(nz15 + .45, 0, .35)",
     "    ZM = MOSSZONE(co)\n    patch = sm(nzA + .45 * nzB + .75 * ZM, -.22, .02) * sm(nz15 + .45 + .25 * ZM, -.10, .25)"),   # v017：A 頂面核心連成一片，邊緣仍破碎
    ("    moss_top = thick * sm(up, .28, .68) * patch",
     "    _lat = sm(nzA + .35 * nzB, -.15, .35)\n    moss_top = ZM * sm(up, -.05 - .50 * _lat, .38 - .30 * _lat) * patch"),   # v020：往兩側消退的範圍沿長度起伏          # v016：苔只在 A 頂面、拱枝 B 頂部成主要覆蓋區
    ("    moss = np.clip(np.maximum(moss_top, .80 * moss_wet), 0, 1) * bark",
     "    moss = np.clip(np.maximum(moss_top, .50 * moss_wet), 0, 1) * bark"),   # 其他枝只留零星濕苔，不整根鋪綠
    ("    lich = .55 * sm(r0, .020, .045) * sm(up, -.55, -.05) * sm(nz7 + .45 * nz15, .22, .36) * bark * (1 - sm(moss, .2, .6))",
     "    lich = .6 * sm(r0, .020, .050) * sm(up, -.65, .05) * sm(nz15 + .45 * nz7, .47, .53) * sm(nzB, -.10, .10) * bark * (1 - sm(moss, .05, .25)) * sm(co[:, 2], .04, .10)"),   # v020：中頻切塊、不上頂面   # v019：雜訊式零星斑減量   # v018：邊界清楚的扁平斑   # v017：側面、頂面的灰白斑（不在苔上、不貼地）
    ("    W[:, 1] = lich * .90\n", "    W[:, 1] = np.maximum(lich, LICHENW(co) * bark * (1 - sm(moss, .05, .25)))\n"),   # v019：指定位置的灰白地衣斑片
    ("    m1 = kind == 1\n", "    m3 = kind == 3\n    W[m3] = 0\n    W[m3, 2] = fib[m3]\n    W[m3, 4] = 1 - fib[m3]\n    m1 = kind == 1\n"),   # v018：蘑菇（kind 3）傘面＝赭棕、傘緣與菌柄＝淺色
    ("    W[:, 2] = fib\n", "    W[:, 2] = fib\n    _ck = np.array((list(getattr(mb, 'crkl', [])) + [0.0] * n)[:n])\n    W[:, 3] = sm(_ck, .12, .55) * .95   # v017：裂縫用 Inner（深褐）層\n"),
])


def MOSSZONE(co):
    """v016：苔的主要覆蓋區＝ A（斷口 0.6 m 之後、中段偏左最濃）與拱枝 B（軸心離地 0.5 m 以上的拱頂）表面附近。"""
    out = np.zeros(len(co))
    PATCH = PATCH26   # v021：A 主苔毯＋小次苔   # v018：(s 中心, 半寬, 權重)，中間露樹皮
    for nm, wt, s0, zmin in (('A', 1.0, .14, -1.0), ('B', 1.0, 0.0, .40), ('B3', 1.0, 0.0, .30)):
        rec = next((x for x in RECS if x.get('name') == nm and not x.get('dead')), None)
        if rec is None:
            continue
        P, r, s_ = rec['P'], rec['r'], rec['s']
        k = (s_ > s0) & (P[:, 2] > zmin)
        fall = np.zeros(len(s_))
        for c_, hw_, w_ in PATCH[nm]:
            fall = np.maximum(fall, w_ * sm(hw_ - np.abs(s_ - c_), 0, hw_ * .45))
        P, r, fall = P[k][::2], r[k][::2], fall[k][::2]
        if not len(P):
            continue
        for i0 in range(0, len(co), 20000):
            c = co[i0:i0 + 20000]
            d = np.linalg.norm(c[:, None, :] - P[None], axis=2) - r[None]
            j = d.argmin(1)
            dm = d[np.arange(len(c)), j]
            out[i0:i0 + 20000] = np.maximum(out[i0:i0 + 20000], wt * fall[j] * sm(.10 - dm, 0, .06))   # 截面扁鼓、節瘤讓表面離軸線 ±3–5 cm，範圍放寬
    return out


ns['MOSSZONE'] = types.FunctionType(MOSSZONE.__code__, ns, 'MOSSZONE')
_SPL_SRC = """
def splinter(mb, c, Te, Ne, Be, rr, sp, lv):
    # v014：撕裂木刺改成順木紋的不規則薄片（6 點截面、多段、微彎、扭轉、鋸齒收尖、尖端偏一側），不再是方正木板
    th = sp['th']
    h = lambda k: math.sin(th * 12.9898 + sp['len'] * 78.233 + k * 37.719) * .5 + .5      # 固定雜訊，不動共用亂數
    rd0 = Ne * math.cos(th) + Be * math.sin(th)
    wv0 = np.cross(Te, rd0)
    wv0 /= np.linalg.norm(wv0) + 1e-12
    if sp.get('lift'):                     # v016：A 左端切線朝下，寬裂片改朝水平／略上方伸出（各片不同）
        Te = Te + np.array((0, 0, sp['lift']))
        Te = Te / np.linalg.norm(Te)
    _ro = sp.get('rot', 0.0)
    if _ro:
        rd0, wv0 = rd0 * math.cos(_ro) + wv0 * math.sin(_ro), wv0 * math.cos(_ro) - rd0 * math.sin(_ro)
        rp_ = Ne * math.cos(th) + Be * math.sin(th)
    else:
        rp_ = rd0
    ln, w = sp['len'], sp['w']
    tk = max(.004, w * sp.get('thk', .22))
    base = c - Te * ln * .25 + rd0 * rr * sp.get('rad', .82)
    slab = sp.get('slab', False)
    segs = (7 if lv == 0 else 3)
    tw = (h(1) - .5) * (.35 if slab else 1.1)          # 沿長度扭轉（寬片幾乎不扭）
    sway = (h(2) - .5) * (.04 if slab else .10) * ln   # 側向彎
    prof = ([(-1, -.35), (-.70, -1), (.45, -.85), (1, -.05), (.80, .90), (-.55, 1)] if slab else
            [(-1, 0), (-.55, -.9), (.35, -1), (1, -.25), (.70, .85), (-.30, .70)])     # 寬片：塊狀不規則截面；細片：不對稱薄片
    if slab:
        base = c - Te * sp.get('emb', .08) + rp_ * rr * sp.get('rad', .5)   # 基部從斷面內部長出，連續接入木芯
    rings, cen = [], []
    for k in range(segs + 1):
        t = k / segs
        a = tw * t
        rd = rd0 * math.cos(a) + wv0 * math.sin(a)
        wv = wv0 * math.cos(a) - rd0 * math.sin(a)
        p = base + Te * ln * t + rp_ * (rr * sp['out'] * t * t) + wv0 * sway * math.sin(t * math.pi * .9)
        jag = 1 + .22 * math.sin(t * 9.0 + th * 5.0) * t
        if slab:                                   # 前段保持寬厚，只有末段 35% 逐漸變尖（尖端偏一側、斜收）
            f_ = 1 - sp.get('tipw', .80) * float(np.clip((t - sp.get('keep', .62)) / (1 - sp.get('keep', .62)), 0, 1)) ** 1.3   # v017：tipw 小 = 末端鈍、參差
            ww = w * .5 * (1 - .12 * t) * f_ * (1 + .12 * math.sin(t * 6.0 + th * 3.0))
            tt = tk * .5 * (1 - .25 * t) * (.45 + .55 * f_)
        else:
            ww = w * (1 - .78 * t ** 1.25) * .5 * jag
            tt = tk * (1 - .60 * t) * .5
        cen.append(p)
        rings.append([mb.v(p + wv * u * ww * (1 + .18 * (h(10 + k * 6 + j) - .5)) + rd * v_ * tt, fib=1.0, kind=2) for j, (u, v_) in enumerate(prof)])
    tipv = mb.v(cen[-1] + Te * ln * ((.03 + .04 * h(3)) if slab else (.10 + .10 * h(3))) + wv0 * w * .18 * (h(4) - .5) + rd0 * rr * sp['out'] * .2, fib=1.0, kind=2)
    n = len(prof)
    for k in range(segs):
        a, b = rings[k], rings[k + 1]
        for j in range(n):
            j1 = (j + 1) % n
            mb.f((a[j], a[j1], b[j1], b[j]), [(ln * k / segs, j * w / n), (ln * k / segs, (j + 1) * w / n), (ln * (k + 1) / segs, (j + 1) * w / n), (ln * (k + 1) / segs, j * w / n)])
    a = rings[-1]
    for j in range(n):
        j1 = (j + 1) % n
        mb.f((a[j], a[j1], tipv), [(ln, j * w / n), (ln, (j + 1) * w / n), (ln * 1.15, (j + .5) * w / n)])
"""
exec(compile(_SPL_SRC, HERE + '/game_dr09v26.py::splinter', 'exec'), ns)
_redef(HERE + '/game_dr09v4.py', 'make_cards', [
    ("spots = [(A, .14, 'top'), (B, .06, 'ground')]", "spots = []"),   # v018：蘑菇改實體幾何（mushrooms）
    ("        for _ in range(R.randint(3, 4)):", "        for _ in range(R.randint(2, 3)):"),
    ("C.upright(base, U(R, .06, .11), U(R, .06, .10), R.choice(mush), U(R, 0, math.pi), tag)", "C.upright(base, *((U(R, .31, .34), U(R, .30, .33)) if _ == 0 else (U(R, .17, .21), U(R, .16, .19))), (mush[0] if _ == 0 else R.choice(mush[:2])), math.pi / 4 + U(R, -.15, .15), tag)"),   # v017：主菌蓋放大；十字卡轉 45°
    ("            q = p + np.array((U(R, -.10, .10), U(R, -.10, .10), 0))", "            q = p + np.array((U(R, -.10, .10), U(R, -.10, .10), 0)) * (.45 if _ == 0 else 1.0)"),   # v014：每叢一朵大的主菌蓋、其餘小而高低錯落
])
_mc_orig = ns['make_cards']


def _make_cards_A_first(body0):
    """v3 的蘑菇／貼地小蕈取 RECS[0] 當主木；v013 的 A 不是第一個擺的，暫時把 A 排到最前面（id 不變）。"""
    saved = ns['RECS']
    A = next(x for x in saved if x.get('name') == 'A')
    ns['RECS'] = [A] + [x for x in saved if x is not A]
    try:
        return _mc_orig(body0)
    finally:
        ns['RECS'] = saved


ns['make_cards'] = _make_cards_A_first


# ================================================================== v017 追加
def UND(rec, s, d):
    """v017：下緣上收——只收朝下的半圈（d.z < 0），上緣不動；rec['und'] = [(s 中心, 寬, 比例)]。"""
    u = rec.get('und')
    if not u or d[2] >= 0:
        return 1.0
    a = sum(k * math.exp(-((s - c) / w) ** 2) for c, w, k in u)
    return 1 - min(a, .6) * (-d[2]) ** 1.3


ns['UND'] = types.FunctionType(UND.__code__, ns, 'UND')
# tube 重新編譯（同 v005 的補丁鏈），加兩處：裂縫權重記在 mb.crk（頂點編號 → 權重）、下緣上收 UND
_H4 = H5['H4']
_H3 = _H4['H3']
_tsrc = H5['_v5_patch'](_H4['_v4_patch'](_H3['_v3_patch'](_H3['G']['_src'])))
_i = _tsrc.index('def tube(')
_tb = _tsrc[_i:_tsrc.index('\ndef ', _i + 10)]
for _a, _b in (("                _ck = CRACK(rec, sr[i], Ls, th)\n",
                "                _ck = CRACK(rec, sr[i], Ls, th)\n                mb.__dict__.setdefault('crk', {})[len(mb.V)] = _ck\n"),
               ("            ring.append(mb.v(C[i] + d * rj, fib=fib, mk=mk))",
                "            ring.append(mb.v(C[i] + d * (rj * UND(rec, sr[i], d)), fib=fib, mk=mk))")):
    assert _tb.count(_a) == 1, _a
    _tb = _tb.replace(_a, _b)
_wrap = ns['tube']
exec(compile(_tb, HERE + '/game_dr09v26.py::tube', 'exec'), ns)
ns['_tube1'] = ns['tube']
ns['tube'] = _wrap
# 細枝不長到 0.8 m 以上（不擋主輪廓）
_redef(HERE + '/game_dr09v4.py', 'twigs', [("(Pt[:, 2] + rt).max() < V['H'] * 1.08", "(Pt[:, 2] + rt).max() < V['H'] * .80")])
ns['_layer_mat_v002'] = ns['layer_mat']


def layer_mat():
    """M_DR09_Layered_v017：v002 的複本，只把纖維槽的顏色換成暖米黃 DR09_FreshWood_v017_Albedo（法線沿用）。"""
    m = bpy.data.materials.get('M_DR09_Layered_v017')
    if m:
        return m
    m0 = _layer_mat_v002()
    m = m0.copy()
    m.name = 'M_DR09_Layered_v017'
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'DR09_FreshWood_Albedo.png':
            n.image = bpy.data.images.load(f'{TEXD9}/DR09_FreshWood_v017_Albedo.png', check_existing=True)
    if m0.users == 0:
        bpy.data.materials.remove(m0)
    u = dict(m['unity'].to_dict()) if hasattr(m['unity'], 'to_dict') else dict(m['unity'])
    u['textures'] = str(u.get('textures', '')).replace('DR09_FreshWood_{Albedo,Normal} (fibre)', 'DR09_FreshWood_v017_Albedo + DR09_FreshWood_Normal (fibre)')
    m['unity'] = u
    return m


def finish_body(o, mb, lv):
    """v017 厚苔：苔權重高、朝上的面複製一層往外推 1–3 cm（雜訊起伏、順著表面），邊界收到 0.15 倍（邊緣薄、破碎）。LOD0、LOD1。"""
    finish_body_base(o, mb, lv)
    if lv > 1:
        return
    import bmesh
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    cl = bm.loops.layers.float_color['Layers']
    bm.verts.ensure_lookup_table()
    bm.normal_update()
    mv = {}
    for f in bm.faces:
        for l in f.loops:
            mv[l.vert.index] = max(mv.get(l.vert.index, 0), l[cl][0])
    sel = [f for f in bm.faces if f.normal.z > .10 and sum(mv.get(v.index, 0) for v in f.verts) / len(f.verts) > .50
           and min(mv.get(v.index, 0) for v in f.verts) > .22]
    if not sel:
        bm.free()
        return
    area = sum(f.calc_area() for f in sel)
    ret = bmesh.ops.duplicate(bm, geom=sel)
    nf = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)]
    nv = {v for f in nf for v in f.verts}
    old = {}
    for a, b in ret['vert_map'].items():
        if b in nv:
            old[b] = a
        elif a in nv:
            old[a] = b
    sf = set(nf)
    edge = set()
    for f in nf:
        for e in f.edges:
            if len([x for x in e.link_faces if x in sf]) < 2:
                edge |= set(e.verts)
    for v in nv:
        n = v.normal.copy() if v.normal.length > .1 else Vector((0, 0, 1))
        m = mv.get(old[v].index, 0) if v in old else .6
        th = (.010 + .020 * (.5 + .5 * noise.noise(v.co * 5.0)) + .006 * noise.noise(v.co * 16.0 + Vector((3, 1, 7)))) * sm(m, .35, .85)
        th = max(th, 0.0) * (.15 if v in edge else 1.0)
        v.co += n * (th + .0015)
    for f in nf:
        for l in f.loops:
            l[cl] = (1.0, 0.0, 0.0, 0.0)
    nfc = len(nf)
    bm.to_mesh(me)
    bm.free()
    print('MOSS_SHELL lod', lv, 'faces', nfc, 'area_m2', round(area, 3))


for _f in (layer_mat, finish_body):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)


def _make_cards_v17(body0):
    """v017：落葉卡逐片檢查依附——葉中心離地 3 cm 內算貼地；否則中心正下方 3.5 cm 內要打到木頭，
    或葉面頂點離木頭 < 8 mm 且中心離木頭 < 2 cm（斜貼在側面）。都不符合的刪掉（蘑菇十字卡不檢查）。"""
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector as V3
    C = _make_cards_A_first(body0)
    me = body0.data
    co = [body0.matrix_world @ v.co for v in me.vertices]
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
    groups = {}
    for f, t in zip(C.F, C.tag):
        groups.setdefault(t, []).append(f)
    drop, nleaf = set(), 0
    for t, fs in groups.items():
        vs = sorted({i for f in fs for i in f})
        if len(vs) != 6:
            continue
        nleaf += 1
        P = [V3(C.V[i]) for i in vs]
        c = (P[2] + P[3]) / 2
        if c.z < .03:
            continue
        h = tree.ray_cast(c + V3((0, 0, .01)), V3((0, 0, -1)), .045)
        if h[0] is not None:
            continue
        if min(tree.find_nearest(p)[3] for p in P) < .008 and tree.find_nearest(c)[3] < .02:
            continue
        drop.add(t)
    keep = [k for k, t in enumerate(C.tag) if t not in drop]
    C.F = [C.F[k] for k in keep]
    C.tag = [C.tag[k] for k in keep]
    print('LEAF_CHECK leaves', nleaf, 'removed_floating', len(drop))
    ns['LEAF_CHECK'] = dict(leaves=nleaf, removed_floating=len(drop))
    return C


ns['make_cards'] = _make_cards_v17


# ================================================================== v018 追加
def CAPC(rec, e=0):
    """v018：斷面中心點往外的距離（倍半徑）可依端點指定（rec['capce'][e]），長斜撕裂面才會是平順的斜面而不是凹錐。"""
    ce = rec.get('capce') or {}
    if e in ce:
        return ce[e]
    return rec.get('capc', .16 if rec.get('heavy') else .50)


ns['CAPC'] = types.FunctionType(CAPC.__code__, ns, 'CAPC', CAPC.__defaults__)
_a = "cen = mb.v(C[i] + Te * rr * CAPC(rec) * rec['ext'][e]"
assert _tb.count(_a) == 1
_tb18 = _tb.replace(_a, "cen = mb.v(C[i] + Te * rr * CAPC(rec, e) * rec['ext'][e]")

# v018：斷面不再是一片平的扇形——加一圈中間點，前後交錯錯開（CAPJ 倍半徑），撕裂面成參差的階梯
_a = "cen = mb.v(C[i] + Te * rr * CAPC(rec, e) * rec['ext'][e], fib=1.0, mk=0)"
assert _tb18.count(_a) == 1, 'cen'
_tb18 = _tb18.replace(_a, _a + "\n        mids = [mb.v((np.array(mb.V[x[0]]) + np.array(mb.V[cen])) * .5 + Te * rr * CAPJ(rec, e) * (.6 + .4 * math.sin(jj * 7.31 + e)) * (1.0 if jj % 2 else -.7) + (np.array(mb.V[x[0]]) - np.array(mb.V[cen])) * .10 * math.sin(jj * 3.7), fib=1.0, mk=0) for jj, x in enumerate(ext)] if (CAPJ(rec, e) and lv <= 1) else []")
_a = "            mb.f(qb, [cuv(x) for x in qb])"
assert _tb18.count(_a) == 1, 'qb'
_tb18 = _tb18.replace(_a, "            if mids:\n"
                          "                _m0, _m1 = (mids[j], mids[j1]) if e == 1 else (mids[j1], mids[j])\n"
                          "                _qc, _qd = (qb[0], qb[1], _m1, _m0), (_m0, _m1, cen)\n"
                          "                mb.f(_qc, [cuv(x) for x in _qc])\n"
                          "                mb.f(_qd, [cuv(x) for x in _qd])\n"
                          "            else:\n"
                          "                mb.f(qb, [cuv(x) for x in qb])")


def CAPJ(rec, e):
    return (rec.get('capj') or {}).get(e, 0.0)


ns['CAPJ'] = types.FunctionType(CAPJ.__code__, ns, 'CAPJ')
# ================================================================== v019 追加（在 tube 原始碼編譯前）
# 一、斷口交界：剝皮範圍改由 PEELW 決定。原本＝「斷口側半圈、固定長度」→ 交界是一圈整齊的環，裸木像套在前端的外殼。
#     v019：每個方向的剝皮長度＝底長＋幾條長短、寬窄不一的舌（倍 r0），再加沿軸的小鋸齒；邊緣窄（0.1 r0）＝樹皮斷得乾脆。
_a = ("                    w = float(sm(dp - de, 0, dp * .35)) * float(sm(ang, -.05, .35))\n"
      "                    w *= float(sm(noise.noise(Vector(C[i] * 9 + d + off)) + .5, .2, .5))\n")
assert _tb18.count(_a) == 1, 'peel'
_tb18 = _tb18.replace(_a, "                    w = PEELW(rec, e, de, th, dp, ang, C[i], d, off)\n")


def PEELW(rec, e, de, th, dp, ang, p, d, off):
    jg = (rec.get('jag') or {}).get(e)
    if not jg:
        w = float(sm(dp - de, 0, dp * .35)) * float(sm(ang, -.05, .35))
        return w * float(sm(noise.noise(Vector(p * 9 + d + off)) + .5, .2, .5))
    r0 = rec['r0']
    L = jg['base']
    for tc, a, aw in jg['tongues']:
        dd = abs((th - tc + math.pi) % (2 * math.pi) - math.pi)
        L += a * math.exp(-(dd / aw) ** 2)
    L *= 1 + .22 * noise.noise(Vector((math.cos(th) * 2.5, math.sin(th) * 2.5, e * 3.1 + 7)))
    L += .22 * noise.noise(Vector(p * 14 + d * .6 + off))          # 沿軸的小鋸齒
    return float(sm(L * r0 - de, 0, r0 * .10))


def torn_end19(rec, e, tear, tilt, lths, nm, nsh, seed, Ls, Lm, Lsh, W, lift):
    """v019 折斷端：主長片各有自己的方位（lths＝相對 tear 的角度），基部高低、抬升方向都不同；中短碎片散在更寬的方位，
    不排成同一扇面。裂縫三道加長（4.5–7 倍半徑），往主幹內部延伸。"""
    rr = float(rec['r'][0 if e == 0 else -1])
    rec['tear'][e] = tear
    rec['cap'][e] = dict(tilt=tilt, notch=tear + math.pi, nw=.55, tooth=.06, lip=tear + 1.75, lw=.40, lipl=.18)
    cenL = .03 + tilt * .9
    rec.setdefault('capce', {})[e] = cenL
    rec.setdefault('capj', {})[e] = .30 * tilt
    rs = random.Random(seed)
    se = 0.0 if e == 0 else float(rec['s'][-1])
    sp = []
    plan_ = [('l', lt, Ls, 1.0, .12) for lt in lths] + [('m', None, Lm, .85, 1.9)] * nm + [('s', None, Lsh, .70, 2.1)] * nsh
    for k, (grp, lt, Lr, wf, spread) in enumerate(plan_):
        th = tear + (lt + U(rs, -spread, spread) if lt is not None else U(rs, -spread, spread))
        c = math.cos(th - tear)
        fr = (.42, .70, .58)[k % 3] if grp == 'l' else (U(rs, .35, .88) if grp == 'm' else U(rs, .15, .90))
        rimL = .03 + tilt * (1 + c)
        along = rr * (cenL + (rimL - cenL) * fr)
        lf = (lift[1], lift[0] * .5, lift[1] * .45)[k % 3] if grp == 'l' else U(rs, *lift)
        sp.append(dict(th=th, len=U(rs, *Lr) * (1.0, .72, .86)[k % 3] if grp == 'l' else U(rs, *Lr), w=U(rs, *W) * wf, out=U(rs, 0, .05), tk=.6,
                       thk=U(rs, .26, .42), rad=fr * XS(rec, se, th), slab=True, keep=U(rs, .22, .45), tipw=U(rs, .78, .92),
                       emb=-(along - U(rs, .01, .03)), rot=U(rs, -.45, .45), lift=lf))
    rec['splint'][e] = sp
    rec['cracks'] = [x for x in rec.get('cracks', []) if x[0] != e] + [(e, tear + .45, rr * 7.0, .09), (e, tear - .80, rr * 5.5, .08),
                                                                      (e, tear + 1.55, rr * 4.5, .07), (e, tear - 2.1, rr * 3.2, .07)]


# 三、地衣：指定位置的灰白扁平斑片（A 前側、拱枝 B／B3 正面側），半徑 5–10 cm，邊緣不規則（角度方向的波動）
LICH = [('A', .20, (0, -1, -.05), .055), ('A', .30, (0, -1, .45), .075), ('A', .44, (0, -1, .15), .095), ('A', .58, (0, -.7, .75), .065),
        ('A', .72, (0, -1, .05), .085), ('A', .86, (0, -.8, .50), .060),
        ('B', .16, (0, -1, .25), .065), ('B', .36, (0, -1, .45), .085), ('B', .55, (0, -.8, .60), .060), ('B', .80, (0, -1, .15), .075),
        ('B3', .45, (0, -1, .55), .065)]


def LICHENW(co):
    out = np.zeros(len(co))
    for nm, fr, dv, R_ in LICH:
        rec = next((x for x in RECS if x.get('name') == nm and not x.get('dead')), None)
        if rec is None:
            continue
        i = int(fr * (len(rec['P']) - 1))
        dv = np.array(dv, float)
        dv /= np.linalg.norm(dv)
        P0 = rec['P'][i]
        c = P0 + dv * rec['r'][i]
        cand = np.linalg.norm(co - P0, axis=1) < rec['r'][i] * 2.2   # 中心貼到實際表面：該方向上最外側的頂點（截面扁鼓、節瘤會讓表面離 P + r 數公分）
        if cand.any():
            v_ = co[cand] - P0
            c = co[cand][((v_ @ dv) / (np.linalg.norm(v_, axis=1) + 1e-9)).argmax()]
        R_ = R_ * 1.5
        dist = np.linalg.norm(co - c, axis=1)
        k = (dist < R_ * 1.8) & ((co - P0) @ dv > 0)
        if not k.any():
            continue
        q = co[k] - c
        ang = np.arctan2(q[:, 2], q[:, 0])
        ir = R_ * (1 + .30 * np.sin(ang * 3 + fr * 17) + .18 * np.sin(ang * 7 + fr * 5) + .12 * np.sin(co[k] @ np.array((61., 47., 53.))))
        out[k] = np.maximum(out[k], sm(ir - dist[k], 0, .020))
    return out


for _f in (PEELW, torn_end19, LICHENW):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__)
ns['LICH'] = LICH
exec(compile(_tb18, HERE + '/game_dr09v26.py::tube', 'exec'), ns)
ns['_tube1'] = ns['tube']
ns['tube'] = _wrap


def torn_end(rec, e, tear, tilt, nl, nm, nsh, seed, Ls, Lm, Lsh, W, lift):
    """v018 折斷端：長斜撕裂面（tear 方向最長）＋纖維。纖維基部依徑向比例 fr 落在撕裂面上（離端點 along），
    方向沿木紋（只略抬升、幾乎不外張），長片集中在撕裂長邊、中短片散開；薄片、末端收薄。"""
    rr = float(rec['r'][0 if e == 0 else -1])
    rec['tear'][e] = tear
    rec['cap'][e] = dict(tilt=tilt, notch=tear + math.pi, nw=.55, tooth=.06, lip=tear + 1.75, lw=.40, lipl=.18)
    cenL = .03 + tilt * .9
    rec.setdefault('capce', {})[e] = cenL
    rec.setdefault('capj', {})[e] = .30 * tilt
    rs = random.Random(seed)
    se = 0.0 if e == 0 else float(rec['s'][-1])
    sp = []
    for grp, n, Lr, wf, spread in (('l', nl, Ls, 1.0, .45), ('m', nm, Lm, .85, 1.3), ('s', nsh, Lsh, .70, 2.2)):
        for _ in range(n):
            th = tear + U(rs, -spread, spread)
            c = math.cos(th - tear)
            fr = U(rs, .40, .88) if grp != 's' else U(rs, .15, .88)
            rimL = .03 + tilt * (1 + c)
            along = rr * (cenL + (rimL - cenL) * fr)
            sp.append(dict(th=th, len=U(rs, *Lr), w=U(rs, *W) * wf, out=U(rs, 0, .04), tk=.6, thk=U(rs, .28, .42),
                           rad=fr * XS(rec, se, th), slab=True, keep=U(rs, .25, .45), tipw=U(rs, .80, .92),
                           emb=-(along - U(rs, .01, .03)), rot=U(rs, -.3, .3), lift=U(rs, *lift)))
    rec['splint'][e] = sp
    rec['cracks'] = [x for x in rec.get('cracks', []) if x[0] != e] + [(e, tear + .5, rr * 4.0, .10), (e, tear - .7, rr * 3.0, .09), (e, tear + 1.4, rr * 2.2, .08)]


ns['torn_end'] = types.FunctionType(torn_end.__code__, ns, 'torn_end')
# 刪隱藏面時裂縫權重一起重排（v017 的 mb.crk 用的是刪面前的頂點編號，刪面後會錯位）
_redef(HERE + '/game_dr09v2.py', 'hidden_faces', [
    ("    me = o.data\n    co = np.array(mb.V)\n", "    me = o.data\n    co = np.array(mb.V)\n    mb.crkl = [getattr(mb, 'crk', {}).get(i, 0.0) for i in range(len(mb.V))]\n"),
    ("    for nm in ('fib', 'mk', 'kind'):", "    for nm in ('fib', 'mk', 'kind', 'crkl'):")])
# 細枝：不高於 0.7 m
_redef(HERE + '/game_dr09v4.py', 'twigs', [("(Pt[:, 2] + rt).max() < V['H'] * 1.08", "(Pt[:, 2] + rt).max() < V['H'] * .70")])
# 落葉：更集中在木頭邊；v3 的小褐蕈卡片取消（蘑菇改實體）
_keep_mc = ns['make_cards']
_redef(HERE + '/game_dr09v3.py', 'make_cards', [
    ("if R.random() > .015 + .985 * math.exp(-max(d, 0) / .09):", "if R.random() > .004 + .996 * math.exp(-max(d, 0) / .07):"),
    ("    nl = int((hi[0] - lo[0]) * (hi[1] - lo[1]) * 22)", "    nl = int((hi[0] - lo[0]) * (hi[1] - lo[1]) * 18)"),
    ("    for k in range(2):", "    for k in range(0):")])
ns['_make_cards3'] = ns['make_cards']
ns['make_cards'] = _keep_mc

# ------------------------------------------------------------------ v018 蘑菇（實體幾何，併進本體網格，kind = 3）
MUSH = [  # (x, y, 傘半徑, 菌柄高, 傾斜 x, 傾斜 y) —— 計畫座標；A 隆起段頂面偏左（不擋拱枝 B 的拱頂輪廓）
    (-1.18, -.43, .125, .115, -.06, -.12),    # v026 九：主蘑菇移到 A 隆起段的苔毯上（不長在斷口裸木上），大、中、小三朵，高低不同
    (-1.01, -.40, .088, .078, .12, -.08),
    (-1.31, -.49, .066, .058, -.16, -.05),
]


def mushrooms(mb, lv, n0):
    seg = (14, 10, 7)[lv]
    V_ = np.array(mb.V[n0:])
    kd = np.array(mb.kind[n0:])
    for (x, y, R_, H_, lx, ly) in MUSH:
        d = np.hypot(V_[:, 0] - x, V_[:, 1] - y)
        ok = (kd == 0) & (d < .06)
        if not ok.any():
            ok = (kd == 0) & (d < d[kd == 0].min() + .02)
        z0 = float(V_[ok, 2].max()) - .02                      # 根部埋進木頭（再被苔殼蓋住）
        base = np.array((x, y, z0))
        up = np.array((lx, ly, 1.0))
        up /= np.linalg.norm(up)
        sa = np.cross(up, (0, 1.0, 0))
        sa /= np.linalg.norm(sa)
        sb = np.cross(up, sa)
        rs = R_ * .19
        top = base + up * (H_ + .02)
        # 菌柄：根部略粗、往上略細、微彎
        rings = []
        for k in range(4):
            t = k / 3
            c = base + up * (H_ + .02) * t + sa * R_ * .10 * math.sin(t * math.pi)
            rr_ = rs * (1.30 - .45 * t)
            rings.append([mb.v(c + (sa * math.cos(2 * math.pi * j / seg) + sb * math.sin(2 * math.pi * j / seg)) * rr_, fib=1.0, kind=3) for j in range(seg)])
        for k in range(3):
            for j in range(seg):
                j1 = (j + 1) % seg
                mb.f((rings[k][j], rings[k][j1], rings[k + 1][j1], rings[k + 1][j]), [(j / seg, k / 3), ((j + 1) / seg, k / 3), ((j + 1) / seg, (k + 1) / 3), (j / seg, (k + 1) / 3)])
        # 菌傘：寬而低的圓頂，傘緣略下彎；下面（菌褶）回到菌柄
        Hc = R_ * .68
        prof = [(.30, .93, 0.0), (.62, .74, 0.0), (.86, .45, .10), (1.00, .16, .45), (.97, .02, .75), (.62, -.04, 1.0), (.26, -.02, 1.0)]
        ct = top + up * Hc * .02
        tipv = mb.v(top + up * Hc, fib=0.0, kind=3)
        cr = []
        for (a, h, fb) in prof:
            ring = []
            for j in range(seg):
                ang = 2 * math.pi * j / seg
                wob = 1 + .05 * math.sin(3 * ang + x * 40)
                ring.append(mb.v(ct + (sa * math.cos(ang) + sb * math.sin(ang)) * R_ * a * wob + up * Hc * h, fib=fb, kind=3))
            cr.append(ring)
        for j in range(seg):
            j1 = (j + 1) % seg
            mb.f((tipv, cr[0][j], cr[0][j1]), [(.5, .5), (j / seg, 0), ((j + 1) / seg, 0)])
        for k in range(len(cr) - 1):
            for j in range(seg):
                j1 = (j + 1) % seg
                mb.f((cr[k][j], cr[k + 1][j], cr[k + 1][j1], cr[k][j1]), [(j / seg, k / 7), (j / seg, (k + 1) / 7), ((j + 1) / seg, (k + 1) / 7), ((j + 1) / seg, k / 7)])


_tube_v2 = ns['tube']


def tube(mb, rec, lv, col=False):
    if rec['kind'] == 'stub' and any(math.hypot(rec['P'][0][0] - m[0], rec['P'][0][1] - m[1]) < .30 for m in MUSH):
        global SEG, OWN
        k_ = OWN != rec['id']
        SEG, OWN = SEG[k_], OWN[k_]             # 也從枝段表移除，免得刪隱藏面時在 A 上挖洞
        rec['dead'] = True
        return                                  # v018：蘑菇旁的平截小樁不建（像立柱、搶主傘）
    n0 = len(mb.V)
    _tube_v2(mb, rec, lv, col)
    if col or rec.get('name') != 'A' or lv > 2:
        return
    # （A 上靠近蘑菇的小樁不建，免得像一根立柱）
    n1 = len(mb.V)
    mushrooms(mb, lv, n0)
    if hasattr(mb, 'own'):
        mb.own += [-1] * (n1 - len(mb.own)) + [rec['id']] * (len(mb.V) - n1)


for _f in (mushrooms, tube):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)
ns['MUSH'] = MUSH
ns['_tube_v2'] = _tube_v2
ns['_layer_mat_v002_18'] = ns['_layer_mat_v002']


def layer_mat():
    """M_DR09_Layered_v018：v002 的複本；裸木＝DR09_FreshWood_v018（暖米黃偏淡赭）、苔＝DR09_Moss_v018（低頻色差）、
    地衣槽（原 Rot）＝DR09_Lichen_v018（扁平灰白／灰綠斑），地衣法線改用樹皮法線（順樹皮貼附、不像苔那樣蓬起）。"""
    m = bpy.data.materials.get('M_DR09_Layered_v026')
    if m:
        return m
    m0 = _layer_mat_v002_18()
    m = m0.copy()
    m.name = 'M_DR09_Layered_v026'
    sw = {'DR09_FreshWood_Albedo.png': 'DR09_FreshWood_v018_Albedo', 'DR09_Moss_v002_Albedo.png': 'DR09_Moss_v018_Albedo',
          'DR09_Lichen_v002_Albedo.png': 'DR09_Lichen_v018_Albedo', 'DR09_Bark_v002_Albedo.png': 'DR09_Bark_v018_Albedo'}
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            if n.image.name in sw:
                n.image = bpy.data.images.load(f'{TEXD9}/{sw[n.image.name]}.png', check_existing=True)
            elif n.image.name == 'DR08_Rot_Normal.png':
                n.image = bpy.data.images.load(f'{ROOT}/art/exports/d2-logs-b/DR08_Shared/Textures/DR08_Bark_Normal.png', check_existing=True)
                n.image.colorspace_settings.name = 'Non-Color'
    if m0.users == 0:
        bpy.data.materials.remove(m0)
    u = dict(m['unity'].to_dict()) if hasattr(m['unity'], 'to_dict') else dict(m['unity'])
    u['textures'] = ('DR09_Shared/Textures: DR09_Bark_v018_Albedo (bark), DR09_Moss_v018_Albedo (moss), DR09_Lichen_v018_Albedo (rot slot = lichen, normal = DR08_Bark_Normal), '
                     'DR09_FreshWood_v018_Albedo + DR09_FreshWood_Normal (fibre), DR09_Soil_v002_Albedo (soil = mushroom cap / ground soil); '
                     'normals DR08_Shared/Textures/DR08_{Bark,Moss,Inner,Soil}_Normal + DR08_Inner_Albedo')
    m['unity'] = u
    return m


def finish_body(o, mb, lv):
    """v018 苔殼：同 v017，厚度 1.4–4 cm，加一層細小起伏（22／m），邊界收到 0.12 倍。"""
    finish_body_base(o, mb, lv)
    if lv > 1:
        return
    import bmesh
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    cl = bm.loops.layers.float_color['Layers']
    bm.verts.ensure_lookup_table()
    bm.normal_update()
    mv = {}
    for f in bm.faces:
        for l in f.loops:
            mv[l.vert.index] = max(mv.get(l.vert.index, 0), l[cl][0])
    sel = [f for f in bm.faces if f.normal.z > .05 and sum(mv.get(v.index, 0) for v in f.verts) / len(f.verts) > .40
           and min(mv.get(v.index, 0) for v in f.verts) > .08]   # v018：放寬，苔塊內部不留破洞（破洞邊會形成深色細縫）
    ss = set(sel)                       # v019：補洞——四周已選的面包住、苔權重 > 0.15 的面也選進來（洞邊會被壓薄成深色細縫）
    for _ in range(3):
        ss |= {f for f in bm.faces if f not in ss and f.normal.z > -.2 and sum(mv.get(v.index, 0) for v in f.verts) / len(f.verts) > .15
               and sum(1 for e in f.edges for g in e.link_faces if g is not f and g in ss) >= 2}
    sel = list(ss)
    if not sel:
        bm.free()
        return
    area = sum(f.calc_area() for f in sel)
    ret = bmesh.ops.duplicate(bm, geom=sel)
    nf = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)]
    nv = {v for f in nf for v in f.verts}
    old = {}
    for a, b in ret['vert_map'].items():
        if b in nv:
            old[b] = a
        elif a in nv:
            old[a] = b
    bmesh.ops.remove_doubles(bm, verts=list(nv), dist=.0008)   # v018：接縫處重複頂點焊起來，苔殼內部不再有裂線
    nf = [f for f in nf if f.is_valid]
    nv = {v for f in nf for v in f.verts}
    bm.normal_update()
    sf = set(nf)
    edge = set()
    for f in nf:
        for e in f.edges:
            if len([x for x in e.link_faces if x in sf]) < 2:
                edge |= set(e.verts)
    for v in nv:
        n = v.normal.copy() if v.normal.length > .1 else Vector((0, 0, 1))
        m = mv.get(old[v].index, 0) if v in old else .6
        th = (.014 + .044 * max(0.0, .5 + .7 * noise.noise(v.co * 3.2 + Vector((5, 2, 9)))) + .010 * noise.noise(v.co * 9.0) + .006 * noise.noise(v.co * 22.0 + Vector((3, 1, 7)))) * sm(m, .30, .85)   # v019：墊狀厚薄起伏
        th = max(th, 0.0) * (.12 if v in edge else 1.0)
        v.co += n * (th + .0015)
    for f in nf:
        for l in f.loops:
            l[cl] = ((.30 + .25 * (.5 + .5 * noise.noise(l.vert.co * 7.0))) if l.vert in edge else 1.0, 0.0, 0.0, 0.0)   # v020：苔毯邊緣漸淡、透出樹皮（不是一片布的硬邊）
    nfc = len(nf)
    bm.to_mesh(me)
    bm.free()
    print('MOSS_SHELL lod', lv, 'faces', nfc, 'area_m2', round(area, 3))


for _f in (layer_mat, finish_body):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__, _f.__defaults__)


# v019：地衣斑片邊緣——頂點權重 G 只給大概位置，邊緣鋸齒由 DR09_LichenMask_v019（2 次／公尺）決定：
#   w' = clamp((G × 1.25 ＋ mask) × 7 − 7.34)，再接原本的 Rot 混合（原本的 ×1.6−0.3 改成直通）。
_layer_mat18 = ns['layer_mat']


def layer_mat19():
    m = bpy.data.materials.get('M_DR09_Layered_v026')
    if m and m.get('v019_lichen_mask'):
        return m
    m = _layer_mat18()
    N, Lk = m.node_tree.nodes, m.node_tree.links
    sp = next(n for n in N if n.bl_idname == 'ShaderNodeSeparateColor')
    g = sp.outputs[1]
    sh = next(l.to_node for l in g.links if l.to_node.bl_idname == 'ShaderNodeMath')
    uv = next(n for n in N if n.bl_idname == 'ShaderNodeUVMap' and n.uv_map == 'UVMap')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (2, 2, 1)
    Lk.new(uv.outputs['UV'], mp.inputs['Vector'])
    t = N.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(ROOT + '/art/exports/d2-logs-b/DR09_Shared/Textures/DR09_LichenMask_v019.png', check_existing=True)
    t.image.colorspace_settings.name = 'Non-Color'
    Lk.new(mp.outputs[0], t.inputs['Vector'])
    a = N.new('ShaderNodeMath')
    a.operation = 'MULTIPLY_ADD'
    Lk.new(g, a.inputs[0])
    a.inputs[1].default_value = 1.25
    Lk.new(t.outputs['Color'], a.inputs[2])
    b = N.new('ShaderNodeMath')
    b.operation = 'MULTIPLY_ADD'
    b.use_clamp = True
    Lk.new(a.outputs[0], b.inputs[0])
    b.inputs[1].default_value = 7.0
    b.inputs[2].default_value = -7.34
    Lk.new(b.outputs[0], sh.inputs[0])
    sh.inputs[1].default_value = 1.0
    sh.inputs[2].default_value = 0.0
    m['v019_lichen_mask'] = True
    return m


ns['layer_mat'] = types.FunctionType(layer_mat19.__code__, ns, 'layer_mat')
ns['_layer_mat18'] = _layer_mat18


# ================================================================== v020 追加
# 一、斷口立體結構：裂塊（stave）＝主幹截面的一個扇環（角度 span、內外半徑 ri～ro，倍半徑），從主幹內部某個深度 dep 開始、
#     沿主幹方向伸出斷面 ext 公尺；末段收窄、內半徑往外收成薄片、尖端偏一側；略往外張、各自抬升。
#     外側面在根部一段（barkL）保留樹皮（樹皮不規則地蓋住部分裸木）；側面、內面帶深色裂縫權重（dark），整片不同色。
#     每片起點（深度）、方位、粗細、長度、末端都不同，從正面、俯視、斜視都是立體的塊，不是一片扇形薄板。
def staves(mb, rec, lv):
    for e, lst in (rec.get('staves') or {}).items():
        P = rec['P']
        c = np.array(P[0] if e == 0 else P[-1], float)
        Te = np.array(P[0] - P[2] if e == 0 else P[-1] - P[-3], float)
        Te /= np.linalg.norm(Te)
        Ti = -Te
        dn = np.array((0, 0, -1.0))
        Nn = dn - Ti * (Ti @ dn)
        Nn /= np.linalg.norm(Nn)
        Bn = np.cross(Ti, Nn)                       # A 左端：th 0＝下、π/2＝後（+y）、−π/2＝前（−y）、π＝上
        rr = float(rec['r'][0 if e == 0 else -1])
        se = 0.0 if e == 0 else float(rec['s'][-1])
        segs, na = (7, 5) if lv == 0 else ((4, 3) if lv == 1 else (2, 3))
        crk = mb.__dict__.setdefault('crk', {})
        for q, st in enumerate(lst):
            hj = lambda k: math.sin(q * 91.7 + k * 37.719 + st['th'] * 13.1) * .5 + .5
            L = st['dep'] + st['ext']
            rings, cens = [], []
            for k in range(segs + 1):
                t = k / segs
                g = float(np.clip((t - st['keep']) / (1 - st['keep']), 0, 1))
                sp_ = st['span'] * (1 - .82 * g ** 1.15)
                ct = st['th'] + st['bias'] * st['span'] * .5 * g
                ri = st['ri'] + (st['ro'] - st['ri']) * .60 * g ** 1.2
                ro = st['ro'] * (1 - .10 * g)
                rdc = Nn * math.cos(ct) + Bn * math.sin(ct)
                cen_off = Te * (-st['dep'] + L * t) + rdc * st['out'] * t * t + np.array((0, 0, st['lift'])) * t * t
                ring = []
                arcs = [(ct - sp_ / 2 + sp_ * j / (na - 1), ro, 'o', j) for j in range(na)] + \
                       [(ct + sp_ / 2 - sp_ * j / (na - 1), ri, 'i', j) for j in range(na)]
                for a, rf, side, j in arcs:
                    d = Nn * math.cos(a) + Bn * math.sin(a)
                    jit = 1 + (.07 if 0 < j < na - 1 else .16) * (hj(k * 11 + j + (0 if side == 'o' else 50)) - .5) * (.3 + t)   # 兩側撕開的邊參差
                    p = c + cen_off + d * rr * rf * XS(rec, se, a) * jit + Te * (.025 * (hj(500 + k * 7 + j) - .5) if j in (0, na - 1) else 0)
                    if side == 'o':
                        along = L * t
                        bk = along < st['barkL'] * L * (.75 + .5 * hj(200 + j))
                        fib = 0.0 if bk else 1.0
                        ck = 0.0 if bk else .10 * hj(300 + k)
                    else:
                        fib = 1.0
                        ck = st['dark'] * (.6 + .4 * hj(400 + k + j))
                    if j in (0, na - 1):
                        ck = max(ck, st['dark'] * .8)          # 兩側撕開的面較深
                    crk[len(mb.V)] = ck
                    ring.append(mb.v(p, fib=fib, kind=2))
                rings.append(ring)
                cens.append(c + cen_off + rdc * rr * (ri + ro) * .5)
            n = len(rings[0])
            crk[len(mb.V)] = st['dark'] * .5
            tipv = mb.v(cens[-1] + Te * L * .05 + (Nn * math.cos(st['th']) + Bn * math.sin(st['th'])) * rr * .04 * (hj(7) - .5), fib=1.0, kind=2)
            crk[len(mb.V)] = st['dark']
            basev = mb.v(cens[0] - Te * .01, fib=1.0, kind=2)
            for k in range(segs):
                a_, b_ = rings[k], rings[k + 1]
                for j in range(n):
                    j1 = (j + 1) % n
                    mb.f((a_[j], a_[j1], b_[j1], b_[j]), [(L * k / segs, j * .04), (L * k / segs, (j + 1) * .04), (L * (k + 1) / segs, (j + 1) * .04), (L * (k + 1) / segs, j * .04)])
            for j in range(n):
                j1 = (j + 1) % n
                mb.f((rings[-1][j], rings[-1][j1], tipv), [(L, j * .04), (L, (j + 1) * .04), (L * 1.05, (j + .5) * .04)])
                mb.f((rings[0][j1], rings[0][j], basev), [(0, (j + 1) * .04), (0, j * .04), (-.02, (j + .5) * .04)])


def tube20(mb, rec, lv, col=False):
    _tube_v19(mb, rec, lv, col)
    if col or not rec.get('staves') or rec.get('dead'):
        return
    n1 = len(mb.V)
    staves(mb, rec, lv)
    if hasattr(mb, 'own'):
        mb.own += [-1] * (n1 - len(mb.own)) + [rec['id']] * (len(mb.V) - n1)


ns['_tube_v19'] = ns['tube']
for _f in (staves,):
    ns[_f.__name__] = types.FunctionType(_f.__code__, ns, _f.__name__)
ns['tube'] = types.FunctionType(tube20.__code__, ns, 'tube', tube20.__defaults__)

# 主斷口的裂塊表（A 左端）：th 方位、span 角寬、ri／ro 內外半徑比、ext 伸出、dep 起點在斷面內的深度、out 外張、lift 抬升、
#   bias 尖端偏向、keep 開始收尖的位置、barkL 外側根部保留樹皮的比例、dark 側面裂縫深度
STAVES_A = [   # v020：薄（徑向厚 0.2–0.35 倍半徑）、窄（0.3–0.6 rad）、從根部就逐漸收薄（keep 0.15–0.25），分內外層
    dict(th=-1.95, span=.60, ri=.62, ro=.94, ext=.38, dep=.10, out=.05, lift=.05, bias=.6, keep=0.13, barkL=.45, dark=.35),   # 主長片：前上外層
    dict(th=2.75, span=.55, ri=.66, ro=.93, ext=.30, dep=.05, out=.07, lift=.09, bias=-.5, keep=0.15, barkL=.30, dark=.30),   # 主長片：上後外層
    dict(th=-.55, span=.55, ri=.40, ro=.72, ext=.34, dep=.15, out=.03, lift=.05, bias=.4, keep=0.17, barkL=0., dark=.42),     # 主長片：前下內層（從深處長出）
    dict(th=-1.40, span=.40, ri=.40, ro=.65, ext=.24, dep=.14, out=.03, lift=.04, bias=-.3, keep=0.15, barkL=0., dark=.45),   # 中：前側內層
    dict(th=-1.05, span=.45, ri=.12, ro=.42, ext=.20, dep=.20, out=.02, lift=.03, bias=-.3, keep=0.10, barkL=0., dark=.48),   # 中：木芯
    dict(th=1.90, span=.45, ri=.70, ro=.93, ext=.18, dep=.03, out=.06, lift=.07, bias=.5, keep=0.15, barkL=.60, dark=.30),    # 中：後側外層帶樹皮
    dict(th=-2.60, span=.40, ri=.35, ro=.62, ext=.16, dep=.12, out=.04, lift=.07, bias=.3, keep=0.13, barkL=0., dark=.50),    # 中：上前內層
    dict(th=.75, span=.40, ri=.66, ro=.92, ext=.13, dep=.02, out=.05, lift=.04, bias=-.4, keep=0.15, barkL=.50, dark=.30),    # 中：下後外層帶樹皮
    dict(th=-1.45, span=.30, ri=.72, ro=.92, ext=.08, dep=.01, out=.03, lift=.02, bias=.2, keep=0.10, barkL=.35, dark=.30),   # 短
    dict(th=-2.90, span=.28, ri=.10, ro=.35, ext=.07, dep=.09, out=.02, lift=.03, bias=-.2, keep=0.10, barkL=0., dark=.55),   # 短：木芯
    dict(th=1.20, span=.28, ri=.40, ro=.62, ext=.09, dep=.06, out=.03, lift=.03, bias=.3, keep=0.10, barkL=0., dark=.45),     # 短
    dict(th=2.20, span=.30, ri=.20, ro=.45, ext=.10, dep=.10, out=.03, lift=.05, bias=-.3, keep=0.10, barkL=0., dark=.50),    # 短：內層
]
ns['STAVES_A'] = STAVES_A


# 三、苔：前景主幹頂面連續苔毯，向兩側的覆蓋範圍沿長度起伏（低頻雜訊控制往側面延伸多少），不是等寬綠帶
# 四、地衣：雜訊式地衣再用中頻雜訊切成大小不同的斑；指定斑片半徑各自不同；內部加破碎（配合材質遮罩成為邊緣破碎的殼斑）
def LICHENW20(co):
    out = np.zeros(len(co))
    for q, (nm, fr, dv, R_) in enumerate(LICH):
        rec = next((x for x in RECS if x.get('name') == nm and not x.get('dead')), None)
        if rec is None:
            continue
        i = int(fr * (len(rec['P']) - 1))
        dv = np.array(dv, float)
        dv /= np.linalg.norm(dv)
        P0 = rec['P'][i]
        c = P0 + dv * rec['r'][i]
        cand = np.linalg.norm(co - P0, axis=1) < rec['r'][i] * 2.2
        if cand.any():
            v_ = co[cand] - P0
            c = co[cand][((v_ @ dv) / (np.linalg.norm(v_, axis=1) + 1e-9)).argmax()]
        R_ = R_ * (.75, 1.35, .95, 1.15, .65, 1.25, .85, 1.05, .70, 1.30, .90)[q % 11]
        dist = np.linalg.norm(co - c, axis=1)
        k = (dist < R_ * 1.8) & ((co - P0) @ dv > 0)
        if not k.any():
            continue
        q_ = co[k] - c
        ang = np.arctan2(q_[:, 2], q_[:, 0])
        ir = R_ * (1 + .34 * np.sin(ang * 3 + fr * 17) + .22 * np.sin(ang * 5 + fr * 5) + .15 * np.sin(co[k] @ np.array((61., 47., 53.))))
        out[k] = np.maximum(out[k], sm(ir - dist[k], 0, .020) * (.80 + .20 * np.sin(co[k] @ np.array((31., -27., 23.)) + q)))
    return out


ns['LICHENW'] = types.FunctionType(LICHENW20.__code__, ns, 'LICHENW')


# ================================================================== v021 追加
# 一、斷口裂片改為「沿主幹木紋往左撕開的扁薄木片」：
#     截面＝不規則扁楔形（外弧寬、徑向很薄；一側厚一側薄；內外緣頂點各自抖動）——不是圓形木刺。
#     根部寬厚，往末端寬度收到約 50%、厚度收到約 20%；末端不收成一點，而是參差的破碎平口（每個頂點各自縮回不同長度）。
#     方向沿主幹切線，幾乎不外張、不抬升（不再上下左右均勻放射）；起點深度各異，形成前後不同深度的層次。
def staves21(mb, rec, lv):
    for e, lst in (rec.get('staves') or {}).items():
        P = rec['P']
        c = np.array(P[0] if e == 0 else P[-1], float)
        Te = np.array(P[0] - P[2] if e == 0 else P[-1] - P[-3], float)
        Te /= np.linalg.norm(Te)
        Ti = -Te
        dn = np.array((0, 0, -1.0))
        Nn = dn - Ti * (Ti @ dn)
        Nn /= np.linalg.norm(Nn)
        Bn = np.cross(Ti, Nn)                       # A 左端：th 0＝下、π/2＝後（+y）、−π/2＝前（−y）、π＝上
        rr = float(rec['r'][0 if e == 0 else -1])
        se = 0.0 if e == 0 else float(rec['s'][-1])
        segs, na = (9, 6) if lv == 0 else ((5, 4) if lv == 1 else (2, 3))
        crk = mb.__dict__.setdefault('crk', {})
        for q, st in enumerate(lst):
            if lv == 2 and st['ext'] < .10:
                continue
            hj = lambda k: math.sin(q * 91.7 + k * 37.719 + st['th'] * 13.1) * .5 + .5
            L = st['dep'] + st['ext']
            thick = st['ro'] - st['ri']
            wd = st.get('wedge', .55)
            flip = (q % 2) == 1
            # 末端參差：每個寬度位置縮回的比例不同（−0.16～+0.06 倍長度），外、內緣同一位置一起縮（斷口有厚度）
            jag = [(-.075 if (j + q) % 2 else .0) + .05 * (hj(500 + j) - .5) for j in range(na)]   # 末端參差平口（只動最後一圈，高低交錯），不收成一點
            jag[int(hj(77) * (na - 1) + .5)] -= .035 * (st['ext'] > .15)                           # 長片：一角多斷掉一截
            rings, side_of = [], []
            for k in range(segs + 1):
                t = k / segs
                g = float(np.clip((t - st['keep']) / (1 - st['keep']), 0, 1))
                sp_ = st['span'] * (1 - .32 * g ** 1.1)
                ct = st['th'] + st['bias'] * st['span'] * .30 * g
                thk = thick * (1 - .80 * g)
                rdc = Nn * math.cos(ct) + Bn * math.sin(ct)
                cen_off = rdc * st['out'] * t * t + np.array((0, 0, st['lift'])) * t * t
                ring = []
                for side in ('o', 'i'):
                    for jj in range(na):
                        j = jj if side == 'o' else na - 1 - jj
                        u = j / (na - 1)
                        a = ct - sp_ / 2 + sp_ * u
                        d = Nn * math.cos(a) + Bn * math.sin(a)
                        a0, a1 = ct - sp_ / 2, ct + sp_ / 2
                        dch = (1 - u) * (Nn * math.cos(a0) + Bn * math.sin(a0)) + u * (Nn * math.cos(a1) + Bn * math.sin(a1))
                        d = d * .35 + dch * .65                               # 截面壓平：外弧往弦拉（扁片，不是圓殼）
                        ro_ = st['ro'] * (1 - .06 * g) * (1 + .05 * (hj(k * 7 + j) - .5))
                        wt = 1 - wd * (1 - u if flip else u)                 # 扁楔形：一側厚、一側薄
                        tk_ = thk * wt * (1 + .35 * (hj(k * 13 + j + 70) - .5))
                        rf = ro_ if side == 'o' else max(ro_ - tk_, .02)
                        along = L * t + (L * jag[j] if k == segs else 0.0)
                        p = c + Te * (-st['dep'] + along) + cen_off + d * rr * rf * XS(rec, se, a)
                        if side == 'o':
                            bk = along < st['barkL'] * L * (.70 + .6 * hj(200 + j))
                            fib = 0.0 if bk else 1.0
                            ck = 0.0 if bk else .10 * hj(300 + k)
                        else:
                            fib = 1.0
                            ck = st['dark'] * (.55 + .45 * hj(400 + k + j))
                        if j in (0, na - 1):
                            ck = max(ck, st['dark'] * .85)         # 兩側撕開的面較深
                        if k == segs:
                            ck = max(ck, st['dark'] * .5)
                        crk[len(mb.V)] = ck
                        ring.append(mb.v(p, fib=fib, kind=2))
                rings.append(ring)
            n = len(rings[0])
            for k in range(segs):
                a_, b_ = rings[k], rings[k + 1]
                for j in range(n):
                    j1 = (j + 1) % n
                    mb.f((a_[j], a_[j1], b_[j1], b_[j]), [(L * k / segs, j * .04), (L * k / segs, (j + 1) * .04), (L * (k + 1) / segs, (j + 1) * .04), (L * (k + 1) / segs, j * .04)])
            # 末端：參差平口（扇形接到末圈中心，平面而非尖錐）
            cend = np.mean([mb.V[i] for i in rings[-1]], axis=0)
            crk[len(mb.V)] = st['dark'] * .6
            tipv = mb.v(cend, fib=1.0, kind=2)
            cb = np.mean([mb.V[i] for i in rings[0]], axis=0)
            crk[len(mb.V)] = st['dark']
            basev = mb.v(cb - Te * .01, fib=1.0, kind=2)
            for j in range(n):
                j1 = (j + 1) % n
                mb.f((rings[-1][j], rings[-1][j1], tipv), [(L, j * .04), (L, (j + 1) * .04), (L * 1.01, (j + .5) * .04)])
                mb.f((rings[0][j1], rings[0][j], basev), [(0, (j + 1) * .04), (0, j * .04), (-.02, (j + .5) * .04)])


ns['staves'] = types.FunctionType(staves21.__code__, ns, 'staves')

# 裂片表（A 左端）：th 方位、span 角寬、ri／ro 內外半徑比（ro−ri＝厚度，0.10–0.22 倍半徑＝扁）、ext 伸出、dep 起點在斷面內的深度、
#   out／lift 幾乎為 0（沿主幹）、bias 末端偏向、keep 開始收薄的位置、barkL 外側根部保留樹皮比例、dark 裂縫深度、wedge 楔形程度
STAVES_A = [
    # 少數長裂片：構成輪廓（外層、帶樹皮）
    dict(th=-2.10, span=.80, ri=.79, ro=.95, ext=.40, dep=.06, out=.010, lift=.025, bias=.35, keep=.30, barkL=.42, dark=.35, wedge=.60),   # 長：前上
    dict(th=2.70, span=.70, ri=.80, ro=.93, ext=.31, dep=.02, out=.008, lift=.030, bias=-.30, keep=.32, barkL=.30, dark=.32, wedge=.50),  # 長：後上
    dict(th=-.70, span=.95, ri=.73, ro=.90, ext=.33, dep=.13, out=.000, lift=.010, bias=.15, keep=.42, barkL=.15, dark=.42, wedge=.45),   # 長：前下，從較深處長出
    # 中裂片：外層與內層交錯，起點深度不同
    dict(th=-1.45, span=.55, ri=.50, ro=.70, ext=.21, dep=.17, out=.000, lift=.010, bias=-.30, keep=.28, barkL=0., dark=.48, wedge=.65),  # 中：內層
    dict(th=1.85, span=.62, ri=.80, ro=.93, ext=.17, dep=.03, out=.006, lift=.015, bias=.35, keep=.28, barkL=.55, dark=.30, wedge=.50),   # 中：後側帶樹皮
    dict(th=-2.70, span=.50, ri=.45, ro=.64, ext=.16, dep=.11, out=.000, lift=.012, bias=.30, keep=.25, barkL=0., dark=.50, wedge=.60),   # 中：上前內層
    dict(th=.55, span=.58, ri=.80, ro=.92, ext=.13, dep=.02, out=.005, lift=.000, bias=-.30, keep=.25, barkL=.45, dark=.30, wedge=.55),   # 中：下後帶樹皮
    dict(th=-1.62, span=.42, ri=.82, ro=.95, ext=.19, dep=.04, out=.004, lift=.008, bias=.30, keep=.30, barkL=.50, dark=.32, wedge=.55),  # 中：正前外層
    dict(th=3.10, span=.50, ri=.81, ro=.94, ext=.14, dep=.03, out=.004, lift=.012, bias=-.25, keep=.28, barkL=.40, dark=.30, wedge=.50),  # 中：正上外層
    dict(th=-.05, span=.55, ri=.56, ro=.74, ext=.15, dep=.12, out=.000, lift=.000, bias=.25, keep=.28, barkL=0., dark=.48, wedge=.60),    # 中：下方內層
    # 短裂片：內層、穿插在長片之間（從斷面深處冒出，不貼在樹皮表面）
    dict(th=1.20, span=.44, ri=.42, ro=.60, ext=.08, dep=.07, out=.000, lift=.000, bias=.30, keep=.20, barkL=0., dark=.45, wedge=.55),
    dict(th=-.95, span=.40, ri=.28, ro=.44, ext=.07, dep=.09, out=.000, lift=.004, bias=-.30, keep=.20, barkL=0., dark=.55, wedge=.60),
    dict(th=2.30, span=.40, ri=.40, ro=.58, ext=.06, dep=.06, out=.000, lift=.006, bias=.20, keep=.20, barkL=0., dark=.50, wedge=.55),
    dict(th=-2.25, span=.38, ri=.18, ro=.34, ext=.09, dep=.10, out=.000, lift=.004, bias=.20, keep=.20, barkL=0., dark=.55, wedge=.60),
]
ns['STAVES_A'] = STAVES_A


# 二、地衣：幾塊清楚可辨的灰白斑片（大小不一），半徑恢復 v019 的 1.5 倍並按片放大縮小；斑內部只輕微破碎（不淡到看不見）
def LICHENW21(co):
    out = np.zeros(len(co))
    for q, (nm, fr, dv, R_) in enumerate(LICH):
        rec = next((x for x in RECS if x.get('name') == nm and not x.get('dead')), None)
        if rec is None:
            continue
        i = int(fr * (len(rec['P']) - 1))
        dv = np.array(dv, float)
        dv /= np.linalg.norm(dv)
        P0 = rec['P'][i]
        c = P0 + dv * rec['r'][i]
        cand = np.linalg.norm(co - P0, axis=1) < rec['r'][i] * 2.2
        if cand.any():
            v_ = co[cand] - P0
            c = co[cand][((v_ @ dv) / (np.linalg.norm(v_, axis=1) + 1e-9)).argmax()]
        R_ = R_ * 1.15 * (.70, 1.45, .95, 1.20, .60, 1.35, .85, 1.10, .65, 1.30, .90)[q % 11]
        dist = np.linalg.norm(co - c, axis=1)
        k = (dist < R_ * 1.8) & ((co - P0) @ dv > 0)
        if not k.any():
            continue
        q_ = co[k] - c
        ang = np.arctan2(q_[:, 2], q_[:, 0])
        ir = R_ * (1 + .30 * np.sin(ang * 3 + fr * 17) + .20 * np.sin(ang * 5 + fr * 5) + .12 * np.sin(co[k] @ np.array((61., 47., 53.))))
        out[k] = np.maximum(out[k], sm(ir - dist[k], 0, .018) * (.86 + .14 * np.sin(co[k] @ np.array((83., -71., 59.)) + q)))
    return out


ns['LICHENW'] = types.FunctionType(LICHENW21.__code__, ns, 'LICHENW')


# 三、苔毯邊緣：材質裡對苔層（R）做與地衣同樣的遮罩銳化（另一個縮放／偏移，花紋不同）：
#     w' = clamp((R × 1.3 ＋ mask) × 6 − 6.6)。苔殼內部 R＝1 → 全覆蓋；苔殼邊緣與樹皮上的低權重 → 被遮罩切成破碎、逐漸消退的邊。
_layer_mat20 = ns['layer_mat']


def layer_mat21():
    m = _layer_mat20()
    if m.get('v021_moss_mask'):
        return m
    N, Lk = m.node_tree.nodes, m.node_tree.links
    sp = next(n for n in N if n.bl_idname == 'ShaderNodeSeparateColor')
    r_out = sp.outputs[0]
    dst = [l.to_socket for l in r_out.links]
    uv = next(n for n in N if n.bl_idname == 'ShaderNodeUVMap' and n.uv_map == 'UVMap')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.3, 1.3, 1)
    mp.inputs['Location'].default_value = (.37, .71, 0)
    Lk.new(uv.outputs['UV'], mp.inputs['Vector'])
    t = N.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(ROOT + '/art/exports/d2-logs-b/DR09_Shared/Textures/DR09_LichenMask_v019.png', check_existing=True)
    t.image.colorspace_settings.name = 'Non-Color'
    Lk.new(mp.outputs[0], t.inputs['Vector'])
    a = N.new('ShaderNodeMath')
    a.operation = 'MULTIPLY_ADD'
    Lk.new(r_out, a.inputs[0])
    a.inputs[1].default_value = 1.3
    Lk.new(t.outputs['Color'], a.inputs[2])
    b = N.new('ShaderNodeMath')
    b.operation = 'MULTIPLY_ADD'
    b.use_clamp = True
    Lk.new(a.outputs[0], b.inputs[0])
    b.inputs[1].default_value = 6.0
    b.inputs[2].default_value = -6.1
    for s_ in dst:
        Lk.new(b.outputs[0], s_)
    m['v021_moss_mask'] = True
    return m


ns['layer_mat'] = types.FunctionType(layer_mat21.__code__, ns, 'layer_mat')
ns['_layer_mat20'] = _layer_mat20


_cr20 = ns['contact_report']


def contact_report21():
    out = _cr20()
    print('BRANCH_IDS', [(x['id'], x.get('name')) for x in RECS if x['kind'] == 'branch' and not x.get('dead')])
    return out


ns['contact_report'] = types.FunctionType(contact_report21.__code__, ns, 'contact_report')
ns['_cr20'] = _cr20


# ================================================================== v022 追加
# 二、左端斷口裂片（v021 像平行堆疊的厚木板）→ 根部厚、末端薄且不規則尖裂的木片：
#   * 厚度：根部 0.20–0.34 倍半徑，往末端收到約 12%（不是等厚板條）；寬度收到約 45%；截面扁楔形（一側厚一側薄）、外弧壓平。
#   * 末端：每個寬度位置縮回的長度不同 → 2～3 個長短不一的尖齒；中間一道深的縱向劈裂（V 形缺口往根部延伸，裂縫深色）。
#     縮回量沿長度漸進（t²，單調不折返），尖齒順木紋、不是方形平口。
#   * 輕微扭曲：截面繞自身中心線旋轉（每片方向、角度不同，0.15–0.45 rad）。
#   * 方向：沿主幹，再各自偏 2–6°（往外、往內、上、下、側向都有）＋輕微彎；不平行、也不從同一點放射。
#   * 從主幹內部長出：外層片根部 ro≈1.0（與樹皮面齊平）、起點在斷面內 dep 0.06–0.18 m，根部埋在主幹裡。
def staves22(mb, rec, lv):
    for e, lst in (rec.get('staves') or {}).items():
        P = rec['P']
        c = np.array(P[0] if e == 0 else P[-1], float)
        Te = np.array(P[0] - P[2] if e == 0 else P[-1] - P[-3], float)
        Te /= np.linalg.norm(Te)
        Ti = -Te
        dn = np.array((0, 0, -1.0))
        Nn = dn - Ti * (Ti @ dn)
        Nn /= np.linalg.norm(Nn)
        Bn = np.cross(Ti, Nn)                       # A 左端：th 0＝下、π/2＝後（+y）、−π/2＝前（−y）、π＝上
        rr = float(rec['r'][0 if e == 0 else -1])
        se = 0.0 if e == 0 else float(rec['s'][-1])
        segs, na = (10, 7) if lv == 0 else ((5, 4) if lv == 1 else (3, 3))
        crk = mb.__dict__.setdefault('crk', {})
        for q, st in enumerate(lst):
            if lv == 2 and st['ext'] < .12:
                continue
            hj = lambda k: math.sin(q * 91.7 + k * 37.719 + st['th'] * 13.1) * .5 + .5
            L = st['dep'] + st['ext']
            wd = st.get('wedge', .5)
            flip = (q % 2) == 1
            # 末端縮回（倍 L）：先全部縮一些，再挑 1～2 個尖齒（不縮）、中間一道深劈裂
            jag = [-(.07 + .15 * hj(500 + j)) for j in range(na)]
            for tp in st.get('teeth', (0, )):
                jag[min(na - 1, max(0, int(tp * (na - 1) + .5)))] = -.02 * hj(77)
            jag = [.5 * jag[j] + .25 * (jag[max(j - 1, 0)] + jag[min(j + 1, na - 1)]) for j in range(na)]   # 尖齒兩側漸縮（不是單點細針）
            sp_j = st.get('split', .5)
            js = min(na - 2, max(1, int(sp_j * (na - 1) + .5)))
            jag[js] = -st.get('splitd', .42)
            ct0 = st['th']
            rd0 = Nn * math.cos(ct0) + Bn * math.sin(ct0)
            tg0 = -Nn * math.sin(ct0) + Bn * math.cos(ct0)        # 截面切向（繞主幹）
            dev = rd0 * st['out'] + tg0 * st.get('sw', 0.0) + np.array((0, 0, st['lift']))
            rings = []
            for k in range(segs + 1):
                t = k / segs
                g = float(np.clip((t - st['keep']) / (1 - st['keep']), 0, 1))
                sp_ = st['span'] * (1 - .55 * g ** 1.1)
                ct = ct0 + st['bias'] * st['span'] * .30 * g
                thk = (st['ro'] - st['ri']) * (1 - .88 * g ** .9)
                ro_k = st['ro'] - .10 * g * (st['ro'] - st['ri'])
                a0, a1 = ct - sp_ / 2, ct + sp_ / 2
                e0 = Nn * math.cos(a0) + Bn * math.sin(a0)
                e1 = Nn * math.cos(a1) + Bn * math.sin(a1)
                pts, meta = [], []
                for side in ('o', 'i'):
                    for jj in range(na):
                        j = jj if side == 'o' else na - 1 - jj
                        u = j / (na - 1)
                        a = a0 + sp_ * u
                        d = (Nn * math.cos(a) + Bn * math.sin(a)) * .35 + ((1 - u) * e0 + u * e1) * .65
                        ro_ = ro_k * (1 + .05 * (hj(k * 7 + j) - .5))
                        wt = 1 - wd * (1 - u if flip else u)
                        tk_ = thk * wt * (1 + .30 * (hj(k * 13 + j + 70) - .5))
                        rf = ro_ if side == 'o' else max(ro_ - tk_, .02)
                        along = L * (t + jag[j] * t * t)                    # 單調（不折返）
                        tt = along / L
                        p = c + Te * (-st['dep'] + along) + dev * along + np.array((0, 0, st.get('bend', 0.0))) * tt * tt * L + d * rr * rf * XS(rec, se, a)
                        if p[2] < .012:                                   # 不穿到地面下（貼地的裂片壓平在地上）
                            p = p.copy()
                            p[2] = .012 + .004 * hj(k + j)
                        pts.append(p)
                        meta.append((side, j, tt))
                # 輕微扭曲：截面繞自身中心旋轉
                cen = np.mean(pts, axis=0)
                phi = st.get('tw', 0.0) * t ** 1.3
                if phi:
                    ax = Te + dev
                    ax /= np.linalg.norm(ax)
                    cph, sph = math.cos(phi), math.sin(phi)
                    pts = [cen + (v - cen) * cph + np.cross(ax, v - cen) * sph + ax * (ax @ (v - cen)) * (1 - cph) for v in pts]
                ring = []
                for p, (side, j, tt) in zip(pts, meta):
                    if side == 'o':
                        bk = tt * L < st['barkL'] * L * (.70 + .6 * hj(200 + j))
                        fib = 0.0 if bk else 1.0
                        ck = 0.0 if bk else .10 * hj(300 + k)
                    else:
                        fib = 1.0
                        ck = st['dark'] * (.55 + .45 * hj(400 + k + j))
                    if j in (0, na - 1):
                        ck = max(ck, st['dark'] * .85)            # 兩側撕開的面較深
                    if j == js and t > .45:
                        ck = max(ck, st['dark'] * 1.4)            # 縱向劈裂：深色裂縫
                    crk[len(mb.V)] = min(ck, 1.0)
                    ring.append(mb.v(p, fib=fib, kind=2))
                rings.append(ring)
            n = len(rings[0])
            for k in range(segs):
                a_, b_ = rings[k], rings[k + 1]
                for j in range(n):
                    j1 = (j + 1) % n
                    mb.f((a_[j], a_[j1], b_[j1], b_[j]), [(L * k / segs, j * .04), (L * k / segs, (j + 1) * .04), (L * (k + 1) / segs, (j + 1) * .04), (L * (k + 1) / segs, j * .04)])
            # 末端：外、內緣在同一寬度位置直接相接（薄邊），不另開平口
            last = rings[-1]
            for j in range(na - 1):
                o0, o1 = last[j], last[j + 1]
                i0, i1 = last[2 * na - 1 - j], last[2 * na - 2 - j]
                mb.f((o1, o0, i0, i1), [(L, j * .04), (L, (j + 1) * .04), (L * 1.01, (j + 1) * .04), (L * 1.01, j * .04)])
            cb = np.mean([mb.V[i] for i in rings[0]], axis=0)
            crk[len(mb.V)] = st['dark']
            basev = mb.v(cb - Te * .01, fib=1.0, kind=2)
            for j in range(n):
                j1 = (j + 1) % n
                mb.f((rings[0][j1], rings[0][j], basev), [(0, (j + 1) * .04), (0, j * .04), (-.02, (j + .5) * .04)])


ns['staves'] = types.FunctionType(staves22.__code__, ns, 'staves')

# 裂片表（A 左端）：out／sw／lift＝各自偏離主幹方向（倍長度，小角度，正負都有）、bend＝末段上彎／下彎、tw＝扭曲、
#   teeth＝尖齒在寬度上的位置（0–1）、split／splitd＝縱向劈裂位置與深度（倍長度）
STAVES_A = [
    # 主要長裂片：建立輪廓（外層、根部與樹皮齊平）
    dict(th=-2.15, span=.95, ri=.70, ro=.95, ext=.40, dep=0.18, out=.030, sw=.035, lift=.050, bend=.02, bias=.30, keep=.12, barkL=.38, dark=.38, wedge=.55, tw=.30, teeth=(.15, .80), split=.50, splitd=.40),   # 長：前上
    dict(th=2.65, span=.85, ri=.74, ro=.95, ext=.30, dep=0.14, out=.020, sw=-.040, lift=.065, bend=.03, bias=-.25, keep=.12, barkL=.30, dark=.34, wedge=.50, tw=-.35, teeth=(.70,), split=.35, splitd=.36),     # 長：後上
    dict(th=-.80, span=.95, ri=.66, ro=.94, ext=.34, dep=0.22, out=-.020, sw=.050, lift=.060, bend=.0, bias=.20, keep=.15, barkL=.15, dark=.42, wedge=.45, tw=.40, teeth=(.10, .55), split=.80, splitd=.34),  # 長：前下（略往內收）
    # 中裂片
    dict(th=-1.45, span=.60, ri=.44, ro=.70, ext=.22, dep=0.24, out=-.030, sw=-.030, lift=.030, bend=0., bias=-.30, keep=.10, barkL=0., dark=.50, wedge=.60, tw=-.25, teeth=(.30,), split=.70, splitd=.30),    # 中：內層
    dict(th=1.85, span=.70, ri=.74, ro=.95, ext=.17, dep=0.13, out=.045, sw=.030, lift=.020, bend=.02, bias=.35, keep=.10, barkL=.55, dark=.30, wedge=.50, tw=.30, teeth=(.85,), split=.40, splitd=.30),      # 中：後側帶樹皮
    dict(th=-2.75, span=.55, ri=.40, ro=.64, ext=.18, dep=0.19, out=-.015, sw=.045, lift=.040, bend=.01, bias=.30, keep=.10, barkL=0., dark=.52, wedge=.60, tw=.45, teeth=(.20, .75), split=.50, splitd=.28),  # 中：上前內層
    dict(th=.50, span=.66, ri=.76, ro=.95, ext=.15, dep=0.12, out=.025, sw=-.050, lift=-.020, bend=-.01, bias=-.30, keep=.10, barkL=.45, dark=.30, wedge=.55, tw=-.30, teeth=(.60,), split=.25, splitd=.28),   # 中：下後帶樹皮
    # 短裂片：插在長片之間，不同深度
    dict(th=-1.70, span=.45, ri=.76, ro=.95, ext=.10, dep=0.12, out=.035, sw=.020, lift=.015, bend=0., bias=.30, keep=.10, barkL=.50, dark=.32, wedge=.55, tw=.20, teeth=(.40,), split=.75, splitd=.25),
    dict(th=3.10, span=.50, ri=.70, ro=.94, ext=.09, dep=0.13, out=.030, sw=-.025, lift=.035, bend=0., bias=-.25, keep=.10, barkL=.40, dark=.30, wedge=.50, tw=-.25, teeth=(.20,), split=.65, splitd=.25),
    dict(th=1.20, span=.48, ri=.36, ro=.60, ext=.08, dep=0.16, out=-.020, sw=.030, lift=.010, bend=0., bias=.30, keep=.10, barkL=0., dark=.48, wedge=.55, tw=.30, teeth=(.70,), split=.30, splitd=.25),
    dict(th=-.05, span=.55, ri=.50, ro=.74, ext=.12, dep=0.18, out=-.010, sw=-.040, lift=-.015, bend=0., bias=.25, keep=.10, barkL=0., dark=.48, wedge=.60, tw=-.35, teeth=(.25, .85), split=.55, splitd=.28),
    dict(th=-2.30, span=.42, ri=.16, ro=.36, ext=.07, dep=0.18, out=.000, sw=.030, lift=.020, bend=0., bias=.20, keep=.10, barkL=0., dark=.55, wedge=.60, tw=.25, teeth=(.50,), split=.20, splitd=.22),
]
ns['STAVES_A'] = STAVES_A

# 三、地面以下壓平：枝端蓋或下陷的木頭最多埋入 1.2 cm（v022 前 B3 起點、主拱左腳端蓋到 −8 cm，讓正面剪影的底線往下移）
_MBv0 = ns['MB'].v


def _mbv22(self, p, fib=0.0, mk=0.0, kind=0):
    if p[2] < -.012:
        p = (p[0], p[1], -.012)
    return _MBv0(self, p, fib, mk, kind)


ns['MB'].v = _mbv22


# ================================================================== v023 追加
# 四、左端斷口：三片主要裂片沿木紋往左延長（主幹左端收短 0.12 m 補回）、變薄；中、短裂片長度與深度錯開
_SA = [dict(d) for d in ns['STAVES_A']]
for _d, (_ext, _ri, _tw) in zip(_SA[:3], ((.58, .80, .30), (.44, .82, -.40), (.46, .76, .45))):
    _d.update(ext=_ext, ri=_ri, tw=_tw, keep=.08)
_SA[0].update(teeth=(.20, .70), split=.45, splitd=.34)
_SA[1].update(teeth=(.80,), split=.30, splitd=.30)
_SA[2].update(teeth=(.15, .60), split=.85, splitd=.28)
for _d, _e in zip(_SA[3:7], (.30, .20, .26, .13)):                       # 中裂片：長短錯開
    _d.update(ext=_e)
ns['STAVES_A'] = _SA

# 三、右上主枝 T1 折斷端：不對稱撕裂分叉——上側一長片往前上方、側下一片較短往外，其餘短而參差（受 1.1 m 限高，不往上翹）
ns['STAVES_T1'] = [   # 裂片要有重量：徑向厚 0.55–0.8 倍半徑、寬 1.3–1.6 rad，前 35% 不收薄
    dict(th=2.85, span=1.60, ri=.20, ro=.96, ext=.30, dep=.10, out=.020, sw=.030, lift=-.05, bend=.0, bias=.25, keep=.35, barkL=.55, dark=.36, wedge=.45, tw=.30, teeth=(.20, .70), split=.50, splitd=.30),
    dict(th=-1.25, span=1.35, ri=.25, ro=.96, ext=.17, dep=.08, out=.070, sw=-.030, lift=-.03, bend=-.02, bias=-.30, keep=.30, barkL=.45, dark=.36, wedge=.45, tw=-.35, teeth=(.65,), split=.35, splitd=.26),
    dict(th=1.30, span=1.10, ri=.30, ro=.96, ext=.09, dep=.07, out=.030, sw=.030, lift=-.02, bend=.0, bias=.25, keep=.30, barkL=.40, dark=.34, wedge=.50, tw=.25, teeth=(.40,), split=.70, splitd=.22),
    dict(th=.05, span=1.20, ri=.05, ro=.60, ext=.06, dep=.08, out=-.010, sw=.020, lift=-.02, bend=.0, bias=.20, keep=.30, barkL=0., dark=.50, wedge=.55, tw=-.20, teeth=(.30, .80), split=.55, splitd=.20),
]

# 五、地衣：主幹前側三塊醒目斑片（大小、高低不同）＋拱枝與右側粗枝少量；斑片內有樹皮孔洞，不是連續等寬白帶
ns['LICH'] = [('A', .24, (0, -1, -.35), .110), ('A', .55, (0, -.8, .40), .085), ('A', .84, (0, -1, -.05), .070),
              ('B', .14, (0, -1, .20), .075), ('B', .40, (0, -.7, .70), .070), ('B', .70, (0, -1, .25), .080),
              ('B3', .50, (0, -1, .55), .065), ('T1', .55, (0, -.8, .60), .075), ('T2', .50, (0, -1, .40), .055), ('R1', .40, (0, -1, .50), .060)]
_LW22 = ns['LICHENW']


def LICHENW23(co):
    w = _LW22(co)
    h = np.sin(co @ np.array((97., -83., 71.))) * np.sin(co @ np.array((-53., 89., 67.))) + .45 * np.sin(co @ np.array((31., 29., -41.)))
    return w * (.15 + .85 * sm(h, -.55, -.10))                                # 斑片內樹皮孔洞


ns['LICHENW'] = types.FunctionType(LICHENW23.__code__, ns, 'LICHENW')
ns['_LW22'] = _LW22


# ================================================================== v024 追加
# 診斷：DR9PARTS=1 時，網格加一個點屬性 own（構件 id，-1＝苔層／卡片等），方便逐件單獨顯示；正式輸出不加
_HF0 = ns['hidden_faces']


def _hf24(o, mb):
    if os.environ.get('DR9PARTS') and hasattr(mb, 'own'):
        own = list(mb.own) + [-1] * (len(o.data.vertices) - len(mb.own))
        at = o.data.attributes.new('own', 'INT', 'POINT')
        at.data.foreach_set('value', own[:len(o.data.vertices)])
    return _HF0(o, mb)


ns['hidden_faces'] = _hf24

# 三、左端斷口重建：參考的破口輪廓是「上緣往下斜、下緣往上斜，在中間高度收成參差的尖端」（不是一排平行往左的木板）。
#   核心裂片（內層、最長）從斷面中段伸出；外層裂片從上、下、前、後緣往中心收（out 為負），越外越短；
#   各片厚度、楔形、扭曲、起點深度都不同；根部埋在主幹內（dep），尖端薄碎。
_K = dict(bend=0., keep=.20, barkL=0., dark=.46, sw=0.)
ns['STAVES_A'] = [
    # 核心長片（內層）
    dict(_K, th=-1.90, span=.95, ri=.10, ro=.62, ext=.46, dep=.22, out=-.06, lift=.00, bias=.25, wedge=.70, tw=.45, teeth=(.25, .70), split=.50, splitd=.34),
    dict(_K, th=2.30, span=.85, ri=.15, ro=.58, ext=.38, dep=.16, out=-.12, lift=-.02, bias=-.30, wedge=.35, tw=-.55, teeth=(.60,), split=.30, splitd=.30),
    dict(_K, th=-.45, span=.80, ri=.12, ro=.60, ext=.32, dep=.26, out=-.14, lift=.04, bias=.30, wedge=.60, tw=.35, teeth=(.20, .85), split=.65, splitd=.26),
    # 外層：往中心收、越外越短
    dict(_K, th=3.05, span=.95, ri=.66, ro=.95, ext=.28, dep=.08, out=-.42, lift=.0, bias=.30, barkL=.40, dark=.34, wedge=.50, tw=.40, teeth=(.30,), split=.70, splitd=.30, keep=.12),
    dict(_K, th=-2.45, span=.80, ri=.72, ro=.95, ext=.24, dep=.12, out=-.36, lift=.0, bias=-.25, barkL=.45, dark=.34, wedge=.65, tw=-.35, teeth=(.75,), split=.40, splitd=.28, keep=.12),
    dict(_K, th=1.95, span=.75, ri=.60, ro=.95, ext=.20, dep=.05, out=-.30, lift=.0, bias=.30, barkL=.50, dark=.32, wedge=.40, tw=.50, teeth=(.20, .65), split=.85, splitd=.24, keep=.12),
    dict(_K, th=-1.25, span=.70, ri=.74, ro=.95, ext=.17, dep=.10, out=-.26, lift=.0, bias=.25, barkL=.35, dark=.34, wedge=.55, tw=.30, teeth=(.50,), split=.25, splitd=.24, keep=.12),
    dict(_K, th=.05, span=.90, ri=.70, ro=.95, ext=.21, dep=.07, out=-.34, lift=.0, bias=-.30, barkL=.40, dark=.34, wedge=.45, tw=-.45, teeth=(.35, .80), split=.55, splitd=.26, keep=.12),
    dict(_K, th=.85, span=.60, ri=.62, ro=.92, ext=.12, dep=.12, out=-.20, lift=.0, bias=.25, barkL=.45, dark=.36, wedge=.60, tw=.35, teeth=(.60,), split=.30, splitd=.22, keep=.12),
    dict(_K, th=-.85, span=.55, ri=.76, ro=.95, ext=.10, dep=.06, out=-.18, lift=.0, bias=-.25, barkL=.50, dark=.34, wedge=.50, tw=-.30, teeth=(.40,), split=.70, splitd=.22, keep=.12),
    # 短碎片（不同深度）
    dict(_K, th=1.30, span=.45, ri=.30, ro=.55, ext=.07, dep=.18, out=-.10, lift=.0, bias=.20, wedge=.60, tw=.40, teeth=(.50,), split=.30, splitd=.20),
    dict(_K, th=-2.95, span=.40, ri=.35, ro=.62, ext=.09, dep=.14, out=-.12, lift=.0, bias=-.20, wedge=.55, tw=-.40, teeth=(.30,), split=.70, splitd=.20),
]


# v024 二、T1 折斷端：粗端保留厚度，斷面為參差撕裂（上側一片稍長往右上、其餘短而厚，長短錯落），不收成尖棒；受 1.1 m 限高
ns['STAVES_T1'] = [
    dict(th=2.70, span=1.30, ri=.25, ro=.97, ext=.15, dep=.06, out=.040, sw=.030, lift=.04, bend=.0, bias=.25, keep=.45, barkL=.50, dark=.36, wedge=.40, tw=.30, teeth=(.25, .70), split=.50, splitd=.30),
    dict(th=-1.35, span=1.25, ri=.30, ro=.97, ext=.10, dep=.05, out=.080, sw=-.030, lift=-.03, bend=-.02, bias=-.30, keep=.40, barkL=.45, dark=.36, wedge=.45, tw=-.35, teeth=(.60,), split=.35, splitd=.26),
    dict(th=1.20, span=1.05, ri=.30, ro=.97, ext=.07, dep=.04, out=.050, sw=.030, lift=.0, bend=.0, bias=.25, keep=.40, barkL=.40, dark=.34, wedge=.50, tw=.25, teeth=(.40,), split=.70, splitd=.22),
    dict(th=.15, span=1.10, ri=.20, ro=.97, ext=.05, dep=.03, out=.030, sw=.020, lift=-.02, bend=.0, bias=.20, keep=.45, barkL=.30, dark=.40, wedge=.55, tw=-.20, teeth=(.30, .80), split=.55, splitd=.20),
    dict(th=-2.60, span=.90, ri=.05, ro=.55, ext=.04, dep=.10, out=.0, sw=.010, lift=.0, bend=.0, bias=.0, keep=.45, barkL=0., dark=.55, wedge=.60, tw=.10, teeth=(.50,), split=.0, splitd=.0),
]


# v025 一、左端斷口：少數主要長裂片＋少量次要裂片（取代 v024 的 12 片收攏碎片）
#   參考正面：裸木上緣跟著主幹頂面往左延伸到左端，下半部較短而參差；裸木與樹皮交接在端面往右約 0.1–0.15 m。
#   主要長裂片 ro≈1.0（外面貼齊／略蓋過樹皮）、dep 0.10–0.16（埋入主幹，交接往右退）、out≈0（不往中心收）。
#   th：0＝下、π/2＝後、−π/2＝前、π＝上。
_K25 = dict(bend=0., sw=0., dark=.42)
ns['STAVES_A'] = [   # v025：主要長裂片收窄（不是寬板）、縱向深劈裂；片與片之間留縫，看得到端面深度
    # 主要長裂片（上緣沿主幹頂面往左）
    dict(_K25, th=2.95, span=.62, ri=.45, ro=1.00, dep=.16, ext=.33, out=.02, lift=.02, sw=.02, keep=.35, bias=.20, barkL=.30, wedge=.55, tw=.55, teeth=(.30,), split=.50, splitd=.42),      # 上
    dict(_K25, th=2.20, span=.58, ri=.35, ro=1.00, dep=.12, ext=.27, out=.04, lift=.01, sw=.03, keep=.35, bias=-.20, barkL=.25, wedge=.60, tw=-.45, teeth=(.65,), split=.40, splitd=.40),     # 上後
    dict(_K25, th=-2.45, span=.64, ri=.30, ro=1.00, dep=.10, ext=.38, out=.01, lift=-.01, sw=-.02, keep=.35, bias=-.25, barkL=.20, wedge=.60, tw=-.60, teeth=(.70,), split=.35, splitd=.44),  # 上前：最長
    dict(_K25, th=-1.65, span=.60, ri=.12, ro=.98, dep=.24, ext=.28, out=.06, lift=.0, keep=.30, bias=.25, barkL=0., dark=.52, wedge=.65, tw=.50, teeth=(.25, .80), split=.50, splitd=.42),   # 前中：內層深裂
    # 次要裂片（下半部較短、參差）
    dict(_K25, th=-.85, span=.50, ri=.45, ro=.98, dep=.06, ext=.17, out=.04, lift=.05, keep=.35, bias=.20, barkL=.35, wedge=.55, tw=.35, teeth=(.40,), split=.60, splitd=.34),
    dict(_K25, th=1.45, span=.55, ri=.42, ro=.98, dep=.08, ext=.21, out=.06, lift=.0, keep=.30, bias=-.20, barkL=.40, wedge=.55, tw=-.35, teeth=(.50,), split=.30, splitd=.32),
    dict(_K25, th=.20, span=.55, ri=.50, ro=.97, dep=.05, ext=.10, out=.02, lift=.02, keep=.30, bias=.20, barkL=.40, wedge=.50, tw=.25, teeth=(.35, .80), split=.60, splitd=.26),
    dict(_K25, th=-3.10, span=.40, ri=.10, ro=.50, dep=.20, ext=.12, out=.0, lift=.0, keep=.35, bias=0., barkL=0., dark=.55, wedge=.55, tw=.25, teeth=(.50,), split=.40, splitd=.25),
]

# v025 二、T1 端部：不對稱長撕裂口——上側一長裂片往右上（外側樹皮、內側裸木），側下一片中長，其餘短齒；斜撕裂面
ns['STAVES_T1'] = [
    dict(th=2.85, span=1.65, ri=.35, ro=1.00, ext=.21, dep=.08, out=.020, sw=.030, lift=.04, bend=.0, bias=.25, keep=.50, barkL=.45, dark=.38, wedge=.45, tw=.35, teeth=(.30,), split=.55, splitd=.30),
    dict(th=-1.45, span=1.10, ri=.30, ro=.98, ext=.17, dep=.05, out=.050, sw=-.030, lift=.02, bend=.0, bias=-.30, keep=.35, barkL=.40, dark=.36, wedge=.50, tw=-.35, teeth=(.60,), split=.35, splitd=.26),
    dict(th=1.25, span=.95, ri=.35, ro=.97, ext=.07, dep=.04, out=.040, sw=.030, lift=.0, bend=.0, bias=.25, keep=.40, barkL=.35, dark=.34, wedge=.50, tw=.25, teeth=(.40,), split=.70, splitd=.22),
    dict(th=.10, span=1.00, ri=.25, ro=.97, ext=.04, dep=.03, out=.030, sw=.020, lift=-.02, bend=.0, bias=.20, keep=.45, barkL=.30, dark=.40, wedge=.55, tw=-.20, teeth=(.30, .80), split=.55, splitd=.20),
    dict(th=-2.50, span=.80, ri=.05, ro=.55, ext=.05, dep=.10, out=.0, sw=.010, lift=.03, bend=.0, bias=.0, keep=.45, barkL=0., dark=.55, wedge=.60, tw=.10, teeth=(.50,), split=.0, splitd=.0),
]


# ======================================================================== v026
# 比例：平面等比收 0.883（x）、0.93（y）；其餘構件高度 ×0.90（參考同寬換算後，主體高度約為 v025 設計的 0.9 倍）；半徑 ×0.94
ns['SX26'], ns['SY26'], ns['SZ26'], ns['SR26'] = .883, .84, .90, .94   # y 收較多：俯視深寬比對齊參考（0.51）
# 主要形體：依參考正面特徵點（L＝3.64 m 換算、x 置中）重新給控制點（軸心高度）
ns['NEW26'] = {
    # 前景主幹 A：上緣 −1.6/.37、−1.17/.46、−.52/.29（含苔）；下緣在 −1.34～−1.04 留小拱洞
    'A': dict(c=[(-1.50, -.465, .205), (-1.41, -.437, .232), (-1.30, -.41, .245), (-1.14, -.37, .268), (-.98, -.335, .272), (-.77, -.28, .248),
                 (-.50, -.21, .172), (-.20, -.14, .128), (.20, -.03, .108), (.72, .11, .080)], r0=.155, tp=.42),
    # 中央主拱 B：上緣 −.95/.48 → −.65/.76 → −.39/.76 → .30/.52 → .82/.17 → 落點 .95；根部粗、拱頂中、末端細（tp .55）
    'B': dict(c=[(-.94, .14, .07), (-.90, .10, .25), (-.86, .06, .44), (-.78, .02, .59), (-.64, -.02, .67), (-.45, -.05, .69), (-.25, -.06, .665),
                 (-.05, -.09, .60), (.15, -.17, .51), (.36, -.24, .40), (.56, -.28, .285), (.76, -.31, .15), (.92, -.32, .05)], r0=.096, tp=.55),
    # 最高主枝 T1：由中部往右上挑起（斜率由 0.4 漸增到 0.6），梢端約 0.92／1.09 m
    'T1': dict(c=[(-.40, .24, .40), (-.24, .24, .45), (-.05, .24, .53), (.13, .25, .61), (.33, .23, .71),
                  (.53, .27, .81), (.68, .31, .870), (.80, .33, .925), (.88, .35, .970)], r0=.105, tp=.28),   # 下端靠在 A 後側、中段搭 B2，俯視由左前往右後斜穿（與 B 交叉成 X）
    # B2：短、低，在 A 後方、主拱左腿右側，作為 T1 中段的支點
    'B2': dict(c=[(-.45, .10, .27), (-.30, .12, .22), (-.15, .13, .14), (-.02, .17, .06), (.08, .19, .03)], r0=.072, tp=.50, knots=((.45, .05),)),
    # 右枝 T2：次高層，梢端約 1.36／0.70
    'T2': dict(c=[(.36, -.10, .40), (.62, -.07, .42), (.86, -.03, .50), (1.04, .00, .58), (1.20, -.08, .64), (1.36, -.18, .69)], r0=.073, tp=.70, mode='shift'),   # 起點搭在主拱右腿上
    # 右下落地枝 R1：最低層，1.03/.48 → 1.42/.33 → 1.73 落地
    'R1': dict(c=[(.98, .04, .48), (1.20, .01, .41), (1.42, -.03, .31), (1.60, -.05, .14), (1.74, -.065, .012)], r0=.068, tp=.60, mode='abs'),
    # B3：由後方低處往右前上斜（中右空洞右側），末端搭在主拱右腿上
    # N9：右後低處的細枝，搭在 M6 上（不再架到 T1 梢端、在正面形成往右下的長斜帶）
    'N9': dict(c=[(1.45, .70, .05), (1.26, .62, .16), (1.06, .55, .27)], r0=.050, tp=.55),
    'B3': dict(c=[(.05, .30, .10), (.20, .18, .20), (.34, .02, .33), (.44, -.12, .42), (.50, -.21, .45)], r0=.075, tp=.50),
}
ns['UND26'] = [(.30, .10, .30), (.58, .08, -1.15), (.94, .14, .16)]     # A 下緣（沿軸距離跟著收）
for _st in ns['STAVES_A']:
    _st['ext'] *= .90
    _st['dep'] *= .90
for _st in ns['STAVES_T1']:
    _st['ext'] *= .92
for _k, _d in ns['NEW26'].items():                                         # 重新設計的構件：側向弓彎由設計決定（不加亂數弓彎）
    LAYOUT.setdefault(_k, {})['bow'] = _d.get('bow', (0.0, 0.0))

# v026 四、左端撕裂斷口重建：少數長裂片＋中、短裂片，片薄（ri 0.58–0.66，不是厚板）、片間留深縫（看得到內凹端面），
#   不往外放射（out≈0）、扭轉小；長短、深度、剝皮長度各不同。th：0＝下、π/2＝後、−π/2＝前、π＝上。
_K26 = dict(bend=0., sw=0., dark=.42, lift=0., out=.01)
ns['STAVES_A'] = [
    # 長裂片（上緣沿主幹頂面往左）
    dict(_K26, th=3.00, span=.40, ri=.60, ro=1.00, dep=.18, ext=.33, sw=.02, keep=.30, bias=.20, barkL=.42, wedge=.50, tw=.25, teeth=(.30,), split=.45, splitd=.40),
    dict(_K26, th=-2.42, span=.38, ri=.58, ro=1.00, dep=.15, ext=.29, lift=-.01, keep=.30, bias=-.25, barkL=.18, wedge=.55, tw=-.30, teeth=(.70,), split=.40, splitd=.42),
    dict(_K26, th=2.22, span=.34, ri=.64, ro=1.00, dep=.13, ext=.22, sw=.02, keep=.35, bias=-.15, barkL=.30, wedge=.55, tw=-.20, teeth=(.60,), split=.30, splitd=.30),
    # 中裂片
    dict(_K26, th=-1.55, span=.42, ri=.55, ro=.99, dep=.11, ext=.16, keep=.30, bias=.25, barkL=.10, dark=.48, wedge=.60, tw=.30, teeth=(.25, .80), split=.50, splitd=.36),
    dict(_K26, th=1.38, span=.38, ri=.60, ro=.99, dep=.09, ext=.13, keep=.30, bias=-.20, barkL=.36, wedge=.55, tw=-.25, teeth=(.50,), split=.30, splitd=.30),
    dict(_K26, th=-.72, span=.36, ri=.62, ro=.99, dep=.07, ext=.10, lift=.03, keep=.35, bias=.20, barkL=.24, wedge=.55, tw=.25, teeth=(.40,), split=.55, splitd=.30),
    # 短裂片
    dict(_K26, th=.30, span=.42, ri=.66, ro=.98, dep=.05, ext=.05, keep=.30, bias=.20, barkL=.40, wedge=.50, tw=.20, teeth=(.35, .80), split=.60, splitd=.24),
    dict(_K26, th=-3.05, span=.30, ri=.12, ro=.46, dep=.22, ext=.09, keep=.35, bias=0., barkL=0., dark=.58, wedge=.55, tw=.15, teeth=(.50,), split=.40, splitd=.25),   # 內層芯材（端面深處）
]

# v026 七、苔：主苔毯在前景主幹 A 隆起段頂面（s 0.10–0.85），次要覆蓋在主拱 B 的左肩；其餘露樹皮
ns['PATCH26'] = {'A': ((.48, .50, 1.0), (1.30, .16, .50)), 'B': ((.82, .30, .80),), 'B3': ((.60, .12, .30),)}

# 四、地衣（v021 成品覆蓋率約 0.1%，正面幾乎看不見）：斑片加多、加大，集中在苔毯下方的主幹前側、主拱與右側粗枝的正面／上面
ns['LICH'] = [('A', .12, (0, -1, -.30), .070), ('A', .26, (0, -1, -.10), .095), ('A', .40, (0, -1, -.35), .110), ('A', .52, (0, -1, .10), .080),
              ('A', .66, (0, -1, -.20), .100), ('A', .80, (0, -.9, .30), .075), ('A', .92, (0, -1, -.10), .065),
              ('B', .12, (0, -1, .20), .075), ('B', .30, (0, -1, .45), .095), ('B', .48, (0, -.6, .80), .080), ('B', .66, (0, -1, .30), .085), ('B', .84, (0, -1, .10), .070),
              ('B3', .45, (0, -1, .55), .075), ('T1', .55, (0, -.8, .60), .070), ('T1', .80, (0, -1, .30), .060),
              ('T2', .50, (0, -1, .40), .060), ('R1', .40, (0, -1, .50), .060)]


def _make_cards_v18(body0):
    """v018：落葉卡逐片用三維位置檢查——葉中心離地 3 cm 內＝地面；否則中心正下方 4.5 cm 內要打到木頭、而且那裡夠平（法線 z ≥ 0.45，能承托），
    或葉面頂點離木頭 < 8 mm 且中心離木頭 < 2 cm（卡在枝縫）。都不符合的刪掉。"""
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector as V3
    C = _make_cards_A_first(body0)
    me = body0.data
    co = [body0.matrix_world @ v.co for v in me.vertices]
    tree = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
    groups = {}
    for f, t in zip(C.F, C.tag):
        groups.setdefault(t, []).append(f)
    drop, nleaf, why = set(), 0, {'float': 0, 'steep': 0}
    for t, fs in groups.items():
        vs = sorted({i for f in fs for i in f})
        if len(vs) != 6:
            continue
        nleaf += 1
        P = [V3(C.V[i]) for i in vs]
        c = (P[2] + P[3]) / 2
        if c.z < .03:
            continue
        h = tree.ray_cast(c + V3((0, 0, .01)), V3((0, 0, -1)), .055)
        if h[0] is not None:
            if h[1].z >= .45:
                continue
            why['steep'] += 1
            drop.add(t)
            continue
        if min(tree.find_nearest(p)[3] for p in P) < .008 and tree.find_nearest(c)[3] < .02:
            continue
        why['float'] += 1
        drop.add(t)
    keep = [k for k, t in enumerate(C.tag) if t not in drop]
    C.F = [C.F[k] for k in keep]
    C.tag = [C.tag[k] for k in keep]
    print('LEAF_CHECK leaves', nleaf, 'removed', len(drop), why)
    ns['LEAF_CHECK'] = dict(leaves=nleaf, removed=len(drop), **why)
    return C


ns['make_cards'] = _make_cards_v18
ns['LAYOUT'] = LAYOUT
ns['zlib'] = zlib


def run(v, phase):
    ns['PHASE'] = phase
    import bpy
    asset = ns['NAMES'][v]
    if phase == 2:
        ns['run'](v)
        rep = ns['contact_report']()
        bpy.context.scene['dr09_v26_contacts'] = json.dumps(rep)
        bpy.ops.wm.save_as_mainfile(filepath=f'{HERE}/blend/{asset}_v026.blend', copy=True)
        print('CONTACT_SUMMARY', rep)
        return
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    ns['plan'](v)
    ns['cleanup']()
    R_ = ns['RECS']
    print('DEAD', [(x['kind'], x.get('name', ''), np.round(x['P'][len(x['P']) // 2], 2).tolist()) for x in R_ if x.get('dead')])
    if os.environ.get('DR9DUMP'):
        json.dump([dict(id=x['id'], parent=x.get('parent'), name=x.get('name', ''), kind=x['kind'], P=np.round(x['P'][::2], 3).tolist(), r=np.round(x['r'][::2], 3).tolist())
                   for x in R_ if not x.get('dead') and x['kind'] in ('branch', 'fork', 'stub')], open(os.environ['DR9DUMP'], 'w'))
    print('PLANCHECK', json.dumps(ns['plan_checks']()))
    print('CONTACT_SUMMARY', ns['contact_report']())
    mb = ns['MB']()
    for rec in R_:
        if not rec.get('dead'):
            ns['tube'](mb, rec, 0)
    o = ns['to_object'](mb, f'{asset}_LOD0', ns['layer_mat']())
    ns['hidden_faces'](o, mb)
    ns['_triangulate'](o)
    root = bpy.data.objects.new(asset, None)
    bpy.context.scene.collection.objects.link(root)
    o.parent = root
    piv = ns['_exec'](ns['ROOTS'] + '/dr_pivot.py', 'dr_pivot')
    piv['to_bottom_centre'](root, o)
    print('GREYBOX tris', ns['_tri'](o))
    out = os.environ.get('DR9OUT', f'{HERE}/blend/{asset}_v026_greybox.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out, copy=True)
    print('GREYBOX_DONE', out)


if __name__ == '__main__' and '--' in sys.argv:
    a = sys.argv[sys.argv.index('--') + 1:]
    try:
        run(a[0] if a else 'L', int(a[1]) if len(a) > 1 else 2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
