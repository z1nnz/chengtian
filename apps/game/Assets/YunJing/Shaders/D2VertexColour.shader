// D2 古樹神木（Claude Code, 11/26）：Blender 把每個模型材質的底色烘進頂點色，這個 shader 直接拿頂點色當底色。
// 主光＋陰影、環境光（SH）、URP 霧；雙面（葉子、蕨）；支援 GPU instancing（蕨、草、石頭重複擺幾萬份）。
Shader "YunJing/D2VertexColour"
{
    Properties
    {
        _Tint ("Tint", Color) = (1, 1, 1, 1)
        _Wrap ("Light wrap (leaves)", Range(0, 1)) = 0.25
        _Smooth ("Smoothness", Range(0, 1)) = 0.15
        [Toggle(_HERO)] _Hero ("Hero (albedo + normal maps, no vertex colour)", Float) = 0
        _MainTex ("Albedo", 2D) = "white" {}
        [Normal] _BumpMap ("Normal", 2D) = "bump" {}
        _BumpScale ("Normal strength", Range(0, 2)) = 1
        [Toggle(_TRI)] _Tri ("Triplanar bark (god tree, like Blender box projection)", Float) = 0
        _TriScale ("Box projection scale (object space)", Vector) = (0.357, 0.357, 0.222, 0)
        _TriBlend ("Box blend", Range(0, 1)) = 0.35
        _BarkMean ("Bark texture mean (linear)", Vector) = (0.2, 0.15, 0.1, 0)
        _BarkLift ("Bark lift luminance", Float) = 0.3
        _Dbg ("Debug view", Float) = 0
        _TriRow0 ("Unity world -> object row 0", Vector) = (1, 0, 0, 0)
        _TriRow1 ("Unity world -> object row 1", Vector) = (0, 0, 1, 0)
        _TriRow2 ("Unity world -> object row 2", Vector) = (0, 1, 0, 0)
        [Toggle(_TILE)] _Tile ("Tiled bark on own UV (V6 arch)", Float) = 0
        _AOStr ("Baked AO strength", Range(0, 1)) = 1
        _Wet ("Puddle reflection strength", Range(0, 2)) = 1
        // 11/28 D2 調色（Unity 專案沒開後製；改全隊的渲染設定要先問 → 先在 D2 自己的 shader 做）；_Grade = 0 回到沒調色
        _Grade ("D2 grade on", Float) = 1
        _GExp ("Grade exposure (stops)", Float) = 0.25
        _GCon ("Grade contrast", Float) = 1.15
        _GSat ("Grade saturation", Float) = 1.05
        _GWarm ("Grade warmth", Float) = 0.03
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" "RenderPipeline" = "UniversalPipeline" }
        Cull Off

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_instancing
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog
            #pragma shader_feature_local _HERO
            #pragma shader_feature_local _TRI
            #pragma shader_feature_local _TILE
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            CBUFFER_START(UnityPerMaterial)
                half4 _Tint; half _Wrap; half _Smooth; half _BumpScale; float4 _MainTex_ST; float4 _TriScale; half _TriBlend; float4 _BarkMean; half _BarkLift; float4 _TriRow0; float4 _TriRow1; float4 _TriRow2; float _Dbg; half _AOStr; half _Wet; half _Grade; half _GExp; half _GCon; half _GSat; half _GWarm;
            CBUFFER_END
            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            TEXTURE2D(_BumpMap); SAMPLER(sampler_BumpMap);

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float4 tangentOS : TANGENT; float2 uv : TEXCOORD0; float2 uv1 : TEXCOORD1; float2 uv2 : TEXCOORD2; float4 colour : COLOR; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                half4 colour : TEXCOORD2;
                float fogCoord : TEXCOORD3;
                float2 uv : TEXCOORD4;
                float4 tangentWS : TEXCOORD5;
                float2 uv1 : TEXCOORD6;
                float2 uv2 : TEXCOORD7;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(v); UNITY_TRANSFER_INSTANCE_ID(v, o);
                o.positionWS = TransformObjectToWorld(v.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.colour = v.colour;
                o.uv = v.uv; o.uv1 = v.uv1; o.uv2 = v.uv2;
                o.tangentWS = float4(TransformObjectToWorldDir(v.tangentOS.xyz), v.tangentOS.w * GetOddNegativeScale());
                o.fogCoord = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 frag(Varyings i, bool front : SV_IsFrontFace) : SV_Target
            {
                // 11/28 v5：減面版有退化三角形 → 法線長度 0 → normalize 出 NaN（V1 神木遠景整團黑）→ 安全版
                float3 nWS = i.normalWS; nWS = dot(nWS, nWS) > 1e-12 ? nWS * rsqrt(dot(nWS, nWS)) : float3(0, 1, 0);
                UNITY_SETUP_INSTANCE_ID(i);
                half ao = 1, rough = 1;
                #if defined(_TRI) || defined(_TILE)
                    // 神木：跟 Blender 一樣用物件座標做盒投影（同一張掃描樹皮、同樣比例）。
                    // 頂點色 A = 樹皮換成平均色時的結果、uv/uv1 存 B = 樹皮換成黑色時的結果 → 顏色 = B + (A−B)·樹皮/平均
                    // Unity 世界 → 神木在 Blender 的物件空間（材質存不了矩陣 → 拆成三列向量）
                  #if defined(_TILE)
                    // V6 拱門：同一張樹皮用模型自己的 UV 鋪（Blender GodTreeBark 材質）
                    half3 bark = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, i.uv).rgb;
                    half3 B0 = half3(i.uv1.x, i.uv1.y, i.uv2.x); ao = i.uv2.y;
                  #else
                    float3x3 R3 = float3x3(_TriRow0.xyz, _TriRow1.xyz, _TriRow2.xyz);
                    float3 p = (mul(R3, i.positionWS) + float3(_TriRow0.w, _TriRow1.w, _TriRow2.w)) * _TriScale.xyz;
                    float3 nObj = normalize(mul(R3, nWS));
                    float3 w = pow(abs(nObj), lerp(16, 2, _TriBlend)); w /= max(w.x + w.y + w.z, 1e-6);
                    float2 uvX = p.yz, uvY = p.xz, uvZ = p.xy;
                    half3 bark = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, uvX).rgb * w.x
                               + SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, uvY).rgb * w.y
                               + SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, uvZ).rgb * w.z;
                    half3 B0 = half3(i.uv.x, i.uv.y, i.uv1.x); ao = i.uv1.y;
                  #endif
                    // 算式在線性空間（跟 Blender 一樣）；專案是 Gamma 色彩空間時貼圖取樣不會自動轉線性 → 自己轉，算完再轉回去
                    half3 A = SRGBToLinear(i.colour.rgb);
                    #if defined(UNITY_COLORSPACE_GAMMA)
                        bark = SRGBToLinear(bark);
                    #endif
                    half3 B = B0;
                    // 用亮度比（逐色比會把灰白的樹皮凸紋放大成藍白色）；色相留一半
                    half3 lw = half3(.2126, .7152, .0722);
                    half lr = min(dot(bark, lw) / max(dot(_BarkMean.rgb, lw), 1e-3), 3);
                    half3 hue = lerp(1, (bark / max(dot(bark, lw), 1e-3)) / (_BarkMean.rgb / max(dot(_BarkMean.rgb, lw), 1e-3)), .35);
                    half3 albedo = max(0, B + (A - B) * lr * hue) * _Tint.rgb;
                    #if defined(UNITY_COLORSPACE_GAMMA)
                        albedo = LinearToSRGB(albedo);
                    #endif
                    if (_Dbg > 0.5) return half4(_Dbg < 1.5 ? bark : _Dbg < 2.5 ? A : _Dbg < 3.5 ? B * 4 : half3(lr, lr, lr) / 3, 1);
                    half barkAmt = saturate(dot(A - B, half3(.2126, .7152, .0722)) / max(_BarkLift, 1e-3));
                  #if defined(_TILE)
                    half3 tn = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, i.uv), _BumpScale * barkAmt);
                    float3 nw = nWS;
                    // 11/28 v5：UV 退化的地方切線是 0 → normalize 出 NaN（V1 神木腳下一團黑／綠）→ 改用安全版
                    float3 tw = i.tangentWS.xyz; tw = dot(tw, tw) > 1e-8 ? tw * rsqrt(dot(tw, tw)) : float3(0, 0, 0);
                    float3 bw = cross(nw, tw) * (i.tangentWS.w < 0 ? -1 : 1);
                    float3 nn = tn.x * tw + tn.y * bw + tn.z * nw;
                    float3 n = (dot(nn, nn) > 1e-8 ? nn * rsqrt(dot(nn, nn)) : nw) * (front ? 1 : -1);
                  #else
                    // 樹皮法線（OpenGL）三向混合；長苔的地方淡掉
                    half3 tX = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, uvX), _BumpScale);
                    half3 tY = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, uvY), _BumpScale);
                    half3 tZ = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, uvZ), _BumpScale);
                    tX = half3(tX.xy + nObj.yz, abs(tX.z) * nObj.x);
                    tY = half3(tY.xy + nObj.xz, abs(tY.z) * nObj.y);
                    tZ = half3(tZ.xy + nObj.xy, abs(tZ.z) * nObj.z);
                    float3 nb = normalize(tX.zxy * w.x + tY.xzy * w.y + tZ.xyz * w.z);
                    nb = normalize(lerp(nObj, nb, barkAmt));
                    float3 n = normalize(mul(nb, R3)) * (front ? 1 : -1);
                  #endif
                #elif defined(_HERO)
                    // 主角物件：Blender 烘的底色貼圖（sRGB 匯入，取樣已是線性）＋切線空間法線
                    half4 albAO = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, i.uv);
                    half3 albedo = albAO.rgb * _Tint.rgb; ao = albAO.a;   // alpha = Blender 烘的 AO（舊圖沒有 alpha → 1）
                    half3 tn = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, i.uv), _BumpScale);
                    float3 nw = nWS;
                    // 11/28 v5：UV 退化的地方切線是 0 → normalize 出 NaN（V1 神木腳下一團黑／綠）→ 改用安全版
                    float3 tw = i.tangentWS.xyz; tw = dot(tw, tw) > 1e-8 ? tw * rsqrt(dot(tw, tw)) : float3(0, 0, 0);
                    float3 bw = cross(nw, tw) * (i.tangentWS.w < 0 ? -1 : 1);
                    float3 nn = tn.x * tw + tn.y * bw + tn.z * nw;
                    float3 n = (dot(nn, nn) > 1e-8 ? nn * rsqrt(dot(nn, nn)) : nw) * (front ? 1 : -1);
                #else
                    half3 albedo = i.colour.rgb;   // Blender 匯出的頂點色是 sRGB
                    #if !defined(UNITY_COLORSPACE_GAMMA)
                        albedo = SRGBToLinear(albedo);
                    #endif
                    albedo *= _Tint.rgb;
                    rough = i.colour.a;   // alpha = Blender 的粗糙度（舊匯出沒有 → 1）
                    float3 n = nWS * (front ? 1 : -1);
                #endif
                Light sun = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half ndl = saturate((dot(n, sun.direction) + _Wrap) / (1 + _Wrap));
                float3 v = normalize(GetWorldSpaceViewDir(i.positionWS));
                float3 h = normalize(sun.direction + v);
                half spec = pow(saturate(dot(n, h)), lerp(8, 128, _Smooth)) * _Smooth * 0.5;
                // 11/28 凹縫陰影：環境光整個乘 AO、直射光乘一半（Blender 有全域光照，凹處自然暗）
                ao = lerp(1, saturate(ao), _AOStr);
                half3 lit = albedo * (sun.color * ndl * sun.shadowAttenuation * lerp(1, ao, .5) + SampleSH(n) * ao) + sun.color * spec * sun.shadowAttenuation;
                // 11/28 積水、坑裡的水：粗糙度低的地方反射天空（陰天的天光色）＋太陽高光；Fresnel 讓斜看更亮
                half wet = saturate((.2 - rough) / .12) * _Wet;   // 11/28 v5b：.3 時路上整片灰 → 只留真正的水窪（Blender 水窪粗糙度很低）   // 11/28 v5：.55 太寬，整條路變鏡子 → 只有真的積水（粗糙度 < .3）
                if (wet > 0)
                {
                    float3 rv = reflect(-v, n);
                    half3 sky = lerp(unity_AmbientEquator.rgb * .5, unity_AmbientSky.rgb * 1.3, saturate(rv.y * 1.4 + .05));   // 11/28 v5b：森林裡水面大多倒映暗的樹，只有接近正上方才是天
                    half fr = .02 + .98 * pow(1 - saturate(dot(n, v)), 5);
                    half a2 = max(rough * rough, .002);
                    half nh = saturate(dot(n, h));
                    half dd = nh * nh * (a2 - 1) + 1;
                    half ggx = a2 / (PI * dd * dd) * .25;
                    // 11/28 v5b：濕的地方本身變暗、反射上限 60%
                    lit = lerp(lit * lerp(1, .45, wet), sky, min(fr * .9 + .1, .6) * wet) + sun.color * min(ggx, 30) * fr * sun.shadowAttenuation * wet;
                }
                // 11/28 v5：神木遠景減面版有少數像素算出 NaN（整團黑）→ 改用只有環境光的安全色，霧照樣蓋上
                if (any(isnan(lit)) || any(isinf(lit))) lit = max(0, albedo) * SampleSH(nWS);
                lit = max(lit, 0);
                half3 col = MixFog(lit, i.fogCoord);
                if (_Grade > .5)   // 11/28 對照 Blender AgX 中高對比：亮一點、對比強一點、微暖（線性空間、以 18% 灰為中心）
                {
                    col *= exp2(_GExp);
                    col = .18 * pow(max(col, 1e-5) / .18, _GCon);
                    half lum = dot(col, half3(.2126, .7152, .0722));
                    col = max(0, lerp(lum, col, _GSat)) * half3(1 + _GWarm, 1, 1 - _GWarm);
                    col = col / (1 + max(0, col - .8) * .5);   // 亮部柔和收（避免天空、水面直接爆白）
                }
                return half4(col, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On ColorMask 0 Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            float3 _LightDirection;
            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings { float4 positionCS : SV_POSITION; };
            Varyings vert(Attributes v)
            {
                Varyings o; UNITY_SETUP_INSTANCE_ID(v);
                float3 ws = TransformObjectToWorld(v.positionOS.xyz);
                float3 n = TransformObjectToWorldNormal(v.normalOS);
                o.positionCS = TransformWorldToHClip(ApplyShadowBias(ws, n, _LightDirection));
                #if UNITY_REVERSED_Z
                    o.positionCS.z = min(o.positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #else
                    o.positionCS.z = max(o.positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                return o;
            }
            half4 frag(Varyings i) : SV_Target { return 0; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On ColorMask R Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct Attributes { float4 positionOS : POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings { float4 positionCS : SV_POSITION; };
            Varyings vert(Attributes v) { Varyings o; UNITY_SETUP_INSTANCE_ID(v); o.positionCS = TransformObjectToHClip(v.positionOS.xyz); return o; }
            half4 frag(Varyings i) : SV_Target { return 0; }
            ENDHLSL
        }
    }
    FallBack Off
}
