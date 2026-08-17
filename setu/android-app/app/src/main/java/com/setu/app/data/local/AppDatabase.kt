package com.setu.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [SurveyRecord::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun surveyDao(): SurveyDao
}
