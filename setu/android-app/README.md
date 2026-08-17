# Setu Android App

Kotlin + Jetpack Compose. Structure only — no dependencies resolved yet,
most files are stubs with `TODO`s.

## Package layout (`app/src/main/java/com/setu/app/`)

- `mesh/` — **Bluetooth transport layer.** `MeshTransport.kt` is the interface
  everything else in the app depends on. `NearbyConnectionsTransport.kt` is
  the only file that should import anything from
  `com.google.android.gms.nearby.*` — this is deliberate, so swapping in a
  custom cross-platform BLE protocol later means replacing this one file,
  not rewriting the sync logic.
- `sync/` — the merge logic (manifest, diff, merge) and the orchestrator
  that drives a full sync cycle. Port of `mesh_sync_simulation.py`.
- `data/local/` — Room entities and DAOs, matches `../database/local_schema.md`.
- `data/remote/` — talks to the backend once a phone is online (the "bridge" role).
- `ui/` — Compose screens.

## Dependencies to add when the team is ready to actually build (not yet)
- `androidx.compose.*`
- `androidx.room:room-runtime`, `room-ktx`
- `com.google.android.gms:play-services-nearby`
- `androidx.camera:camera-camera2`, `camera-lifecycle`, `camera-view`
- `com.google.android.gms:play-services-location`
- `com.squareup.retrofit2:retrofit`, `converter-gson`
