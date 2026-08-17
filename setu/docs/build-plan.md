# Setu — Build Plan (7 Days)

**Assumptions baked into this plan — check these before sharing with the team:**
- Working name: **Setu** (from our naming discussion — swap it out everywhere if you land on something else)
- Scope this week: **survey capture + offline Bluetooth mesh sync only**. Damage assessment (photos/satellite), SOS signal, and message-level encryption are explicitly OUT of scope this week — add-on features "if selected," not part of this prototype.
- Timeline: 7 days, ending with a working live demo + recorded backup
- Process changes included: Day 1 team walkthrough, a shared task board, daily 10–15 min standups, a fixed daily Q&A window for you, researchers doubling as dev-unblockers

**Phases are gated by working features, not just the calendar.** Each phase has a specific, testable success condition. Don't move to the next phase until the current one's gate is actually met — if Day 3 ends and the gate isn't hit, Day 4 stays on fixing it rather than starting new work.

---

## Phase 0 — Kickoff & Foundation (Day 1)

**Gate to exit:** Record schema locked in writing. All 4 devs have working local environments. Shared board is live with Day 2 tasks on it.

**You (Leader / Bluetooth):**
- Morning: run the 30-min whole-team architecture walkthrough — use the mesh design doc, show everyone the full picture before anyone starts coding solo.
- Set up the shared board (sheet, Trello, whatever the team already knows) with To Do / Doing / Done / Blocked columns.
- Fix a daily standup time and your own daily Q&A window — protect the rest of your day for Bluetooth work.
- Afternoon: set up the Android Studio project, add the Nearby Connections dependency, sanity-check that two test phones can discover each other using Google's own sample app before writing any real sync logic.

**Backend:**
- Set up the FastAPI project skeleton, confirm it runs locally.
- Draft a Pydantic model for the survey record — bring it to the schema-lock discussion, don't finalize it alone.
- Read: FastAPI's official tutorial (path params, request bodies, Pydantic models).

**Frontend:**
- Set up the Android Studio project with Compose, confirm an empty app builds and runs on a real device.
- Sketch the capture screen fields (manual details + auto-captured GPS/timestamp/device ID).
- Read: Jetpack Compose state basics (`remember`, `mutableStateOf`); skim the CameraX quickstart.

**Database:**
- Lead the schema-lock discussion today — this is the day's priority. Fields at minimum: `id`, `device_id`, `local_counter`, survey detail fields, `lat`, `lon`, `timestamp`.
- Set up a local Postgres instance (Docker is fine) for testing.
- Read: PostGIS basics — `geometry(Point, 4326)` type, `ST_DWithin`.

**Researchers:**
- Sit in on the schema-lock discussion so the PPT stays accurate to what's actually being built.
- Start the PPT skeleton: problem statement + solution overview (we already have sourced content for this).
- Double-check any stats already being cited.

**Evening standup:** confirm schema is written down somewhere everyone can see, environments work, board has Day 2 tasks.

---

## Phase 1 — Bluetooth Core Proof (Day 2–3)

**Gate to exit:** Two physical Android phones, both in airplane mode, discover each other via Nearby Connections and exchange one dummy record — verified across at least 5 repeated runs. This is the single most important gate in the whole project; don't rush past it.

**Day 2**
- *You:* implement basic advertising/discovery + connection (P2P_CLUSTER strategy) between two real test phones. Use real devices, not emulators — Bluetooth doesn't work reliably in an emulator.
- *Backend:* build the `POST /records/batch` endpoint skeleton, test it manually with dummy JSON matching the locked schema.
- *Frontend:* build the capture screen UI — no DB wiring yet, just get the fields and layout right.
- *Database:* finalize the Room entity definitions and hand them to frontend; finalize and apply the Postgres DDL.
- *Researchers:* draft the "why this and not another flood app" slide; set up a placeholder architecture slide.

**Day 3**
- *You:* get an actual dummy record transferred between the two connected phones with airplane mode on. Run it repeatedly, log success rate. This is today's gate-check task.
- *Backend:* add the hash-chain function (`sha256(record + previous_hash)`) with a couple of unit tests.
- *Frontend:* wire the capture screen to the local Room database now that entities exist.
- *Database:* support any schema mismatches that show up during integration.
- *Researchers:* check in briefly with the dev team to keep the PPT's technical claims accurate; help backend/frontend look up anything they're stuck on.

**Evening Day 3 gate check:** did two phones reliably exchange a record in airplane mode? If not, Day 4 stays on fixing this specifically before Phase 2 work starts.

---

## Phase 2 — Full Mesh Sync + Capture Integration (Day 4–5)

**Gate to exit:** A record captured on Phone A shows up correctly on Phone B *and* Phone C after a few rounds of pairwise sync, fully offline, zero duplicates — recreate the room-propagation scenario from the design doc.

**Day 4**
- *You:* port the manifest-diff merge logic into Kotlin, wired to Room; test with 2 phones first.
- *Backend:* finish the batch ingestion endpoint fully — validate, insert into Postgres, apply the hash-chain.
- *Frontend:* finish wiring the capture screen fully — a captured record should now actually persist locally.
- *Database:* watch for real insert issues during backend integration; start designing basic indexes.
- *Researchers:* update the architecture slide with what's actually real now, not just planned.

**Day 5**
- *You:* extend the test to 3 phones (borrow one), verify convergence against the room-propagation model — note how many sync rounds it took.
- *Backend:* add a basic status-check endpoint (mocked data is fine for now).
- *Frontend:* add the sync-status indicator, now backed by real data.
- *Database:* add indexes, run a basic load test with a batch of dummy records.
- *Researchers:* draft every remaining PPT slide except results/demo (that comes after Phase 3).

**Evening Day 5 gate check:** 3-phone offline convergence demonstrated reliably?

---

## Phase 3 — Bridge to Backend (Day 6)

**Gate to exit:** A phone that "comes online" pushes its full merged record set to the backend and it lands correctly in Postgres — test at least 3 times, including two bridge phones with overlapping data, confirming no duplicates land centrally.

- *You:* implement the bridge trigger — detect connectivity, push local records to the backend.
- *Backend:* add dedup logic (reject records whose key already exists), test the overlapping-push scenario specifically.
- *Frontend:* build a minimal data viewer — a simple list pulling from the backend, just enough to prove the loop closes. Doesn't need to be a polished dashboard.
- *Database:* add a unique constraint on `(device_id, local_counter)` as a safety net; finalize load test results.
- *Researchers:* start pulling real screenshots into the architecture and results slides.

**Evening gate check:** full loop confirmed — offline capture → mesh sync → bridge → backend → visible centrally?

---

## Phase 4 — Polish & Demo Prep (Day 7)

**Gate:** none technical — this is about being ready, not building something new.

- *Whole dev team:* morning bug bash, fix anything broken from Day 6's integration.
- *You:* rehearse the live 2-phone airplane-mode demo at least 3 times; record a clean backup video in case live Bluetooth misbehaves on stage.
- *Researchers:* finalize the PPT completely, rehearse the pitch narrative with whoever presents.
- *Everyone:* final sync — no pending known bugs, and agree on the answer if judges ask about scope: "damage assessment, satellite verification, and SOS are designed for the next phase; this week we proved the offline mesh sync actually works."
