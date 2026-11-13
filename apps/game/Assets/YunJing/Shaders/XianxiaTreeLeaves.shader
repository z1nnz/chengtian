// 承天 XT01 xianxia great tree: leaf cards (and the LOD3 impostor with _Baked = 1). URP, both faces, alpha clip.
// The leaf atlas is grey: colour = deep / mid / tip ramp along the light mask in vertex colour B, pushed leaf by leaf by the painted
// value; vertex colour A picks a per-cluster tint (A < 0.5 -> Variation A, A > 0.5 -> Variation B). Green and gold are two
// materials of this shader on the same mesh and texture. Normals come from the mesh (bent to each leaf cluster): soft lobes.
// Cards seen edge-on thin out (Graze) so the crown rim never shows smeared slivers.
// Wind: vertex colour R = sway weight, G = phase (the bark shader uses the same sway, so leaves stay on their twigs).
Shader "YunJing/XianxiaTreeLeaves"
{
    Properties
    {
        _BaseMap ("Leaf atlas (grey clusters + impostors)", 2D) = "white" {}
        _Cutoff ("Alpha cut-off", Range(0, 1)) = 0.5
        [Toggle] _Baked ("Impostor (use the atlas colour as is)", Float) = 0
        _BaseColor ("Impostor tint", Color) = (1, 1, 1, 1)
        [Header(Leaf colour)]
        _DeepColor ("Deep (inside, underneath)", Color) = (0.17, 0.35, 0.32, 1)
        _MidColor ("Mid", Color) = (0.36, 0.6, 0.27, 1)
        _TipColor ("Tip (sunlit tops)", Color) = (0.72, 0.85, 0.42, 1)
        _MidPoint ("Mid point", Range(0.05, 0.95)) = 0.5
        _MaskOffset ("Light mask offset", Range(-0.5, 0.5)) = 0
        _DetailMid ("Atlas mean value (gamma)", Range(0.1, 0.9)) = 0.65
        _Detail ("Leaf-by-leaf light", Range(0, 2)) = 0.8
        _ValueStrength ("Painted value on colour", Range(0, 1)) = 0.45
        _VariationA ("Cluster tint A (0.5 grey = none)", Color) = (0.73, 0.64, 0.35, 1)
        _VariationB ("Cluster tint B (0.5 grey = none)", Color) = (0.44, 0.62, 0.53, 1)
        _VariationAmount ("Cluster tint amount", Range(0, 1)) = 0.45
        [Header(Light)]
        _Wrap ("Wrap (soft terminator)", Range(0, 1)) = 0.5
        _ShadowTint ("Shadow tint (ambient in shade)", Color) = (0.62, 0.74, 0.9, 1)
        _Ambient ("Ambient strength", Range(0, 2)) = 1
        _Translucency ("Back-light glow", Range(0, 1)) = 0.35
        _GrazeMin ("Graze: clipped below", Range(0, 1)) = 0.3
        _GrazeMax ("Graze: whole above", Range(0, 1)) = 0.66
        _ShadowStrength ("Cast shadow strength", Range(0, 1)) = 0.55
        [Header(Wind)]
        _WindStrength ("Sway (m at weight 1)", Float) = 0.22
        _WindSpeed ("Sway speed", Float) = 1
        _Flutter ("Leaf flutter (m)", Float) = 0.035
        _WindDir ("Wind direction (xz)", Vector) = (1, 0, 0.35, 0)
    }
    SubShader
    {
        Tags { "RenderType" = "TransparentCutout" "Queue" = "AlphaTest" "RenderPipeline" = "UniversalPipeline" }
        Cull Off

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor, _DeepColor, _MidColor, _TipColor, _VariationA, _VariationB, _ShadowTint;
            half _Cutoff, _Baked, _MidPoint, _MaskOffset, _DetailMid, _Detail, _ValueStrength, _VariationAmount;
            half _Wrap, _Ambient, _Translucency, _GrazeMin, _GrazeMax, _ShadowStrength;
            float _WindStrength, _WindSpeed, _Flutter;
            float4 _WindDir;
        CBUFFER_END
        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);

        float3 Sway(float3 positionWS, float4 colour, float flutter)
        {
            float3 origin = float3(UNITY_MATRIX_M._m03, UNITY_MATRIX_M._m13, UNITY_MATRIX_M._m23);
            float w = colour.r; float ph = colour.g * 6.2832;
            float t = _Time.y * _WindSpeed + origin.x * 0.31 + origin.z * 0.23;
            float gust = sin(t * 1.25 + ph * 0.25) * 0.55 + sin(t * 2.6 + ph * 0.5) * 0.25 + 0.2;
            float2 dir = normalize(_WindDir.xz + 1e-4);
            float3 offset = float3(dir.x, 0, dir.y) * gust * _WindStrength * w;
            offset.y -= abs(gust) * _WindStrength * w * w * 0.15;
            offset += sin(t * 6.3 + ph * 4.0 + dot(positionWS, float3(2.1, 1.3, 1.7))) * flutter * w * float3(0.5, 0.35, 0.5);
            return positionWS + offset;
        }

        half GrazeCut(float3 positionWS)
        {
            float3 ng = normalize(cross(ddy(positionWS), ddx(positionWS)));
            float3 v = normalize(_WorldSpaceCameraPos - positionWS);
            half g = abs(dot(ng, v));
            return lerp(0.97h, _Cutoff, saturate((g - _GrazeMin) / max(_GrazeMax - _GrazeMin, 1e-3)));
        }

        half GreyGamma(half3 c)
        {
            #if defined(UNITY_COLORSPACE_GAMMA)
                return c.g;
            #else
                return LinearToSRGB(c).g;
            #endif
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float2 uv : TEXCOORD0; float4 colour : COLOR; };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float4 colour : TEXCOORD3;
                float fogCoord : TEXCOORD4;
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                float3 ws = Sway(TransformObjectToWorld(v.positionOS.xyz), v.colour, _Flutter * (1 - _Baked));
                o.positionWS = ws; o.positionCS = TransformWorldToHClip(ws);
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap); o.colour = v.colour;
                o.fogCoord = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                half4 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv);
                clip(tex.a - GrazeCut(i.positionWS));          // the impostor too: its crossed quad seen edge-on would be a thin line
                half3 col;
                if (_Baked > 0.5) col = tex.rgb * _BaseColor.rgb;
                else
                {
                    half lum = GreyGamma(tex.rgb);
                    half m = saturate(i.colour.b + _MaskOffset + (lum - _DetailMid) * _Detail);
                    half3 ramp = m < _MidPoint ? lerp(_DeepColor.rgb, _MidColor.rgb, m / _MidPoint)
                                               : lerp(_MidColor.rgb, _TipColor.rgb, (m - _MidPoint) / (1 - _MidPoint));
                    half a = i.colour.a;
                    half3 tint = (a > 0.5 ? _VariationB.rgb : _VariationA.rgb) * 2;
                    col = lerp(ramp, ramp * tint, abs(a * 2 - 1) * _VariationAmount);
                    col *= lerp(1, lum / _DetailMid, _ValueStrength);
                }
                float3 n = normalize(i.normalWS);           // cluster normal: the same for both faces of a card
                Light sun = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half sh = lerp(1, sun.shadowAttenuation, _ShadowStrength);      // soft: the crown's own shadow never blots a lobe black
                half lit = saturate((dot(n, sun.direction) + _Wrap) / (1 + _Wrap)) * sh * sun.distanceAttenuation;
                float3 v = normalize(_WorldSpaceCameraPos - i.positionWS);
                half glow = pow(saturate(dot(v, -sun.direction)), 4) * _Translucency * sh;
                half3 amb = SampleSH(n) * _Ambient * lerp(_ShadowTint.rgb, 1, lit);
                half3 c = col * (sun.color * (lit + glow) + amb);
                return half4(MixFog(c, i.fogCoord), 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On ColorMask 0
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            float3 _LightDirection;
            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float2 uv : TEXCOORD0; float4 colour : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; float2 uv : TEXCOORD0; };
            Varyings vert(Attributes v)
            {
                Varyings o;
                float3 ws = Sway(TransformObjectToWorld(v.positionOS.xyz), v.colour, _Flutter * (1 - _Baked));
                float3 n = TransformObjectToWorldNormal(v.normalOS);
                o.positionCS = TransformWorldToHClip(ApplyShadowBias(ws, n, _LightDirection));
                #if UNITY_REVERSED_Z
                    o.positionCS.z = min(o.positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #else
                    o.positionCS.z = max(o.positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                return o;
            }
            half4 frag(Varyings i) : SV_Target { clip(SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).a - _Cutoff); return 0; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On ColorMask R
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            struct Attributes { float4 positionOS : POSITION; float2 uv : TEXCOORD0; float4 colour : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; float2 uv : TEXCOORD0; float3 positionWS : TEXCOORD1; };
            Varyings vert(Attributes v)
            {
                Varyings o;
                o.positionWS = Sway(TransformObjectToWorld(v.positionOS.xyz), v.colour, _Flutter * (1 - _Baked));
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                return o;
            }
            half4 frag(Varyings i) : SV_Target
            {
                clip(SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).a - GrazeCut(i.positionWS));
                return 0;
            }
            ENDHLSL
        }
    }
    FallBack Off
}
