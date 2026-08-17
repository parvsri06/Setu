package com.setu.app.data.remote

/**
 * Runs when this phone detects real internet connectivity — pushes every
 * locally-held record (including ones that arrived via mesh sync from other
 * devices) up to the backend via ApiService.
 */
class BridgeUploader {
    // TODO: detect connectivity, batch records from SurveyDao, call ApiService.pushBatch().
}
