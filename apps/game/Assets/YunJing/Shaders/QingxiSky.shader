// The novice world's sky: a clear blue that deepens overhead and pales into haze at the horizon, soft drifting
// cumulus, and a gentle sun. Same properties as Skybox/Procedural where QingxiDayNight drives them (_SkyTint,
// _GroundColor, _Exposure), so the clock still colours dawn, dusk and night.
Shader "YunJing/QingxiSky"
{
    Properties
    {
        _SkyTint ("Sky tint", Color) = (.5, .62, .74, 1)
        _GroundColor ("Horizon haze", Color) = (.78, .83, .84, 1)
        _Exposure ("Exposure", Float) = 1.2
        _SunSize ("Sun size", Float) = .035
        _Clouds ("Cloud cover", Range(0, 1)) = .5
        _Night ("Night", Range(0, 1)) = 0
        _MoonDir ("Moon direction", Vector) = (-.3, .4, .86, 0)
        _Ridges ("Distant ridges", Range(0, 1)) = 1
    }
    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off ZWrite Off
        Pass
        {
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _SkyTint;
                half4 _GroundColor;
                float _Exposure;
                float _SunSize;
                float _Clouds;
                float _Night;
                float4 _MoonDir;
                float _Ridges;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dir : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.dir = input.positionOS.xyz;
                return o;
            }

            float Hash(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }
            float Noise(float2 p)
            {
                float2 i = floor(p), f = frac(p);
                f = f * f * (3 - 2 * f);
                return lerp(lerp(Hash(i), Hash(i + float2(1, 0)), f.x), lerp(Hash(i + float2(0, 1)), Hash(i + 1), f.x), f.y);
            }
            float Fbm(float2 p)
            {
                float v = 0, a = .5;
                for (int k = 0; k < 5; k++) { v += a * Noise(p); p = p * 2.03 + 17.1; a *= .5; }
                return v;
            }

            // One layer of far mountains: a ridge line around the whole horizon (seamless: the noise runs on a circle).
            // Returns how much of this pixel the layer covers.
            float Ridge(float3 d, float freq, float seed, float base, float amp)
            {
                float2 ring = normalize(d.xz + 1e-5) * freq;
                float h = base + amp * (Fbm(ring + seed) * .75 + Noise(ring * 3.1 + seed) * .25);
                return smoothstep(h + .004, h - .004, d.y);
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float3 d = normalize(i.dir);
                float up = d.y;
                float3 sun = normalize(_MainLightPosition.xyz);
                half3 zenith = _SkyTint.rgb * half3(.62, .85, 1.25);
                zenith = lerp(dot(zenith, half3(.3, .55, .15)).xxx, zenith, .78);   // a softer blue: the 11/11 sky was louder than the land
                half3 horizon = lerp(_GroundColor.rgb, half3(.86, .92, .97), .45);
                half3 c = lerp(horizon, zenith, pow(saturate(up), .5));
                c = lerp(c, _GroundColor.rgb * .85, saturate(-up * 5));   // below the horizon: haze
                // Cumulus on a dome: noise projected from the view direction, drifting slowly, thinning to the horizon.
                float2 uv = d.xz / (up + .18) * .55 + _Time.y * float2(.003, .0012);
                float n = Fbm(uv * 1.4);
                float cover = smoothstep(1 - _Clouds, 1.05 - _Clouds * .7, n) * smoothstep(.0, .22, up);
                float lit = saturate(Fbm(uv * 1.4 + sun.xz * .08) - n + .55);   // brighter on the sun side of each cloud
                half3 cloud = lerp(half3(.72, .77, .86) * _SkyTint.rgb * 1.6, half3(1, .99, .96), lit);
                c = lerp(c, cloud, cover * .92);
                // The sun: a small soft disc and a wide glow.
                float s = saturate(dot(d, sun));
                c += half3(1, .93, .8) * (pow(s, 900 / max(_SunSize * 30, .1)) * 3 + pow(s, 12) * .25) * (1 - cover * .8);
                // Stars and the moon's halo, at night only, behind the clouds.
                // Cells in the direction itself (not a flat projection), so stars stay round down to the horizon.
                float3 sp = d * 95;
                float3 cell3 = floor(sp);
                float2 cell = cell3.xy + cell3.z * 17.31;
                float star = step(.955, Hash(cell)) * smoothstep(.34, .0, length(frac(sp) - .5));
                star *= .6 + .4 * sin(_Time.y * (1 + Hash(cell + 3) * 2) + Hash(cell + 7) * 6.28);
                float m = saturate(dot(d, normalize(_MoonDir.xyz)));
                half3 night = half3(.85, .9, 1) * star * 2.2 * smoothstep(.02, .3, up)
                    + half3(.55, .68, 1) * (pow(m, 90) * .9 + pow(m, 7) * .22);
                c += night * _Night * (1 - cover * .85) / max(_Exposure * .82, .05) * .35;
                // The moon: a small sphere lit from the side and a little behind, so it shows as a waning crescent
                // (承天's sign) with a soft terminator, darker seas, a dimmed limb and, at night, faint earthshine on
                // the dark side. Pale by day.
                float3 md = normalize(_MoonDir.xyz);
                float3 mr = normalize(cross(float3(0, 1, 0), md));
                float3 mu = cross(md, mr);
                float2 mp = float2(dot(d, mr), dot(d, mu)) / .034;
                float mrad = dot(mp, mp);
                if (mrad < 1 && dot(d, md) > 0)
                {
                    float3 mn = float3(mp, -sqrt(1 - mrad));                 // towards the viewer is -z here
                    float3 ml = normalize(float3(-.86, .22, .46));           // sunlight from the left, slightly behind
                    float lit = smoothstep(-.04, .22, dot(mn, ml));
                    float seas = lerp(.62, 1, smoothstep(.35, .7, Fbm(mp * 2.1 + 5.3)));
                    seas *= lerp(.88, 1, Noise(mp * 9 + 2.7));
                    float limb = lerp(.72, 1, pow(1 - mrad, .35));
                    half3 face = half3(1, .98, .92) * seas * limb * lit * 1.5
                        + half3(.16, .2, .3) * seas * limb * (1 - lit) * _Night;
                    float edge = smoothstep(1, .93, mrad);
                    float show = edge * (1 - cover * .9) * lerp(lit * .3, 1, _Night);
                    c = lerp(c, face / max(_Exposure * .82, .05), show);
                }
                // Far mountains in three layers, each paler and bluer than the one in front, sinking into the haze
                // at their feet, so the land does not end at the edge of the walkable ground.
                half3 haze = lerp(_GroundColor.rgb, c, .25);
                half3 rock = _GroundColor.rgb * half3(.5, .58, .7);
                float foot = smoothstep(-.02, .09, up);
                c = lerp(c, lerp(haze, rock, .22 * foot + .06), Ridge(d, 2.1, 11.3, .03, .15) * _Ridges);
                c = lerp(c, lerp(haze, rock, .42 * foot + .1), Ridge(d, 3.4, 47.9, .012, .105) * _Ridges);
                c = lerp(c, lerp(haze, rock, .66 * foot + .14), Ridge(d, 5.6, 83.1, -.004, .062) * _Ridges);
                return half4(c * _Exposure * .82, 1);
            }
            ENDHLSL
        }
    }
}
