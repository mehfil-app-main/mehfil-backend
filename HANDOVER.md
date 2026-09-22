# Mehfil — handover

Everything a buyer receives, and every account that has to change hands. Written so the transfer is a
checklist rather than a negotiation.

---

## 1 · What is being sold

| Repository | Contents |
|---|---|
| `mehfil-ios` | SwiftUI app, iOS 26+, Liquid Glass. 24 screens. |
| `mehfil-android` | Kotlin + Jetpack Compose (Material 3), min SDK 26. The same 24 screens. |
| `mehfil-backend` | Firestore rules, the shared data model, branding assets, policies, store guides. No server. |
| `sanu5.github.io` | The marketing homepage, privacy policy, terms and account-deletion page (GitHub Pages). |
| `mehfil-design` | The 92-artboard design wall, `tokens.css`, and `NOTES.md` — the design reasoning. |

Both apps are feature-complete against the product spec, build clean, and run today in **device-only mode**
with no backend configured — a buyer can open either project and see the whole product working in ten minutes.

**Start with [`NOTES.md`](https://github.com/Sanu5/mehfil-design/blob/main/NOTES.md).** It is the most
substantial document in the sale: six phases of design decisions, every derivation from the source design
system, the rulings that were applied in review, and the full skin migration from the first visual language to
the current one — with the measurements that forced each change. The code is a translation of that document.

---

## 2 · Identifiers that transfer

| Thing | Current value | How it moves |
|---|---|---|
| iOS bundle id | `com.anish.mehfil` | See §3 — the buyer should re-namespace. |
| Android application id | `com.mehfil.app` | Neutral already; can be kept as-is. |
| Firebase project | `mehfil-567fb` (see `.firebaserc`, untracked) | Transfer ownership, or the buyer creates their own — §4. |
| Marketing site | `https://sanu5.github.io/` | Buyer hosts the same files on their own domain — §5. |
| Support email | `biswalworkanish@gmail.com` | Replace throughout — §5. |
| Android upload keystore | `mehfil-release.jks` (untracked, never committed) | §6. |
| Apple App ID / Services ID | not yet created | §3. |

---

## 3 · iOS: bundle id and signing

The bundle id is `com.anish.mehfil` — it carries the seller's name and **should not** transfer. The app has
never been submitted to App Store Connect, so nothing is bound to it yet and renaming is free:

1. Xcode → target **Mehfil** → Signing & Capabilities → **Bundle Identifier** → e.g. `com.buyerco.mehfil`.
   (One place; `PRODUCT_BUNDLE_IDENTIFIER` appears twice in `project.pbxproj`, Debug and Release.)
2. Select the buyer's **Team**. Xcode registers the App ID and enables **Sign in with Apple** on it.
3. Add an iOS app with the new bundle id in the buyer's Firebase project and drop in the new
   `GoogleService-Info.plist` (§4).
4. `run-on-device.sh` takes `BUNDLE_ID` as an environment variable, so device testing needs no edit.

**Capabilities used:** Sign in with Apple only. There is no push, no background mode, no App Group, no
iCloud container — nothing that complicates a team transfer. A free personal team can build and run the app
with `./run-on-device.sh`, which swaps in empty entitlements and hides the Apple button.

---

## 4 · Firebase

Two clean options. **Option B is recommended** — it leaves the seller with nothing to keep paying for and the
buyer with an account in their own name.

### Option A · Transfer the existing project
1. Firebase console → ⚙ **Users and permissions** → add the buyer's Google account as **Owner**.
2. Google Cloud console → **IAM** → remove the seller's account once the buyer confirms access.
3. Billing: the buyer attaches their own billing account (Google Cloud → Billing → *Change billing*).
4. The buyer re-downloads `GoogleService-Info.plist` and `google-services.json` — the files are git-ignored and
   are **not** part of the sale.

### Option B · Buyer creates a fresh project (recommended)
Follow `backend/README.md` end to end — about 30 minutes. It produces a project with no history, no leftover
test users and billing in the buyer's name from the first day. Then:
```bash
cd backend && cp .firebaserc.example .firebaserc && firebase use --add && firebase deploy --only firestore:rules
```

Either way the buyer must register their own **SHA fingerprints** (debug and Play App Signing) for Google
sign-in on Android, and publish their own **OAuth consent screen**.

### What is in the database today
Only the seller's own test vendor under `vendors/{uid}`. There is no customer data, so no data-protection
obligation travels with the sale. The seller deletes that account from Profile → Account → Delete account at
handover, leaving the project empty.

---

## 5 · Strings the buyer must replace

All of these are deliberately in one place each:

| What | Where |
|---|---|
| Privacy / terms / deletion URLs | `PRIVACY_URL`, `TERMS_URL` in `ui/screens/AuthScreens.kt`; the two `Link`s in `AuthViews.swift`; `site/` |
| Support email | `site/*.html`, `backend/PRIVACY.md`, `backend/TERMS.md`, `LICENSE` |
| Marketing site | `site/` — plain HTML, no build step. Point a domain at it or copy into any host. |
| Store copy | `backend/STORE_COPY.md` |
| Copyright holder | `LICENSE` in every repository |

---

## 6 · Android signing

The upload keystore (`android/mehfil-release.jks`) and `android/keystore.properties` are **git-ignored and were
never committed**. The app has not been uploaded to Play, so no key is yet bound to a listing and **the buyer
should generate their own**:

```bash
cd android && keytool -genkeypair -v -keystore mehfil-release.jks -alias mehfil -keyalg RSA -keysize 2048 -validity 10000
```

then create `keystore.properties` as `backend/PLAY_STORE.md` describes. If the seller has already published,
the keystore file and its passwords must transfer instead, out of band — never in the repository.

---

## 7 · Third-party dependencies and their licences

Nothing in the stack is commercially restricted; there are no paid SDKs and no per-seat licences.

| Dependency | Licence | Notes |
|---|---|---|
| Firebase iOS SDK / Android BOM | Apache 2.0 | Free tier; Blaze only if the buyer adds features that need it |
| GoogleSignIn-iOS, Credential Manager, googleid | Apache 2.0 | |
| AndroidX / Jetpack Compose | Apache 2.0 | |
| Inter typeface | SIL Open Font License 1.1 | `OFL-Inter.txt` ships in both apps |
| Google "G" mark | Google brand guidelines | Used only on its own sign-in button, as required |

Running costs at launch scale: **zero**. Firebase's free tier covers authentication and a small Firestore
workload; the only unavoidable costs are the Apple Developer Program ($99/yr) and the Play Console ($25 once).

---

## 8 · Repository history and exposure — stated plainly

A buyer will check this, so it is documented rather than glossed.

- The four repositories were **public from 14 September 2026**. GitHub's traffic API records, over the
  following 14 days: `mehfil-ios` 48 clones / 29 unique, `mehfil-android` 28 / 12, `mehfil-backend` 23 / 11,
  `sanu5.github.io` 21 / 9 — almost all on the publication day itself, against 0–1 page views. That pattern is
  the signature of automated crawlers rather than people, and **there are zero forks on any repository**. But it
  cannot be proven that no human took a copy.
- There was **no `LICENSE` file** during that window. Under the Berne Convention and GitHub's own terms,
  publishing source code grants no licence: absent an explicit grant, all rights are reserved. Anyone holding a
  clone has **no right to use, modify or distribute it**. A `LICENSE` stating exactly that is now in every
  repository.
- Making the repositories private before the sale is recommended, and the seller should do it:
  ```bash
  for r in mehfil-ios mehfil-android mehfil-backend mehfil-design; do gh repo edit Sanu5/$r --visibility private --accept-visibility-change-consequences; done
  ```
  (Leave `sanu5.github.io` public — GitHub Pages needs it, and it contains only the marketing site.)
- **What can honestly be sold is full copyright ownership and an exclusive, unrestricted licence** — not a
  guarantee that no copy exists anywhere. Any listing claiming "never been public" would be false and is the
  kind of thing a buyer discovers with one API call.
- The commit history is short and dense: the apps were built in a small number of long sessions. This is
  visible and should not be dressed up. The substance is in `NOTES.md`, the token system and the 92 artboards —
  the code is downstream of a design process that is fully documented.

---

## 9 · Handover checklist

- [ ] Repositories transferred (`gh repo transfer`, or a fresh push into the buyer's org)
- [ ] `LICENSE` copyright line updated to the buyer
- [ ] Firebase: project transferred or recreated; seller's IAM access removed
- [ ] Seller's test vendor account deleted from the database
- [ ] Bundle id re-namespaced; buyer's Apple team selected
- [ ] Buyer's SHA fingerprints registered; OAuth consent screen published under the buyer's brand
- [ ] `site/` rehosted on the buyer's domain; all four URLs updated in both apps
- [ ] Support email replaced in the apps, policies and store listings
- [ ] Android keystore generated by the buyer (or transferred out of band if already published)
- [ ] Seller's Google, Apple and GitHub accounts removed from every surface
