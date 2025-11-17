# Notification Specification

## Overview

Complete specification for all email notifications, including German copy, recipients, triggers, and result page text.

**Language:** All user-facing copy in German (informal "du" tone)

**Date Format:** Always "01.–05.08.2025" (DD.–DD.MM.YYYY)

---

## Email Configuration

**From Name:** "Betzenstein App"

**From Address:** `no-reply@<app-domain>`

**Format:**
- HTML primary (dark-mode friendly)
- Plain-text fallback required

**Retry Policy (BR-022):**
- ~3 retry attempts
- Exponential backoff between retries
- Failures logged with correlation IDs
- Content consistent across retries

**Bounces:**
- Log-only (no user notification)
- No automatic cleanup

---

## Action Link Behavior

**Approve Links:**
- One-click (no form required)
- Idempotent
- Always redirect to result page

**Deny Links:**
- Opens comment form
- Comment required (plaintext, no links, ≤500 chars)
- After submit, redirect to result page

**All Action Links:**
- Always redirect to result page (never error inline)
- Show success, "Schon erledigt", or error with context

---

## Notification Triggers & Templates

### 1. Request Submitted

**Trigger:** New booking created

**Recipients:** Approver set (except self-approver if requester is approver)

**Purpose:** Ask for approval decision

**German Template:**
```
Betreff: Neue Buchungsanfrage ({{DateRange}})

Hallo {{ApproverVorname}},

Es gibt eine neue Buchungsanfrage:

Von: {{RequesterVorname}}
Zeitraum: {{DateRange}}
Teilnehmer: {{PartySize}} Personen
{{#if Description}}
Beschreibung: {{Description}}
{{/if}}

Bitte prüf die Anfrage und entscheide.

[Zustimmen]  [Ablehnen (mit Grund)]

---
Zur App: {{AppLink}}
```

**Example:**
```
Betreff: Neue Buchungsanfrage (01.–05.08.2025)

Hallo Cornelia,

Es gibt eine neue Buchungsanfrage:

Von: Anna
Zeitraum: 01.–05.08.2025
Teilnehmer: 3 Personen
Beschreibung: Familienbesuch

Bitte prüf die Anfrage und entscheide.

[Zustimmen]  [Ablehnen (mit Grund)]
```

---

### 2. Approve (Not Final)

**Trigger:** Approver approves, but not all three yet approved

**Recipients:** Requester

**Purpose:** Progress update; show who remains outstanding

**German Template:**
```
Betreff: {{Partei}} hat zugestimmt ({{DateRange}})

Hallo {{RequesterVorname}},

Gute Neuigkeiten! {{Partei}} hat deiner Anfrage für {{DateRange}} zugestimmt.

Ausstehend: {{OutstandingList}}

Sobald alle zugestimmt haben, erhältst du eine Bestätigung.

---
Deine Anfrage ansehen: {{PersonalLink}}
```

**Example:**
```
Betreff: Ingeborg hat zugestimmt (01.–05.08.2025)

Hallo Anna,

Gute Neuigkeiten! Ingeborg hat deiner Anfrage für 01.–05.08.2025 zugestimmt.

Ausstehend: Cornelia und Angelika

Sobald alle zugestimmt haben, erhältst du eine Bestätigung.
```

---

### 3. Final Approval (Confirmed)

**Trigger:** Third and final approver approves

**Recipients:**
- Requester
- All three approvers

**Purpose:** Celebrate confirmation

**Note:** Suppress requester's intermediate "last approver approved" notification (send only this Confirmed email)

**German Template:**
```
Betreff: Buchung bestätigt ({{DateRange}})

Hallo {{Vorname}},

Perfekt! Deine Buchung für {{DateRange}} ist jetzt bestätigt.

Zeitraum: {{DateRange}}
Teilnehmer: {{PartySize}} Personen
{{#if Description}}
Beschreibung: {{Description}}
{{/if}}

Alle haben zugestimmt: Ingeborg, Cornelia und Angelika.

---
{{#if IsRequester}}
Deine Anfrage ansehen: {{PersonalLink}}
{{else}}
Anfrage ansehen: {{ApproverLink}}
{{/if}}
```

**Example:**
```
Betreff: Buchung bestätigt (01.–05.08.2025)

Hallo Anna,

Perfekt! Deine Buchung für 01.–05.08.2025 ist jetzt bestätigt.

Zeitraum: 01.–05.08.2025
Teilnehmer: 3 Personen
Beschreibung: Familienbesuch

Alle haben zugestimmt: Ingeborg, Cornelia und Angelika.
```

---

### 4. Deny (Pending or Confirmed)

**Trigger:** Any approver denies (any state)

**Recipients:** **Requester + all three approvers** (everyone)

**Purpose:** Inform all parties of denial and reason

**German Template:**
```
Betreff: {{Partei}} hat abgelehnt ({{DateRange}})

Hallo {{Vorname}},

{{Partei}} hat die Anfrage für {{DateRange}} abgelehnt.

Von: {{RequesterVorname}}
Zeitraum: {{DateRange}}
Teilnehmer: {{PartySize}} Personen

Grund: {{Kommentar}}

Die Anfrage ist jetzt abgelehnt und nicht mehr öffentlich sichtbar.

{{#if IsRequester}}
Du kannst die Anfrage wieder eröffnen oder stornieren.

[Wieder eröffnen]  [Stornieren]

Deine Anfrage ansehen: {{PersonalLink}}
{{else}}
---
Anfrage ansehen: {{ApproverLink}}
{{/if}}
```

**Example (Requester):**
```
Betreff: Cornelia hat abgelehnt (01.–05.08.2025)

Hallo Anna,

Cornelia hat die Anfrage für 01.–05.08.2025 abgelehnt.

Von: Anna
Zeitraum: 01.–05.08.2025
Teilnehmer: 3 Personen

Grund: Der Zeitraum überschneidet sich leider mit einem anderen Termin.

Die Anfrage ist jetzt abgelehnt und nicht mehr öffentlich sichtbar.

Du kannst die Anfrage wieder eröffnen oder stornieren.

[Wieder eröffnen]  [Stornieren]
```

**Example (Approver):**
```
Betreff: Cornelia hat abgelehnt (01.–05.08.2025)

Hallo Ingeborg,

Cornelia hat die Anfrage für 01.–05.08.2025 abgelehnt.

Von: Anna
Zeitraum: 01.–05.08.2025
Teilnehmer: 3 Personen

Grund: Der Zeitraum überschneidet sich leider mit einem anderen Termin.

Die Anfrage ist jetzt abgelehnt und nicht mehr öffentlich sichtbar.
```

---

### 5. Edit: Shorten Dates (No Re-Approval)

**Trigger:** Requester shortens dates within original bounds while Pending

**Recipients:** Requester

**Purpose:** Acknowledge change; no re-approval needed

**German Template:**
```
Betreff: Daten aktualisiert ({{NewDateRange}})

Hallo {{RequesterVorname}},

Deine Anfrage wurde aktualisiert.

Alter Zeitraum: {{OldDateRange}}
Neuer Zeitraum: {{NewDateRange}}

Die bisherigen Zustimmungen bleiben erhalten.

---
Deine Anfrage ansehen: {{PersonalLink}}
```

**Example:**
```
Betreff: Daten aktualisiert (03.–08.08.2025)

Hallo Anna,

Deine Anfrage wurde aktualisiert.

Alter Zeitraum: 01.–10.08.2025
Neuer Zeitraum: 03.–08.08.2025

Die bisherigen Zustimmungen bleiben erhalten.
```

---

### 6. Edit: Extend Dates (Re-Approval Required)

**Trigger:** Requester extends dates (earlier start or later end) while Pending

**Recipients:** Approver set (all three)

**Purpose:** Request re-approval with clear diff

**German Template:**
```
Betreff: Termine geändert – bitte neu bestätigen ({{NewDateRange}})

Hallo {{ApproverVorname}},

{{RequesterVorname}} hat die Anfrage angepasst und benötigt eine neue Bestätigung.

Alter Zeitraum: {{OldDateRange}}
Neuer Zeitraum: {{NewDateRange}}
Teilnehmer: {{PartySize}} Personen

Bitte prüf die Änderung und entscheide erneut.

[Zustimmen]  [Ablehnen (mit Grund)]

---
Anfrage ansehen: {{ApproverLink}}
```

**Example:**
```
Betreff: Termine geändert – bitte neu bestätigen (28.07.–12.08.2025)

Hallo Cornelia,

Anna hat die Anfrage angepasst und benötigt eine neue Bestätigung.

Alter Zeitraum: 01.–10.08.2025
Neuer Zeitraum: 28.07.–12.08.2025
Teilnehmer: 3 Personen

Bitte prüf die Änderung und entscheide erneut.

[Zustimmen]  [Ablehnen (mit Grund)]
```

---

### 7. Reopen (From Denied to Pending)

**Trigger:** Requester reopens denied booking

**Recipients:** Approver set (all three)

**Purpose:** Request fresh approval

**German Template:**
```
Betreff: Wieder eröffnet – bitte neu prüfen ({{DateRange}})

Hallo {{ApproverVorname}},

{{RequesterVorname}} hat eine abgelehnte Anfrage wieder eröffnet.

Zeitraum: {{DateRange}}
Teilnehmer: {{PartySize}} Personen
{{#if Description}}
Beschreibung: {{Description}}
{{/if}}

{{#if DatesChanged}}
Änderung:
Alter Zeitraum: {{OldDateRange}}
Neuer Zeitraum: {{NewDateRange}}
{{/if}}

Bitte prüf die Anfrage erneut und entscheide.

[Zustimmen]  [Ablehnen (mit Grund)]

---
Anfrage ansehen: {{ApproverLink}}
```

**Example (with date change):**
```
Betreff: Wieder eröffnet – bitte neu prüfen (10.–15.08.2025)

Hallo Ingeborg,

Anna hat eine abgelehnte Anfrage wieder eröffnet.

Zeitraum: 10.–15.08.2025
Teilnehmer: 3 Personen
Beschreibung: Familienbesuch (angepasster Termin)

Änderung:
Alter Zeitraum: 01.–05.08.2025
Neuer Zeitraum: 10.–15.08.2025

Bitte prüf die Anfrage erneut und entscheide.

[Zustimmen]  [Ablehnen (mit Grund)]
```

---

### 8. Cancel: Pending or Confirmed

**Trigger:** Requester cancels booking (Pending or Confirmed state)

**Recipients:** **Requester + all three approvers**

**Purpose:** Confirm cancellation; list who was notified

**German Template:**
```
Betreff: Buchung storniert ({{DateRange}})

Hallo {{Vorname}},

Die {{#if WasConfirmed}}bestätigte {{/if}}Buchung von {{RequesterVorname}} für {{DateRange}} wurde storniert.

Benachrichtigt: Ingeborg, Cornelia und Angelika.

{{#if Kommentar}}
Grund: {{Kommentar}}
{{/if}}

{{#unless IsRequester}}
---
Anfrage ansehen: {{ApproverLink}}
{{/unless}}
```

**Example (Pending cancel):**
```
Betreff: Buchung storniert (01.–05.08.2025)

Hallo Cornelia,

Die Buchung von Anna für 01.–05.08.2025 wurde storniert.

Benachrichtigt: Ingeborg, Cornelia und Angelika.
```

**Example (Confirmed cancel with comment):**
```
Betreff: Buchung storniert (01.–05.08.2025)

Hallo Anna,

Die bestätigte Buchung von Anna für 01.–05.08.2025 wurde storniert.

Benachrichtigt: Ingeborg, Cornelia und Angelika.

Grund: Pläne haben sich kurzfristig geändert.
```

---

### 9. Cancel: Denied

**Trigger:** Requester cancels already-denied booking

**Recipients:** **Requester only** (approvers already informed by Deny email)

**Purpose:** Quiet confirmation to requester

**German Template:**
```
Betreff: Buchung storniert ({{DateRange}})

Hallo {{RequesterVorname}},

Die abgelehnte Buchung für {{DateRange}} wurde von dir storniert.

{{#if Kommentar}}
Grund: {{Kommentar}}
{{/if}}
```

**Example:**
```
Betreff: Buchung storniert (01.–05.08.2025)

Hallo Anna,

Die abgelehnte Buchung für 01.–05.08.2025 wurde von dir storniert.
```

---

### 10. Personal Link Recovery

**Trigger:** User requests link via "Ist das deine Anfrage?" flow

**Recipients:** Email provided (if exists in system)

**Purpose:** Resend personal link (neutral copy, no enumeration)

**German Template:**
```
Betreff: Zugangslink

Hallo,

Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt.

{{#if HasBookings}}
Deine Anfragen ansehen: {{PersonalLink}}
{{/if}}

Kommt nichts an? Prüfe die Schreibweise deiner E-Mail-Adresse oder schau in deinem Spam-Ordner nach.

---
Betzenstein App
```

**Note:** Same copy sent whether email exists or not (no enumeration per BR-021)

---

### 11. Weekly Digest

**Trigger:** Sunday 09:00 Europe/Berlin (BR-009)

**Recipients:** Per-approver (only if they have items meeting criteria)

**Purpose:** Remind of outstanding approvals aged ≥5 days

**Inclusion Criteria:**
- Booking status = Pending
- This approver's decision = NoResponse
- Age ≥5 calendar days (day-0: submission date)
- Future-only (exclude past-dated)

**Ordering:** By soonest start date

**Suppression:** If zero items, digest not sent

**German Template:**
```
Betreff: Ausstehende Anfragen – Wochenübersicht

Hallo {{ApproverVorname}},

Du hast {{Count}} ausstehende Buchungsanfrage{{#if Plural}}n{{/if}}, die auf deine Entscheidung warten:

{{#each Items}}
---
Von: {{RequesterVorname}}
Zeitraum: {{DateRange}}
Teilnehmer: {{PartySize}} Personen
{{#if Description}}
Beschreibung: {{Description}}
{{/if}}
Ausstehend seit: {{DaysAgo}} Tagen

[Zustimmen]  [Ablehnen (mit Grund)]
{{/each}}

---
Alle Anfragen ansehen: {{ApproverOverviewLink}}
```

**Example:**
```
Betreff: Ausstehende Anfragen – Wochenübersicht

Hallo Cornelia,

Du hast 2 ausstehende Buchungsanfragen, die auf deine Entscheidung warten:

---
Von: Anna
Zeitraum: 15.–20.08.2025
Teilnehmer: 3 Personen
Beschreibung: Familienbesuch
Ausstehend seit: 6 Tagen

[Zustimmen]  [Ablehnen (mit Grund)]

---
Von: Max
Zeitraum: 01.–03.09.2025
Teilnehmer: 2 Personen
Ausstehend seit: 5 Tagen

[Zustimmen]  [Ablehnen (mit Grund)]

---
Alle Anfragen ansehen: [Link]
```

---

## Result Pages (After Action Links)

Users always redirected to result page after clicking action link. Never show error inline in email.

### Success: Approve (Not Final)

**German Copy:**
```
Danke – du hast zugestimmt.

Status: Ausstehend: {{OutstandingList}}

[Zur Übersicht]
```

**Example:**
```
Danke – du hast zugestimmt.

Status: Ausstehend: Cornelia und Angelika

[Zur Übersicht]
```

---

### Success: Approve (Final - All Confirmed)

**German Copy:**
```
Danke – du hast zugestimmt.

Alles bestätigt! Die Buchung ist jetzt komplett bestätigt.

[Zur Übersicht]
```

---

### Success: Deny

**German Copy:**
```
Erledigt – du hast abgelehnt.

Die Anfrage ist jetzt abgelehnt und nicht mehr öffentlich sichtbar.

[Zur Übersicht]
```

---

### Success: Cancel (Pending or Confirmed)

**German Copy:**
```
Anfrage storniert.

Benachrichtigt: {{NotifiedList}}

[Zur Übersicht]
```

**Example:**
```
Anfrage storniert.

Benachrichtigt: Ingeborg, Cornelia und Angelika.

[Zur Übersicht]
```

---

### Success: Cancel (Denied)

**German Copy:**
```
Anfrage storniert.

[Zur Übersicht]
```

---

### Already Done: Denied First

**Scenario:** User tries to approve/deny, but someone else already denied

**German Copy:**
```
Schon erledigt.

{{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich).

[Zur Übersicht]
```

**Example:**
```
Schon erledigt.

Cornelia hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich).

[Zur Übersicht]
```

---

### Already Done: Generic

**Scenario:** User tries action, but booking already in terminal/incompatible state

**German Copy:**
```
Schon erledigt.

Aktueller Stand: {{StatusDescription}}

[Zur Übersicht]
```

**Examples:**
```
Schon erledigt.

Die Buchung ist bereits bestätigt.

[Zur Übersicht]
```

```
Schon erledigt.

Diese Anfrage ist bereits storniert.

[Zur Übersicht]
```

---

### Error (Fallback)

**Scenario:** Unexpected error during action processing

**German Copy:**
```
Uups – da lief was schief.

Bitte öffne die App und führe die Aktion dort aus.

[Zur App öffnen]
```

---

## Lost-Link Recovery Responses

### Success (Generic)

**UI Copy (shown in popup after submit):**
```
Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt.

Kommt nichts an? Prüfe die Schreibweise oder deinen Spam-Ordner.

[OK]
```

---

### Cooldown Active

**UI Copy (shown if 60s cooldown active per BR-021):**
```
Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet.

[OK]
```

---

## Email Copy Guidelines

### Tone
- Informal "du" form (not "Sie")
- Friendly but professional
- Clear and direct
- Positive framing where possible

### Formatting
- Short paragraphs
- Bullet points or structured info
- Clear CTAs (buttons/links)
- Whitespace for readability

### Accessibility
- Plain language
- Avoid jargon
- Clear action labels
- No ambiguous pronouns

### Dark Mode
- Test HTML emails in dark mode
- Avoid pure white backgrounds
- Ensure button contrast
- Test color combinations

---

## Notification Summary Table

| Trigger | Recipients | Key Content |
|---------|-----------|-------------|
| Submitted | Approvers (not self) | New request; dates, party size |
| Approve (not final) | Requester | Progress; who's outstanding |
| Final approval | Requester + Approvers | Celebration; confirmed |
| Deny (any state) | **Everyone** (Req + 3 Approvers) | Reason; now denied (not public) |
| Edit: Shorten | Requester | Ack change; approvals kept |
| Edit: Extend | Approvers | Re-approval needed; diff |
| Reopen | Approvers | Fresh approval; diffs if changed |
| Cancel (Pending/Confirmed) | **Requester + 3 Approvers** | Confirm cancel; list notified |
| Cancel (Denied) | **Requester only** | Quiet confirmation |
| Weekly Digest | Per-approver (if items) | Outstanding aged ≥5d, future-only |
| Link Recovery | Provided email (if exists) | Neutral; no enumeration |

---

## Implementation Notes

### Email Service
- Use reliable ESP (SendGrid, AWS SES, etc.)
- Configure SPF/DKIM/DMARC
- Monitor delivery rates
- Log all sends with correlation IDs

### Template Engine
- Use variables for dynamic content ({{VariableName}})
- Support conditionals ({{#if}}, {{#unless}})
- Support loops ({{#each}})
- Escape HTML properly

### Testing
- Test all templates with real data
- Verify German characters (ä, ö, ü, ß) render correctly
- Test plain-text fallback
- Test dark mode appearance
- Test mobile email clients

### Monitoring
- Track open rates (optional)
- Monitor bounce rates
- Log retry attempts
- Alert on high failure rates
