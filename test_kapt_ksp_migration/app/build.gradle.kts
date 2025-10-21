plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt") // PROBLEM: Still using deprecated KAPT
    id("dagger.hilt.android.plugin")
    // Missing KSP plugin that should replace KAPT
}

android {
    namespace = "com.example.brokennav"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.brokennav"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildFeatures {
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.4.3" // OLD VERSION - incompatible
    }
}

dependencies {
    // PROBLEM: Mixed Compose BOM and individual versions
    implementation(platform("androidx.compose:compose-bom:2023.08.00")) // OLD BOM
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3:1.2.0") // Incompatible with old BOM

    // PROBLEM: Navigation version conflicts
    implementation("androidx.navigation:navigation-compose:2.7.5") // Needs newer BOM
    implementation("androidx.navigation:navigation-runtime-ktx:2.7.6") // Different version!

    // PROBLEM: Hilt with KAPT (deprecated)
    implementation("com.google.dagger:hilt-android:2.48") // Old version, limited KSP support
    kapt("com.google.dagger:hilt-compiler:2.48") // Should be ksp()

    // PROBLEM: Room with KAPT
    implementation("androidx.room:room-runtime:2.6.0") // Needs Kotlin 1.9.20+
    implementation("androidx.room:room-ktx:2.6.0")
    kapt("androidx.room:room-compiler:2.6.0") // Should be ksp()

    // PROBLEM: Coroutines version mismatch
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.6.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3") // Different version!

    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
}

// KAPT configuration (should be removed)
kapt {
    correctErrorTypes = true
    useBuildCache = true
}
