plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android") version "1.8.20"
    id("dagger.hilt.android.plugin")
    id("kotlin-kapt")
    id("com.google.devtools.ksp") version "1.8.20-1.0.11"
}

android {
    compileSdk 34

    defaultConfig {
        applicationId "com.example.stupiddependencies"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_17  // VERSION MISMATCH!
    }

    kotlinOptions {
        jvmTarget = "1.8"  // ALSO MISMATCHED WITH TARGET!
    }

    buildFeatures {
        dataBinding = true
        compose = true  // BOTH DATABINDING AND COMPOSE!
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.4.3"
    }
}

dependencies {
    // MIXED DEPENDENCY INJECTION FRAMEWORKS - CRITICAL CONFLICT!
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")

    implementation("io.insert-koin:koin-android:3.5.0")  // CONFLICTS WITH HILT!
    implementation("io.insert-koin:koin-core:3.5.0")

    // ROOM WITH KAPT INSTEAD OF KSP - PERFORMANCE ISSUE!
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")  // SHOULD USE KSP FOR BETTER PERFORMANCE!

    // VERSION CONFLICTS IN NAVIGATION
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.6")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.6")
    implementation("androidx.navigation:navigation-compose:2.7.5")  // DIFFERENT VERSION!

    // KOTLIN STANDARD LIBRARY VERSION MISMATCH
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.8.22")  // PLUGIN IS 1.8.20!

    // COROUTINES VERSION CONFLICTS
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")  // DIFFERENT!
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.6.4")     // EVEN OLDER!

    // OKHTTP VERSION CONFLICTS
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")  // OLDER VERSION!

    // COMPOSE BOM BUT OVERRIDDEN VERSIONS - DEFEATS THE PURPOSE
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui:1.5.4")  // OVERRIDES BOM!
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3:1.1.2")  // OVERRIDES BOM!

    // GLIDE WITH KAPT WHEN KSP IS AVAILABLE
    implementation("com.github.bumptech.glide:glide:4.16.0")
    kapt("com.github.bumptech.glide:compiler:4.16.0")  // SHOULD USE KSP!

    // LIFECYCLE COMPONENTS WITH VERSION MISMATCHES
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.6.2")  // DIFFERENT VERSION!
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")

    // TESTING
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}

// KAPT CONFIGURATION ISSUES
kapt {
    correctErrorTypes = true
    useBuildCache = false  // PERFORMANCE ISSUE - SHOULD BE TRUE!

    arguments {
        arg("room.schemaLocation", "$projectDir/schemas")
    }
}

// KSP IS CONFIGURED BUT NOT USED!
ksp {
    arg("room.schemaLocation", "$projectDir/schemas")
}
