/*
 * App-level build config — structure only, dependencies not added/resolved yet.
 * See ../README.md for the list to add when the team starts real implementation.
 */

android {
    namespace = "com.setu.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.setu.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "0.1"
    }

    buildFeatures {
        compose = true
    }
}
