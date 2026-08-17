package com.setu.app.sync

import com.setu.app.mesh.MeshTransport

/**
 * Orchestrates a full sync cycle: discovery -> connect -> exchange manifest
 * -> diff -> transfer -> merge -> disconnect. Owns a MeshTransport but
 * doesn't care which implementation it's given.
 */
class SyncManager(private val transport: MeshTransport) {
    // TODO: wire transport callbacks to RecordMerger and SurveyDao.
}
