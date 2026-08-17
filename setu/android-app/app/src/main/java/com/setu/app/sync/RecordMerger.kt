package com.setu.app.sync

import com.setu.app.data.local.SurveyRecord

/**
 * Core merge logic — Kotlin port of mesh_sync_simulation.py.
 * Every record is uniquely keyed by (device_id, local_counter) and
 * append-only, so merging two devices' record sets is a simple set union,
 * never a conflict to resolve.
 */
class RecordMerger {

    fun manifest(records: List<SurveyRecord>): Set<String> {
        return records.map { "${it.deviceId}:${it.localCounter}" }.toSet()
    }

    fun diff(myKeys: Set<String>, theirKeys: Set<String>): Set<String> {
        return theirKeys - myKeys
    }

    // TODO: merge(missingRecords: List<SurveyRecord>) — insert into Room via SurveyDao.
    // See mesh_sync_simulation.py's sync_with() for the reference logic.
}
