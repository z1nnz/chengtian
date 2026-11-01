using System;
using System.Collections.Generic;

namespace YunJing
{
    // C# port of tools/zhuo-boar/zhuo-boar-rules.mjs (Johnnnny0823). Pure logic with the same fixed step, same order and same
    // numbers from packages/content/zhuo-boar-encounter-v1.json; QingxiZhuoBoarSmoke replays the runs parity.mjs records.
    public static class QingxiZhuoBoarRules
    {
        public const double Step = 1.0 / 120;
        public const string CleansedEvent = "zhuoBoar.cleansed", EscapedEvent = "zhuoBoar.escaped";

        [Serializable] public sealed class Tuning { public double alertSeconds, dodgeCooldownSeconds, boarLengthM, boarWidthM, playerRadiusM, cleansedStandSeconds, fleeSpeedMps, fleeSeconds; }
        [Serializable] public sealed class ButtonTexts { public string dodge, cleanse, cleanseKey, dodgeKey; }
        [Serializable] public sealed class TipTexts { public string alert, telegraph, charge, dazeFar, dazeNear, brake, hit, firstCleanse; }
        [Serializable] public sealed class HudTexts { public string zhuo, stamina, hits; }
        [Serializable] public sealed class Texts { public string prompt, cleansed, cleansedHint, escaped, escapedHint, cooldown; public ButtonTexts button; public TipTexts tip; public HudTexts hud; }
        [Serializable]
        public sealed class Content
        {
            public string id, title;
            public int day, cleanseNeeded, hitsBeforeEscape;
            public double noticeRadiusM, pawTelegraphSeconds, trackTurnDegPerSecond, chargeSpeedMps, chargeMaxDistanceM, brakeRecoverSeconds, dazeSeconds,
                cleanseHoldSeconds, cleanseRadiusM, hitKnockbackM, hitStaminaLoss, staminaFloor, retryCooldownSeconds, dodgeIFrameSeconds, dodgeDistanceM, chargeLineWidthM, dazeShakeSeconds;
            public Tuning tuning;
            public Texts texts;
        }

        public struct P { public double x, z; public P(double x, double z) { this.x = x; this.z = z; } }
        public struct Obstacle { public string id; public double x, z, r; }
        public sealed class Bounds { public double minX, maxX, minZ, maxZ; }
        public sealed class Input { public P player; public IList<Obstacle> obstacles; public bool cleanseHeld; public P? dodge; public Bounds bounds; }
        public struct Event { public string type, obstacle; public double x, z, staminaLost, stamina, durationSeconds; public int hits, count, hitsTaken; }
        public sealed class Line { public double x, z, yaw, length, width; public bool isFixed; }

        static readonly Obstacle[] None = new Obstacle[0];
        static double Dot(P a, P b) => a.x * b.x + a.z * b.z;
        static double Len(P v) => Math.Sqrt(v.x * v.x + v.z * v.z);
        static P Sub(P a, P b) => new P(a.x - b.x, a.z - b.z);
        static P FromYaw(double yaw) => new P(Math.Sin(yaw), Math.Cos(yaw));
        static double ToYaw(P v) => Math.Atan2(v.x, v.z);
        static double Wrap(double a) { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; }

        public sealed class Encounter
        {
            readonly Content c; readonly Tuning t;
            readonly double homeX, homeZ, homeYaw;
            bool armed, chargeHit;
            double accumulator, iFrameUntil = -1, dodgeReadyAt, retryAt = -1, stateAt, cleanseHeld;
            double? lastNow, startedAt;
            P chargeFrom; P? fleeDir;
            readonly List<Event> events = new List<Event>();

            public string state { get; private set; }
            public double x { get; private set; }
            public double z { get; private set; }
            public double yaw { get; private set; }
            public double time { get; private set; }
            public double stamina { get; private set; }
            public int hits { get; private set; }
            public int cleanses { get; private set; }
            public bool visible { get; private set; }
            public Line line { get; private set; }

            public Encounter(Content content, double homeX, double homeZ, double homeYaw, double stamina, bool autoStart)
            {
                c = content; t = content.tuning;
                this.homeX = homeX; this.homeZ = homeZ; this.homeYaw = homeYaw; this.stamina = stamina; armed = autoStart;
                Reset();
            }

            void Reset()
            {
                state = "idle"; x = homeX; z = homeZ; yaw = homeYaw; stateAt = time;
                hits = 0; cleanses = 0; cleanseHeld = 0; chargeHit = false; line = null; visible = true; fleeDir = null;
            }

            P Pos => new P(x, z);
            public double Elapsed => time - stateAt;
            public double Zhuo => Math.Max(0, 1 - (double)cleanses / c.cleanseNeeded);
            public double CleanseProgress => cleanseHeld / c.cleanseHoldSeconds;
            public bool Invulnerable => time < iFrameUntil;
            public double RetryIn => state == "escaped" ? Math.Max(0, retryAt - time) : 0;
            public bool Engaged => state != "idle" && state != "cleansed" && state != "escaped";
            public bool CanCleanse(P player) => state == "daze" && Len(Sub(player, Pos)) <= c.cleanseRadiusM;
            public bool CanDodge => Engaged && time >= dodgeReadyAt;

            public bool Begin()
            {
                if (state != "idle") return false;
                armed = true;
                Enter("alert");
                if (startedAt == null) startedAt = time;
                return true;
            }

            void Enter(string next) { state = next; stateAt = time; }

            // The returned list is reused by the next call.
            public List<Event> Update(double now, Input input)
            {
                events.Clear();
                if (lastNow == null) lastNow = now;
                accumulator += Math.Max(0, now - lastNow.Value);
                lastNow = now;
                if (input.dodge.HasValue) TryDodge(input.dodge.Value);
                while (accumulator >= Step)
                {
                    accumulator -= Step;
                    time += Step;
                    Tick(input);
                }
                return events;
            }

            void TryDodge(P dir)
            {
                double m = Len(dir);
                if (m < 1e-3 || !CanDodge) return;
                iFrameUntil = time + c.dodgeIFrameSeconds;
                dodgeReadyAt = time + t.dodgeCooldownSeconds;
                events.Add(new Event { type = "dodge", x = dir.x / m * c.dodgeDistanceM, z = dir.z / m * c.dodgeDistanceM });
            }

            void Tick(Input input)
            {
                var player = input.player;
                var obstacles = input.obstacles ?? None;
                switch (state)
                {
                    case "idle":
                        if (armed && Len(Sub(player, Pos)) < c.noticeRadiusM)
                        {
                            if (startedAt == null) startedAt = time;
                            Enter("alert");
                            events.Add(new Event { type = "alert" });
                        }
                        break;
                    case "alert":
                        TurnTowards(player);
                        // A player who ran off holds it here instead of being charged from across the valley.
                        if (Elapsed >= t.alertSeconds && Len(Sub(player, Pos)) < c.noticeRadiusM)
                        {
                            Enter("telegraph");
                            events.Add(new Event { type = "telegraph" });
                        }
                        break;
                    case "telegraph":
                        TurnTowards(player);
                        line = ChargeLine(obstacles, input.bounds);
                        if (Elapsed >= c.pawTelegraphSeconds)
                        {
                            line = ChargeLine(obstacles, input.bounds);
                            line.isFixed = true;
                            chargeFrom = Pos;
                            chargeHit = false;
                            Enter("charge");
                            events.Add(new Event { type = "charge" });
                        }
                        break;
                    case "charge":
                        TickCharge(player, obstacles, input.bounds);
                        break;
                    case "brake":
                        if (Elapsed >= c.brakeRecoverSeconds) { Enter("alert"); events.Add(new Event { type = "alert" }); }
                        break;
                    case "daze":
                        TickDaze(player, input.cleanseHeld, obstacles);
                        break;
                    case "cleansed":
                        if (Elapsed >= t.cleansedStandSeconds) TickFlee(player, obstacles, Elapsed - t.cleansedStandSeconds);
                        break;
                    case "escaped":
                        TickFlee(player, obstacles, Elapsed);
                        if (time >= retryAt)
                        {
                            Reset();
                            startedAt = null;
                            events.Add(new Event { type = "returned" });
                        }
                        break;
                }
            }

            void TurnTowards(P target)
            {
                double want = ToYaw(Sub(target, Pos)), max = c.trackTurnDegPerSecond * Math.PI / 180 * Step;
                double d = Wrap(want - yaw);
                yaw = Wrap(yaw + Math.Max(-max, Math.Min(max, d)));
            }

            P Head()
            {
                var dir = FromYaw(yaw);
                double reach = (t.boarLengthM - t.boarWidthM) / 2;
                return new P(x + dir.x * reach, z + dir.z * reach);
            }

            bool FirstObstacle(IList<Obstacle> obstacles, out Obstacle found)
            {
                P head = Head(), dir = FromYaw(yaw);
                double radius = t.boarWidthM / 2;
                for (int i = 0; i < obstacles.Count; i++)
                {
                    var to = Sub(new P(obstacles[i].x, obstacles[i].z), head);
                    if (Dot(to, dir) > 0 && Len(to) < radius + obstacles[i].r) { found = obstacles[i]; return true; }
                }
                found = default;
                return false;
            }

            bool OutOfBounds(Bounds b)
            {
                if (b == null) return false;
                var h = Head();
                return h.x < b.minX || h.x > b.maxX || h.z < b.minZ || h.z > b.maxZ;
            }

            void TickCharge(P player, IList<Obstacle> obstacles, Bounds bounds)
            {
                var dir = FromYaw(yaw);
                x += dir.x * c.chargeSpeedMps * Step;
                z += dir.z * c.chargeSpeedMps * Step;

                if (!chargeHit && !Invulnerable && Touches(player, dir))
                {
                    chargeHit = true;
                    hits++;
                    double side = Dot(Sub(player, Pos), new P(dir.z, -dir.x)) >= 0 ? 1 : -1;
                    double px = dir.x * .6 + dir.z * side * .8, pz = dir.z * .6 - dir.x * side * .8;
                    double lost = Math.Min(c.hitStaminaLoss, Math.Max(0, stamina - c.staminaFloor));
                    stamina -= lost;
                    events.Add(new Event { type = "hit", x = px * c.hitKnockbackM, z = pz * c.hitKnockbackM, staminaLost = lost, stamina = stamina, hits = hits });
                    if (hits >= c.hitsBeforeEscape) { Escape(); return; }
                }

                if (FirstObstacle(obstacles, out var obstacle))
                {
                    line = null;
                    cleanseHeld = 0;
                    Enter("daze");
                    events.Add(new Event { type = "daze", obstacle = obstacle.id });
                    return;
                }
                if (Len(Sub(Pos, chargeFrom)) >= c.chargeMaxDistanceM || OutOfBounds(bounds))
                {
                    line = null;
                    Enter("brake");
                    events.Add(new Event { type = "brake" });
                }
            }

            // Whether the capsule touches the player.
            bool Touches(P player, P dir)
            {
                double half = (t.boarLengthM - t.boarWidthM) / 2;
                double along = Math.Max(-half, Math.Min(half, Dot(Sub(player, Pos), dir)));
                var closest = new P(x + dir.x * along, z + dir.z * along);
                return Len(Sub(player, closest)) < t.boarWidthM / 2 + t.playerRadiusM;
            }

            void TickDaze(P player, bool held, IList<Obstacle> obstacles)
            {
                if (held && CanCleanse(player))
                {
                    cleanseHeld += Step;
                    if (cleanseHeld >= c.cleanseHoldSeconds - 1e-9)
                    {
                        cleanseHeld = 0;
                        cleanses++;
                        events.Add(new Event { type = "cleanse", count = cleanses });
                        if (cleanses >= c.cleanseNeeded)
                        {
                            PickFlee(player, obstacles);
                            Enter("cleansed");
                            events.Add(new Event { type = CleansedEvent, durationSeconds = time - (startedAt ?? 0), hitsTaken = hits });
                            return;
                        }
                    }
                }
                else cleanseHeld = 0;
                if (Elapsed >= c.dazeSeconds)
                {
                    cleanseHeld = 0;
                    Enter("alert");
                    events.Add(new Event { type = "alert" });
                }
            }

            void Escape()
            {
                line = null;
                retryAt = time + c.retryCooldownSeconds;
                Enter("escaped");
                events.Add(new Event { type = EscapedEvent, hitsTaken = hits });
            }

            // Away from the player, through the widest gap among the obstacles.
            void PickFlee(P player, IList<Obstacle> obstacles)
            {
                P best = default;
                double bestScore = double.NegativeInfinity;
                var away = Sub(Pos, player);
                double awayLen = Math.Max(Len(away), 1e-3);
                for (int i = 0; i < 16; i++)
                {
                    var dir = FromYaw(i / 16.0 * 2 * Math.PI);
                    double clear = t.fleeSpeedMps * t.fleeSeconds;
                    for (int k = 0; k < obstacles.Count; k++)
                    {
                        var to = Sub(new P(obstacles[k].x, obstacles[k].z), Pos);
                        double along = Dot(to, dir), lx = to.x - dir.x * along, lz = to.z - dir.z * along;
                        if (along > 0 && Math.Sqrt(lx * lx + lz * lz) < t.boarWidthM / 2 + obstacles[k].r + .3) clear = Math.Min(clear, along);
                    }
                    double score = clear + Dot(dir, away) / awayLen * 6;
                    if (score > bestScore) { bestScore = score; best = dir; }
                }
                fleeDir = best;
            }

            void TickFlee(P player, IList<Obstacle> obstacles, double fleeing)
            {
                if (!visible) return;
                if (fleeDir == null) PickFlee(player, obstacles);
                var dir = fleeDir.Value;
                yaw = ToYaw(dir);
                x += dir.x * t.fleeSpeedMps * Step;
                z += dir.z * t.fleeSpeedMps * Step;
                if (fleeing >= t.fleeSeconds) { visible = false; events.Add(new Event { type = "gone" }); }
            }

            // Where the charge would go from here: from the boar, up to the first obstacle, the bounds or the maximum distance.
            Line ChargeLine(IList<Obstacle> obstacles, Bounds bounds)
            {
                P dir = FromYaw(yaw), head = Head();
                double radius = t.boarWidthM / 2, length = c.chargeMaxDistanceM;
                for (int i = 0; i < obstacles.Count; i++)
                {
                    var to = Sub(new P(obstacles[i].x, obstacles[i].z), head);
                    double along = Dot(to, dir);
                    if (along <= 0) continue;
                    double lx = to.x - dir.x * along, lz = to.z - dir.z * along, lateral = Math.Sqrt(lx * lx + lz * lz), reach = radius + obstacles[i].r;
                    if (lateral < reach) length = Math.Min(length, Math.Max(0, along - Math.Sqrt(reach * reach - lateral * lateral)));
                }
                if (bounds != null)
                    length = Math.Min(length, Math.Max(0, Math.Min(ToEdge(head.x, dir.x, bounds.minX, bounds.maxX), ToEdge(head.z, dir.z, bounds.minZ, bounds.maxZ))));
                return new Line { x = x, z = z, yaw = yaw, length = length, width = c.chargeLineWidthM, isFixed = false };
            }

            static double ToEdge(double from, double d, double min, double max) => d > 1e-6 ? (max - from) / d : d < -1e-6 ? (min - from) / d : double.PositiveInfinity;
        }
    }
}
