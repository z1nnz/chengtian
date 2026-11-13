// 承天 XT01 xianxia great tree: bark. URP, opaque, hand-painted bark tile + normal map, soft wrapped light with a cool shadow tint.
// Wind: the same sway as YunJing/XianxiaTreeLeaves (vertex colour R = weight: trunk 0, limbs 0.02-0.25, twigs up to ~0.55,
// G = phase), so twigs and their leaf cards move together. Keep _WindStrength / _WindSpeed / _WindDir equal on both materials.
Shader "YunJing/XianxiaTreeBark"
{
    Properties
    {
        _BaseMap ("Bark", 2D) = "white" {}
        _BaseColor ("Tint", Color) = (1, 1, 1, 1)
        [Normal] _BumpMap ("Normal", 2D) = "bump" {}
        _BumpScale ("Normal strength", Range(0, 2)) = 1
        _Wrap ("Wrap (soft terminator)", Range(0, 1)) = 0.25
        _ShadowTint ("Shadow tint (ambient in shade)", Color) = (0.8, 0.86, 0.96, 1)
        _Ambient ("Ambient strength", Range(0, 2)) = 1.35
        _ShadowStrength ("Cast shadow strength", Range(0, 1)) = 0.7
        _WindStrength ("Sway (m at weight 1)", Float) = 0.22
        _WindSpeed ("Sway speed", Float) = 1
        _WindDir ("Wind direction (xz)", Vector) = (1, 0, 0.35, 0)
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" "RenderPipeline" = "UniversalPipeline" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor, _ShadowTint;
            half _BumpScale, _Wrap, _Ambient, _ShadowStrength;
            float _WindStrength, _WindSpeed;
            float4 _WindDir;
        CBUFFER_END
        TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
        TEXTURE2D(_BumpMap); SAMPLER(sampler_BumpMap);

        float3 Sway(float3 positionWS, float4 colour)
        {
            float3 origin = float3(UNITY_MATRIX_M._m03, UNITY_MATRIX_M._m13, UNITY_MATRIX_M._m23);
            float w = colour.r; float ph = colour.g * 6.2832;
            float t = _Time.y * _WindSpeed + origin.x * 0.31 + origin.z * 0.23;
            float gust = sin(t * 1.25 + ph * 0.25) * 0.55 + sin(t * 2.6 + ph * 0.5) * 0.25 + 0.2;
            float2 dir = normalize(_WindDir.xz + 1e-4);
            float3 offset = float3(dir.x, 0, dir.y) * gust * _WindStrength * w;
            offset.y -= abs(gust) * _WindStrength * w * w * 0.15;
            return positionWS + offset;
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

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float4 tangentOS : TANGENT; float2 uv : TEXCOORD0; float4 colour : COLOR; };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
                float4 tangentWS : TEXCOORD3;
                float fogCoord : TEXCOORD4;
            };

            Varyings vert(Attributes v)
            {
                Varyings o;
                float3 ws = Sway(TransformObjectToWorld(v.positionOS.xyz), v.colour);
                o.positionWS = ws; o.positionCS = TransformWorldToHClip(ws);
                VertexNormalInputs ni = GetVertexNormalInputs(v.normalOS, v.tangentOS);
                o.normalWS = ni.normalWS; o.tangentWS = float4(ni.tangentWS, v.tangentOS.w * GetOddNegativeScale());
                o.uv = TRANSFORM_TEX(v.uv, _BaseMap);
                o.fogCoord = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 frag(Varyings i) : SV_Target
            {
                half3 albedo = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).rgb * _BaseColor.rgb;
                half3 nt = UnpackNormalScale(SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, i.uv), _BumpScale);
                float3 bt = cross(i.normalWS, i.tangentWS.xyz) * i.tangentWS.w;
                float3 n = normalize(TransformTangentToWorld(nt, float3x3(i.tangentWS.xyz, bt, i.normalWS)));
                Light sun = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half lit = saturate((dot(n, sun.direction) + _Wrap) / (1 + _Wrap)) * lerp(1, sun.shadowAttenuation, _ShadowStrength) * sun.distanceAttenuation;
                half3 amb = SampleSH(n) * _Ambient * lerp(_ShadowTint.rgb, 1, lit);
                half3 c = albedo * (sun.color * lit + amb);
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
            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float4 colour : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; };
            Varyings vert(Attributes v)
            {
                Varyings o;
                float3 ws = Sway(TransformObjectToWorld(v.positionOS.xyz), v.colour);
                o.positionCS = TransformWorldToHClip(ApplyShadowBias(ws, TransformObjectToWorldNormal(v.normalOS), _LightDirection));
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
            ZWrite On ColorMask R
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            struct Attributes { float4 positionOS : POSITION; float4 colour : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; };
            Varyings vert(Attributes v) { Varyings o; o.positionCS = TransformWorldToHClip(Sway(TransformObjectToWorld(v.positionOS.xyz), v.colour)); return o; }
            half4 frag(Varyings i) : SV_Target { return 0; }
            ENDHLSL
        }
    }
    FallBack Off
}
