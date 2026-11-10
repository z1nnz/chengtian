using QingxiWorld;
using UnityEngine;

namespace YunJing
{
    // Small HUD for interior scenes: where you are, what F does here, and the last result.
    public sealed class QingxiInteriorHud : MonoBehaviour
    {
        public string place = "借住處";
        public QingxiAbcStations stations;
        public QingxiTrainingPractice training;

        static GUIStyle title, body, centre;
        string lastLog; float logUntil;

        static void Styles()
        {
            if (title != null) return;
            var cream = new Color(.96f, .94f, .86f);
            title = new GUIStyle(GUI.skin.label) { fontSize = 26, alignment = TextAnchor.UpperLeft, wordWrap = false };
            if (QingxiFonts.Title != null) title.font = QingxiFonts.Title;
            body = new GUIStyle(GUI.skin.label) { fontSize = 16, alignment = TextAnchor.UpperLeft, wordWrap = true };
            centre = new GUIStyle(GUI.skin.label) { fontSize = 17, alignment = TextAnchor.MiddleCenter, wordWrap = true };
            title.normal.textColor = body.normal.textColor = centre.normal.textColor = cream;
        }

        // Words on the scene itself: a soft shadow in place of a box.
        static void Shadowed(Rect r, string text, GUIStyle style)
        {
            var colour = GUI.color;
            GUI.color = new Color(0, 0, 0, .75f);
            GUI.Label(new Rect(r.x + 1.2f, r.y + 1.2f, r.width, r.height), text, style);
            GUI.color = colour;
            GUI.Label(r, text, style);
        }

        static void Wash(Rect r, float alpha)
        {
            var colour = GUI.color;
            GUI.color = new Color(.03f, .05f, .06f, alpha);
            GUI.DrawTexture(r, Texture2D.whiteTexture);
            GUI.color = colour;
        }

        /// <summary>One line of speech or a result, low in the middle of the screen (IMGUI; call from OnGUI).</summary>
        public static void Subtitle(string text, float up = 0)
        {
            QingxiFonts.ApplyImgui();
            Styles();
            float scale = Mathf.Clamp(Screen.height / 720f, .7f, 2f);
            var previous = GUI.matrix;
            GUI.matrix = Matrix4x4.Scale(Vector3.one * scale);
            float w = Screen.width / scale, h = Screen.height / scale;
            var r = new Rect(w * .5f - 360, h - 150 - up, 720, 60);
            Wash(r, .5f);
            Shadowed(new Rect(r.x + 20, r.y + 4, r.width - 40, r.height - 8), text, centre);
            GUI.matrix = previous;
        }

        void OnGUI()
        {
            QingxiFonts.ApplyImgui();
            var walker = QingxiFirstPerson.Current;
            if (walker == null || (training != null && training.Active)) return;
            Styles();
            float scale = Mathf.Clamp(Screen.height / 720f, .7f, 2f);
            var previous = GUI.matrix;
            GUI.matrix = Matrix4x4.Scale(Vector3.one * scale);
            float w = Screen.width / scale, h = Screen.height / scale;
            Shadowed(new Rect(28, 22, 480, 38), place, title);
            var today = QingxiNoviceDays.Objective;
            if (today != null) Shadowed(new Rect(30, 62, 520, 26), "◆  " + today, body);
            string prompt = stations != null ? stations.Prompt(walker.transform.position) : null;
            if (!string.IsNullOrEmpty(prompt))
            {
                var r = new Rect(w * .5f - 220, h - 84, 440, 38);
                Wash(r, .55f);
                Shadowed(r, prompt, centre);
            }
            GUI.matrix = previous;
            // The last result; the walker's own notes about teleports and markers are for review, not for play.
            string log = walker.LastLog;
            if (log != lastLog) { lastLog = log; logUntil = Time.unscaledTime + 6; }
            if (!string.IsNullOrEmpty(log) && Time.unscaledTime < logUntil && !log.StartsWith("傳送到") && !log.StartsWith("到達")) Subtitle(log, -8);
        }
    }
}
