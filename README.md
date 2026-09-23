# Mehfil · backend

Firebase is the backend for both apps: **Firebase Authentication** (Sign in with Apple, Google) and
**Cloud Firestore** (per-vendor data, offline persistence, security rules). There is no server to run — this
folder holds the rules, the data model both apps implement, and the setup steps.

- `firestore.rules` — only the signed-in owner can read or write `vendors/{uid}` and its subcollections.
- `DATA_MODEL.md` — the document shapes shared by `mehfil-ios` and `mehfil-android`.
- `PRIVACY.md`, `TERMS.md` — the policy pages the apps and store listings link to.
- `branding/` — the app icon. `mehfil-icon.svg` is the master (a rani-pink gradient under a ribbon M whose second
  half folds into gold); `make_icon.py` renders it with macOS QuickLook and writes every raster the stores ask
  for — `mehfil-icon-1024.png` (App Store), `mehfil-icon-512.png` (Play), `mehfil-icon-120.png` (Google consent
  screen), `mehfil-feature-1024x500.png` (Play feature graphic) — plus the Xcode AppIcon and the Android
  adaptive-icon layers (gradient background, mark foreground, white monochrome for themed icons). Edit the SVG, re-run
  the script, rebuild both apps. `make_screenshots.py` frames the raw captures in `branding/screenshots/raw/` into
  1080×1920 listing images (`branding/screenshots/play/`) with the captions from `captions.txt`.

## One-time setup (about 30 minutes)

### 1 · Firebase project
1. [console.firebase.google.com](https://console.firebase.google.com) → **Add project** → name it `mehfil` (Analytics optional).
2. **Build → Authentication → Get started → Sign-in method**: enable **Google** (set the support email), **Apple** and
   **Phone**. Phone sign-in sends real SMS, which needs the project on the **Blaze (pay as you go)** plan — the free
   allowance covers a small app; add a budget alert. While Phone is open, add a **phone number for testing**
   (e.g. `+91 98765 43210` → code `123456`) so the simulator, the emulator and store reviewers can sign in without an SMS.
3. **Build → Firestore Database → Create database** → production mode → region `asia-south1` (Mumbai).
4. Deploy the rules from this folder:
   ```bash
   npm install -g firebase-tools && firebase login
   cp .firebaserc.example .firebaserc   # put your project id in it
   firebase deploy --only firestore:rules
   ```

### 2 · iOS app
1. Project settings → **Add app → iOS**, bundle id `com.anish.mehfil`. Download `GoogleService-Info.plist` and
   drop it into `mehfil-ios/Mehfil/` (it is git-ignored; the Xcode build picks it up automatically and registers
   the Google URL scheme from it).
2. In Xcode: Signing & Capabilities → your team; the **Sign in with Apple** capability is already in
   `Mehfil.entitlements` — Xcode will register it on the App ID.
3. Firebase → Authentication → Apple provider needs nothing extra for native iOS sign-in.
4. **Phone sign-in on iOS** verifies the app with a silent push. Apple Developer → **Keys → +** → tick *Apple Push
   Notifications service (APNs)* → Register → download the `.p8`, note the Key ID. Firebase → Project settings →
   **Cloud Messaging** → *Apple app configuration* → **Upload** the key with Key ID and Team ID. (Without it Firebase
   falls back to a reCAPTCHA page, which works but is uglier.) The Push Notifications capability is already in
   `Mehfil.entitlements`; Xcode enables it on the App ID when you pick your team.

### 3 · Android app
1. Project settings → **Add app → Android**, package `com.mehfil.app`. Add your **SHA-1 and SHA-256** fingerprints:
   ```bash
   # debug keystore
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android | grep -E "SHA1|SHA256"
   ```
   and later the **Play App Signing** fingerprints from Play Console → Setup → App signing.
2. Download `google-services.json` into `mehfil-android/app/` (git-ignored; the Gradle build applies the
   google-services plugin only when the file exists).
3. **Phone sign-in on Android** verifies the app with the Play Integrity API: Google Cloud Console → APIs & Services
   → Library → **Play Integrity API** → Enable (same project). Both SHA fingerprints from step 1 must be registered.
   Builds installed on the emulator use the test numbers instead.
4. Sign in with Apple on Android uses Firebase's web flow. In Apple Developer → Certificates, IDs & Profiles →
   **Services IDs** create one (e.g. `com.anish.mehfil.web`), enable Sign in with Apple, set the return URL to
   `https://<your-project>.firebaseapp.com/__/auth/handler`, and paste the Services ID + key into
   Firebase → Authentication → Apple provider (OAuth code flow configuration).

### 4 · Website, then the Google consent screen
Google only accepts a privacy-policy URL and homepage on a domain you can prove you own, so the policy pages live
on GitHub Pages at **https://sanu5.github.io/** (repo `Sanu5/sanu5.github.io`, source in the `site` folder
of this workspace). Verify that domain once in Search Console (see the site README), then in Google Cloud Console
→ Google Auth Platform → **Branding**: app name, support email, logo (`branding/mehfil-icon-120.png`),
homepage `https://sanu5.github.io/`, privacy `https://sanu5.github.io/privacy/`, terms
`https://sanu5.github.io/terms/`, authorized domain `sanu5.github.io`; then **Audience → Publish** (External → In
production) so any Google account can sign in.

### 5 · Store listings
- Privacy policy URL (both stores): `https://sanu5.github.io/privacy/`.
- App Store: **Sign in with Apple** is required because Google sign-in is offered — done. Account deletion is in
  Profile → Account, as guideline 5.1.1(v) requires. App Privacy answers: Email, Name, Other user content —
  linked to the user, not used for tracking (matches `PrivacyInfo.xcprivacy`).
- Play: Data safety form — collects Email address, Name, Phone number, Other financial info (payment records the
  vendor enters) and Other user-generated content; encrypted in transit; not shared; deletion in-app and at
  `https://sanu5.github.io/delete-account/`. Target API 36. Full walkthrough: `PLAY_STORE.md`.

## Running without Firebase
Both apps run in **device-only** mode when the config file is missing: a "Continue on this device" account with
local storage, so the whole product can be used and reviewed before the project is wired up. Cloud sign-in
buttons appear automatically once the config file is present.
