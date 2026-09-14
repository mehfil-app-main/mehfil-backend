# Mehfil · Firestore data model

Both apps read and write exactly this shape. All documents live under `vendors/{uid}` where `uid` is the
Firebase Auth user id. Dates are Firestore `Timestamp`s, money is an integer number of rupees, enums are the
lower-case strings listed. Document ids are opaque strings (the apps generate 20-char ids; the sample season
uses readable ones).

## vendors/{uid}  — profile
| field | type | notes |
|---|---|---|
| ownerName, businessName, phone, area, since | string | `since` is free text ("since 2018") |
| upi, bankLabel | string | bankLabel is a display label only, never an account number |
| seasonTarget | int | rupees |
| lastSeasonBooked, lastSeasonEvents | int, optional | for the season comparison card |
| notifyPayments, notifyConflicts, notifyChanges | bool | |
| createdAt | timestamp | |

## Subcollections
| collection | fields |
|---|---|
| `clients` | id, name, phone, isRepeat (bool), avatar (int 1–8), createdAt |
| `events` | id, name, clientId, type (`sangeet|mehendi|reception|haldi|nikah|engagement`), start, end (timestamps), venue {name, area, hall?}, guests, quoted, hue (int 1–4), status (`upcoming|completed|cancelled`), crewAssigned, crewNeeded, crewPlan?, inventorySummary?, createdAt |
| `milestones` | id, eventId, name, amount, due (timestamp), status (`paid|pending|overdue`), kind (`advance|instalment|balance|settlement`), paidOn?, method? (`upi|bank|cash|cheque`), reference? |
| `crew` | id, name, role (`coordinator|decorator|helper`), isLead, dayRate, avatar? (int), bookings (array of event ids), note? |
| `attendance` | id = eventId, states (map crewId → `confirmed|arrived|absent`) |
| `inventory` | id, name, total, detail, holds (array of {eventId, qty, date}) |
| `tasks` | id, eventId, block, blockTime, title, crew, duration, done (bool), order (int) |
| `reminders` | id, milestoneId, tone (`gentle|standard|firm`), channel (`whatsapp|sms`), sentAt, outcome |
| `expenses` | id, eventId, name, detail, amount |
| `enquiries` | id, name, phone, source, budget, date?, guests, notes, status (`open|converted|closed`), createdAt |
| `packages` | id, name, detail, price |
| `changeRequests` | id, eventId, summary, guestsDelta, impacts (array of {resource, detail, delta, isShort, icon}), addedCost, revisedQuote, perGuest, status (`pending|approved|declined`), requestedAt, via |

Derived, never stored: overdue (pending milestone with `due` before today), crew conflicts (a crew member whose
`bookings` contain two events that overlap in time), payment state on event cards, season totals.

Optional fields are omitted from the document when absent (iOS) or written as `null` (Android); both readers accept either.

## Phone numbers
- `vendors/{uid}.phone` is stored in **E.164** (`+919811008123`) once verified; `phoneVerified: boolean` records that
  an OTP confirmed it and the number is linked to the Firebase user (`user.phoneNumber`). A number can only reach
  the profile through the OTP flow (sign in with phone, or link/update from onboarding, Account and Business details).
  Device-only builds store whatever was typed with `phoneVerified: false`.
- Client phone numbers (`clients/{id}.phone`) are entered by the vendor and not verified.
