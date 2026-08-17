package com.setu.app.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room entity — matches ../../../../../../shared/record_schema.json and
 * ../../../../../../database/local_schema.md. If you change a field here,
 * update both of those and tell the team.
 */
@Entity(tableName = "survey_records")
data class SurveyRecord(
    @PrimaryKey val id: String,           // deviceId:localCounter
    val deviceId: String,
    val localCounter: Int,
    val capturedAt: String,               // ISO 8601
    val latitude: Double,
    val longitude: Double,
    val surveyDataJson: String,           // JSON-encoded survey fields
    val recordHash: String
)
