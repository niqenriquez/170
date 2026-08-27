# Daily Project Reminder (Telegram)

Sends you Telegram messages **3 times a day** — morning, afternoon, evening:
- **Morning**: how many days are left in the year + today's focus
- **Afternoon**: a check-in on today's focus
- **Evening**: a wrap-up prompt

All content comes from `topics.json`. Runs for free on a schedule via GitHub Actions — no server needed.

## 1. Create your Telegram bot

1. In Telegram, message **@BotFather**.
2. Send `/newbot`, follow the prompts, and name it whatever you like.
3. BotFather will give you a **bot token** — looks like `123456789:ABCdefGhIJKlmNoPQRstuVwxyZ`. Save it.
4. Start a chat with your new bot (search its username, hit Start, send it any message — e.g. "hi").

## 2. Get your chat ID

1. Visit this URL in your browser (replace `<TOKEN>` with your bot token):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
2. Find `"chat":{"id":123456789,...}` in the response — that number is your **chat ID**.
   (If you see nothing, make sure you've sent the bot a message first, then refresh.)

## 3. Fill in your project topics

Edit `topics.json`. Keys are dates in `MM-DD` format (no year — repeats every year). Each date maps to an object with `morning`, `afternoon`, and `evening` messages:

```json
{
  "default": {
    "morning": "No specific focus set for today — pick something and go.",
    "afternoon": "Checking in — how's today's focus coming along?",
    "evening": "Wrap-up time — how did today go?"
  },
  "08-17": {
    "morning": "Work on the marketing site redesign.",
    "afternoon": "Have you finished the homepage mockup yet?",
    "evening": "Reflect: what's left on the redesign for tomorrow?"
  }
}
```

- `"default"` is used for any date you haven't filled in, or any slot you leave out for a specific date.
- You don't need every day filled in — just add what matters.
- You can omit a slot (e.g. just set `"morning"`) and it'll fall back to the default message for that slot.

### Writing longer messages

JSON strings can't contain real line breaks, so a long pep talk written across
several lines in the file will make `topics.json` invalid. Instead of cramming it
onto one unreadable line, write the slot as a **list of lines** — each line stays
on its own row in the file, and they're joined with line breaks when sent. Use `""`
for a blank line between paragraphs:

```json
"08-28": {
  "morning": [
    "Hey Atlas. Today is a new day. You have a choice to make.",
    "Are you going to let the past define your future?",
    "",
    "Todays workout is Chest, Triceps, and Shoulders.",
    "",
    "other things to consider:",
    "- send rent to Julie if you haven't already"
  ],
  "afternoon": "Short ones can stay a plain string.",
  "evening": "Make oatmeal for Friday's breakfast."
}
```

Both forms work anywhere, so use a plain string for one-liners and a list when you
want room to write. Watch for two things inside the quotes: a `"` needs to be
written `\"`, and a `\` needs to be written `\\`. Apostrophes are fine as-is.

## 4. Put this on GitHub

1. Create a new **private** GitHub repository.
2. Push these files (`send_reminder.py`, `topics.json`, `requirements.txt`, `.github/workflows/daily-reminder.yml`) to it.

```bash
cd daily-reminder
git init
git add .
git commit -m "Daily reminder bot"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 5. Add your secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

Add two secrets:
- `TELEGRAM_BOT_TOKEN` → your bot token from step 1
- `TELEGRAM_CHAT_ID` → your chat ID from step 2

## 6. Test it

Go to the **Actions** tab in your repo → **Daily Project Reminder** workflow → **Run workflow**. You'll see a dropdown to pick which slot to test (`morning`, `afternoon`, or `evening`) — pick one and run it. You should get a Telegram message within a few seconds. Repeat for the other two slots if you want to check all three.

## 7. Adjust the send times (optional)

The workflow runs 3 times a day, set (by default) to roughly:
- 7:00 AM Pacific → morning
- 1:00 PM Pacific → afternoon
- 8:00 PM Pacific → evening

Edit the three `cron` lines in `.github/workflows/daily-reminder.yml` if you want different times. Cron schedules in GitHub Actions are always in **UTC**, so convert your desired local time to UTC first. If you change a cron line, also update the matching line in the "Determine which slot to send" step so it still maps to the right slot — the two need to stay in sync.

Note: Pacific Time shifts between PDT (UTC-7, summer) and PST (UTC-8, winter). The times above assume PDT; during PST everything will land about an hour later than intended unless you adjust the cron hours seasonally.

## 8. Workout split auto-sync from Apple Notes (optional)

Apple Notes has no public API a cloud script can query directly, so this uses an **iPhone Shortcut** to push your note's text to GitHub, which then feeds into your morning message automatically.

### 8a. Create a GitHub token

1. On GitHub, go to **Settings** (your account, top-right avatar → Settings) → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
2. Give it a name like `workout-shortcut`, set an expiration (e.g. 1 year).
3. Under **Repository access**, choose **Only select repositories** → pick this repo.
4. Under **Permissions** → **Repository permissions**, set **Contents** to **Read and write**.
5. Generate the token and copy it somewhere safe — you'll paste it into the Shortcut and won't see it again.

### 8b. Build the iPhone Shortcut

In the **Shortcuts** app, create a new shortcut with these actions in order:

1. **Find Notes** (or **Get Note**) — set it to find the specific note where you keep your workout split (e.g. by name).
2. **Get Contents of URL**:
   - URL: `https://api.github.com/repos/<your-username>/<your-repo>/dispatches`
   - Method: `POST`
   - Headers:
     - `Accept`: `application/vnd.github+json`
     - `Authorization`: `Bearer <your-token-from-8a>`
     - `Content-Type`: `application/json`
   - Request Body (JSON):
     ```json
     {
       "event_type": "update-workout",
       "client_payload": { "note_text": "[Note text from step 1]" }
     }
     ```
     (Use the Shortcuts app's variable picker to insert the note's text into `note_text` rather than typing it literally.)

3. Run the Shortcut once manually to test — check the **Actions** tab in your GitHub repo, you should see an "Update Workout Split" run, and `workout.txt` in your repo should update with your note's content.

### 8c. Automate it

In the Shortcuts app, go to **Automation** → **Create Personal Automation** → **Time of Day**, set it for whenever you update your workout note (e.g. the night before, or first thing in the morning before your 7am message goes out). Choose **Run Immediately** (not "Ask Before Running") if you want it fully hands-off — iOS may still occasionally prompt for confirmation on automations that touch certain apps.

Once this is set up, your morning Telegram message will automatically include whatever's currently in that note — no manual JSON editing needed for workouts.

## What's next (not yet built)

- **Teams calendar integration** — pulling your actual meeting schedule into the message. This needs a Microsoft Graph API app registration (OAuth), which is more involved — happy to build this next once the workout flow is confirmed working.
- **AI-generated messages** — instead of static/templated text, using the Claude API to turn raw inputs (workout note, calendar, leftover notes) into a naturally-written daily message, so you're not hand-structuring `topics.json` as much. This can layer on top of what's here now.

## Updating topics later

Just edit `topics.json` and push — no need to touch anything else. You can add entries for as many days as you want, whenever you want.

## Notes

- GitHub Actions free tier includes plenty of minutes for a job this small (well under a minute per run) — this will cost nothing.
- Scheduled workflows can occasionally fire a few minutes late during high GitHub load — not exact-to-the-second, but reliably within the same morning window.
