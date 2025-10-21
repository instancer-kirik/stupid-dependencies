plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android") version "1.8.20"
    id("dagger.hilt.android.plugin")
    id("kotlin-kapt")
    id("com.google.devtools.ksp") version "1.8.20-1.0.11"
    kotlin("plugin.serialization") version "1.8.20"
}

android {
    namespace = "com.example.messyproject"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.messyproject"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8  // Outdated Java version
        targetCompatibility = JavaVersion.VERSION_17   // Mismatch!
    }

    kotlinOptions {
        jvmTarget = "1.8"  // Doesn't match targetCompatibility
    }

    buildFeatures {
        compose = true
        dataBinding = true  // Both Compose and DataBinding enabled
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.4.3"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")

    // Compose BOM - good practice
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")

    // Navigation - version conflict
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.6")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.6")
    implementation("androidx.navigation:navigation-compose:2.7.5")  // Different version!

    // MIXED DEPENDENCY INJECTION FRAMEWORKS - MAJOR ISSUE!
    // Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Koin (conflicts with Hilt!)
    implementation("io.insert-koin:koin-android:3.5.0")
    implementation("io.insert-koin:koin-androidx-compose:3.5.0")

    // Room Database - using KAPT instead of KSP (slower)
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")  // Should use KSP for better performance

    // Retrofit with version conflicts
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.retrofit2:converter-kotlinx-serialization:2.11.0")  // Different version!

    // OkHttp version mismatch
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")  // Version mismatch

    // Kotlin libraries with version conflicts
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.8.22")  // Different from plugin version (1.8.20)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.1")  // Version mismatch
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")

    // More annotation processors using KAPT (slow)
    implementation("com.github.bumptech.glide:glide:4.16.0")
    kapt("com.github.bumptech.glide:compiler:4.16.0")  // Could use KSP

    // Data binding processor (redundant with Compose)
    kapt("androidx.databinding:databinding-compiler:8.2.0")

    // Testing dependencies with version conflicts
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.2")  // Different coroutines version
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2023.08.00"))  // Different BOM version!
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")

    // Forced dependency resolution - bad practice
    configurations.all {
        resolutionStrategy {
            force("org.jetbrains.kotlin:kotlin-stdlib:1.8.20")  // Conflicts with explicit version above
        }
    }
}

// KAPT configuration - performance issues
kapt {
    correctErrorTypes = true
    useBuildCache = false  // Bad for performance
    includeCompileClasspath = false
    javacOptions {
        option("-Xmaxerrs", 500)
    }
}

// Issues this build file demonstrates:
// 1. Mixed DI frameworks (Hilt + Koin) - runtime conflicts
// 2. Java version mismatches (sourceCompatibility vs targetCompatibility vs kotlinOptions)
// 3. KAPT usage instead of KSP - slower compilation
// 4. Version conflicts in related libraries (navigation, coroutines, retrofit, okhttp)
// 5. Kotlin plugin version vs stdlib version mismatch
// 6. Both Compose and DataBinding enabled (redundant)
// 7. Different BOM versions in main vs test
// 8. Forced resolution strategy conflicts
// 9. KAPT configuration that hurts performance
// 10. Unused KSP plugin declaration
