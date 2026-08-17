package com.setu.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface SurveyDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertAll(records: List<SurveyRecord>)

    @Query("SELECT * FROM survey_records")
    suspend fun getAll(): List<SurveyRecord>

    // TODO: query by a list of ids, to support RecordMerger's diff() efficiently.
}
