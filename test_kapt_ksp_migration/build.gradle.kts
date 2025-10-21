plugins {
    id("com.android.application") version "8.1.4" apply false
    id("com.android.library") version "8.1.4" apply false
    id("org.jetbrains.kotlin.android") version "1.8.20" apply false // PROBLEM: Old Kotlin
    id("org.jetbrains.kotlin.kapt") version "1.8.20" apply false // PROBLEM: Should use KSP
    id("com.google.dagger.hilt.android") version "2.48" apply false // PROBLEM: Old Hilt version
    // Missing: id("com.google.devtools.ksp") version "1.9.20-1.0.14" apply false
}

// PROBLEM: buildscript conflicts with plugins block
buildscript {
    dependencies {
        // PROBLEM: Different Hilt version in buildscript vs plugins
        classpath("com.google.dagger:hilt-android-gradle-plugin:2.44") // Older version!

        // PROBLEM: Kotlin version redefined differently
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.8.22") // Different from plugins!
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
        // PROBLEM: JCenter deprecated but still referenced
        jcenter() // Should be removed
    }
}

// PROBLEM: Global dependency versions that conflict with version catalog
subprojects {
    // Force Room version globally - conflicts with libs.versions.toml
    configurations.all {
        resolutionStrategy.force("androidx.room:room-runtime:2.5.2") // Different from 2.6.0 in catalog!

        // Force old Coroutines version - creates conflicts
        resolutionStrategy.force("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.6.1")
    }
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
