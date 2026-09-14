# Publishing Mehfil on Google Play

Everything below is specific to this project. Assets referenced live in `branding/`.

## 0 · Before you start
- **Google Play Console account** — [play.google.com/console/signup](https://play.google.com/console/signup), one-time US$25, and
  identity verification (ID document; usually a day, sometimes longer). Choose *Personal* unless you have a
  registered business — a personal account can be converted later.
- A personal account created after November 2023 must run a **closed test with at least 12 testers for 14 days**
  before it can release to production. Plan for that: start the closed test the same day you get the account.
- `android/app/google-services.json` must be present when you build (it is git-ignored, so on a fresh clone copy it in).

## 1 · Release keystore (once, keep it forever)
```bash
cd "/Users/anish/Desktop/Vibe Coding/Test/mehfil/android" && "/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/keytool" -genkeypair -v -keystore mehfil-release.jks -alias mehfil -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Anish Biswal, O=Mehfil, L=Gurugram, C=IN"
```
It asks for a keystore password (then re-enter). Create `android/keystore.properties`:
```
storeFile=mehfil-release.jks
storePassword=<the password>
keyAlias=mehfil
keyPassword=<the password>
```
Both files are git-ignored. **Back up `mehfil-release.jks` and the password somewhere safe** (a password manager
plus a cloud drive) — this is the *upload key*; Play App Signing lets you reset it if lost, but only after a support
request.

Register the upload key in Firebase too (so a locally installed release build can use Google sign-in):
```bash
cd "/Users/anish/Desktop/Vibe Coding/Test/mehfil/android" && "/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/keytool" -list -v -keystore mehfil-release.jks -alias mehfil | grep -E "SHA1|SHA256"
```
Firebase → Project settings → Android app → **Add fingerprint** → paste both.

## 2 · Build the App Bundle
```bash
cd "/Users/anish/Desktop/Vibe Coding/Test/mehfil/android" && JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home" ./gradlew bundleRelease
```
Output: `app/build/outputs/bundle/release/app-release.aab` (signed with the upload key, R8-minified, resources shrunk).
Each new upload needs a higher `versionCode` in `app/build.gradle.kts` (`versionName` is what users see).

Optional sanity check of the exact release build on the emulator:
```bash
cd "/Users/anish/Desktop/Vibe Coding/Test/mehfil/android" && JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home" ./gradlew assembleRelease && ~/Library/Android/sdk/platform-tools/adb install -r app/build/outputs/apk/release/app-release.apk
```

## 3 · Create the app in Play Console
**All apps → Create app**: name `Mehfil`, default language English (India), *App*, *Free*, tick the declarations → Create.

## 4 · Dashboard → "Set up your app" (every task must be green)
| Task | Answer |
|---|---|
| Privacy policy | `https://sanu5.github.io/privacy/` |
| App access | *All or some functionality is restricted* → add instruction: "Sign in with any Google account; no special credentials needed. A sample season loads on first sign-in so every screen has data." |
| Ads | No ads |
| Content rating | Start questionnaire → email → category **Utility, Productivity, Communication, or Other** → answer No to everything → rating *Everyone* |
| Target audience | Age **18 and over** · not designed for children |
| News app | No |
| COVID-19 contact tracing | No |
| Data safety | see below |
| Government app | No |
| Financial features | *My app doesn't provide any financial features* (Mehfil records amounts; it does not move money) |
| Health | No health features |
| Store listing | see §5 |

**Data safety** — "Does your app collect or share user data?" **Yes**. Encrypted in transit: **Yes**. Deletion:
**Yes**, in-app (Profile → Account → Delete account) and at `https://sanu5.github.io/delete-account/`.
Data types (all *Collected*, not shared, not processed ephemerally, purpose **App functionality** + **Account management**):
- Personal info → **Name**, **Email address** (required, from Apple/Google sign-in), **Phone number** (optional, the vendor's own and clients' numbers they enter)
- Financial info → **Other financial info** (optional, payment records the vendor enters)
- App activity → **Other user-generated content** (optional, events, crew, inventory, notes)

Nothing else is collected (no location, contacts, photos, device IDs, crash logs or analytics).

## 5 · Store listing (Grow → Store presence → Main store listing)
- **App name**: `Mehfil`
- **Short description** (≤ 80): `Wedding-vendor operations: calendar, payments, crew and inventory in one app.`
- **Full description**: see `STORE_COPY.md`
- **App icon**: `branding/mehfil-icon-512.png`
- **Feature graphic**: `branding/mehfil-feature-1024x500.png`
- **Phone screenshots**: the six files in `branding/screenshots/play/` (1080×1920). Tablet screenshots are optional;
  if the form insists, upload the same six.
- **Category**: Business · **Tags**: Productivity, Business management
- **Contact details**: email `biswalworkanish@gmail.com`, website `https://sanu5.github.io/`
- Store settings → app category Business.

## 6 · Testing tracks, then production
1. **Test and release → Internal testing → Create new release** → upload `app-release.aab`. On the first upload
   Play asks you to enrol in **Play App Signing** — accept (Google re-signs with its own key; you keep uploading with yours).
   Release notes: `First release.` → Save → Review → **Start rollout to Internal testing**. Add your own email under
   *Testers* → copy the opt-in link → install from Play on your phone and sign in.
2. **Copy the Play App Signing SHA-256 to Firebase** — Test and release → **Setup → App signing** → *App signing key
   certificate* → SHA-256 → Firebase → Project settings → Android app → Add fingerprint. Without this, Google sign-in
   fails in every Play-distributed build (error 10).
3. **Closed testing** → Create track *Beta* → promote the internal release → add testers (an email list of ≥ 12 people
   who each install and keep it for 14 days; a Google Group is easiest). Start rollout.
4. After 14 days: Dashboard → **Apply for production access** → answer the short questionnaire (what you tested,
   what feedback you got, how the app is ready). Approval usually takes a few days.
5. **Production → Create new release** → promote the closed-test build (or upload a newer bundle with a higher
   `versionCode`) → Countries: India (add others as you like) → Review → **Start rollout to Production**. First reviews
   take from a few hours to about a week.

## 7 · Every update afterwards
Bump `versionCode` (and `versionName`), `./gradlew bundleRelease`, Production → Create new release → upload → rollout.
Keep the keystore. Keep `google-services.json` in `app/`.
