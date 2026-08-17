package com.setu.app.ui.capture

import androidx.compose.runtime.Composable

/**
 * Survey capture screen — manual fields (name, household size, notes) plus
 * auto-captured GPS/timestamp/device ID. Never let the user type location
 * or timestamp manually — see shared/record_schema.json's design_rules.
 */
@Composable
fun CaptureScreen() {
    // TODO: build the form UI, wire submit to SurveyDao.insertAll().
}
