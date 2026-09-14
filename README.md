# Mehfil · backend

Firebase is the backend for both apps: **Firebase Authentication** (Sign in with Apple, Google) and
**Cloud Firestore** (per-vendor data, offline persistence, security rules). There is no server to run — this
folder holds the rules, the data model both apps implement, and the setup steps.

- `firestore.rules` — only the signed-in owner can read or write `vendors/{uid}` and its subcollections.
- `DATA_MODEL.md` — the document shapes shared by `mehfil-ios` and `mehfil-android`.
- `PRIVACY.md`, `TERMS.md` — the policy pages the apps and store listings link to.
- `branding/` — the app icon. `mehfil-icon.svg` is the master (brand mesh of indigo, magenta and ruby under a gold
  ribbon M with a sparkle); `make_icon.py` renders it with macOS QuickLook and writes every raster the stores ask
  for — `mehfil-icon-1024.png` (App Store), `mehfil-icon-512.png` (Play), `mehfil-icon-120.png` (Google consent
  screen), `mehfil-feature-1024x500.png` (Play feature graphic) — plus the Xcode AppIcon and the Android
  adaptive-icon layers (mesh background, mark foreground, white monochrome for themed icons). Edit the SVG, re-run
  the script, rebuild both apps.

## One-time setup (about 30 minutes)

### 1 · Firebase project
1. [console.firebase.google.com](https://console.firebase.google.com) → **Add project** → name it `mehfil` (Analytics optional).
2. **Build → Authentication → Get started → Sign-in method**: enable **Google** (set the support email) and **Apple**.
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

### 3 · Android app
1. Project settings → **Add app → Android**, package `com.mehfil.app`. Add your **SHA-1 and SHA-256** fingerprints:
   ```bash
   # debug keystore
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android | grep -E "SHA1|SHA256"
   ```
   and later the **Play App Signing** fingerprints from Play Console → Setup → App signing.
2. Download `google-services.json` into `mehfil-android/app/` (git-ignored; the Gradle build applies the
   google-services plugin only when the file exists).
3. Sign in with Apple on Android uses Firebase's web flow. In Apple Developer → Certificates, IDs & Profiles →
   **Services IDs** create one (e.g. `com.anish.mehfil.web`), enable Sign in with Apple, set the return URL to
   `https://<your-project>.firebaseapp.com/__/auth/handler`, and paste the Services ID + key into
   Firebase → Authentication → Apple provider (OAuth code flow configuration).

### 4 · Google Cloud consent screen
Firebase creates the OAuth clients. In Google Cloud Console → APIs & Services → OAuth consent screen: set the app
name, support email, the logo (`branding/mehfil-icon-120.png`), add the privacy-policy URL, and publish (External → In production) so any Google account can sign in.

### 5 · Store listings
- Privacy policy URL (both stores): `https://github.com/Sanu5/mehfil-ios/blob/main/PRIVACY.md` (or host `PRIVACY.md` on your own domain).
- App Store: **Sign in with Apple** is required because Google sign-in is offered — done. Account deletion is in
  Profile → Account, as guideline 5.1.1(v) requires. App Privacy answers: Email, Name, Other user content —
  linked to the user, not used for tracking (matches `PrivacyInfo.xcprivacy`).
- Play: Data safety form — collects Email address, Name, App activity (user-generated content); encrypted in
  transit; users can request deletion in-app. Target API 36.

## Running without Firebase
Both apps run in **device-only** mode when the config file is missing: a "Continue on this device" account with
local storage, so the whole product can be used and reviewed before the project is wired up. Cloud sign-in
buttons appear automatically once the config file is present.
