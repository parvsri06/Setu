# Bluetooth Mesh — Protocol, Design & Workflows

**Scope note:** Android-only for this build (Nearby Connections API), but the transport is wrapped behind our own interface — so a custom cross-platform BLE protocol can replace it later without touching the sync/merge logic underneath.

---

## 1. Protocol Workflow — the sync handshake between two phones

```mermaid
flowchart LR
    A[Discover nearby devices] --> B[Connect via Nearby Connections]
    B --> C["Exchange manifest<br/>(record keys only, not full data)"]
    C --> D["Compute diff<br/>(what's missing on each side)"]
    D --> E[Transfer missing records]
    E --> F[Merge into local store]
    F --> G[Disconnect]
    G -.->|next encounter| A
```

Every record is uniquely keyed (device ID + local counter) and append-only, so step F is always a simple set union — never a conflict to resolve.

---

## 2. Mesh Design — offline zone bridging to the connected zone

```mermaid
flowchart TB
    subgraph Offline["Offline Mesh Zone — no internet, Bluetooth only"]
        PA[Phone A]
        PB[Phone B]
        PC[Phone C]
        PD["Phone D<br/>(bridge candidate)"]
        PA <--> PB
        PB <--> PC
        PC <--> PD
        PA <--> PD
    end

    subgraph Online["Connected Zone — reached once signal returns"]
        BE[Backend API]
        SAT[Satellite Check]
        DASH[Officer Dashboard]
        BE --> SAT --> DASH
    end

    PD -.->|reaches signal, pushes merged data| BE
```

Any phone in the mesh can become the bridge — there's no fixed "coordinator device." Whichever phone happens to reach signal first is the one that syncs the group's accumulated data to the backend.

---

## 3. Data travel between a room of people — propagation without full connectivity

The point: nobody has to meet everybody directly. Three rounds of pairwise syncs are enough for four people to fully converge.

**Round 1** — A syncs with B, C syncs with D:
```mermaid
flowchart LR
    A1["Phone A: {a1}"] <-->|sync| B1["Phone B: {b1}"]
    C1["Phone C: {c1}"] <-->|sync| D1["Phone D: {d1}"]
```
*Result: A and B both hold {a1,b1}. C and D both hold {c1,d1}.*

**Round 2** — B syncs with C (A and D happen to be out of range this round):
```mermaid
flowchart LR
    A2["Phone A: {a1,b1}"]
    B2["Phone B: {a1,b1}"] <-->|sync| C2["Phone C: {c1,d1}"]
    D2["Phone D: {c1,d1}"]
```
*Result: B and C now hold the full set {a1,b1,c1,d1}. A and D are still partial.*

**Round 3** — A syncs with D:
```mermaid
flowchart LR
    A3["Phone A: {a1,b1}"] <-->|sync| D3["Phone D: {c1,d1}"]
    B3["Phone B: {a1,b1,c1,d1}"]
    C3["Phone C: {a1,b1,c1,d1}"]
```
*Result: A and D now also hold {a1,b1,c1,d1}. All four phones converged — even though A and C never met directly, and B and D never met directly.*

---

## 4. Data updates vs. app version updates — two separate flows, deliberately

**Data updates — automatic, part of normal operation:**
```mermaid
flowchart LR
    Capture[Household captures a record] --> Local[Stored locally]
    Local --> Sync["Synced via Bluetooth<br/>whenever peers are in range"]
    Sync --> Bridge[Bridge phone reaches internet]
    Bridge --> Backend[Pushed to backend]
```

**App version updates — manual and controlled, never automatic:**
```mermaid
flowchart LR
    Build[New APK built by the team] --> Share["Shared by Bluetooth file-transfer<br/>from coordinator / NGO phone"]
    Share --> Install["Manually installed<br/>(unknown sources)"]
    Install --> Notify["Mesh only passes a passive notice:<br/>'newer version available, get it from your coordinator'"]
```

**Why these are separate:** letting phones silently push app *code* to each other over the mesh would let a single compromised device spread malware exactly like it spreads legitimate data. Data sync stays automatic because merging structured records is safe. Code distribution stays manual and controlled because installing software isn't.
