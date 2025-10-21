plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.kotlin.spring)
    alias(libs.plugins.kotlin.jpa)
    alias(libs.plugins.spring.boot)
    alias(libs.plugins.spring.dependency.management)
    alias(libs.plugins.ksp)
    application
}

group = "com.example.modern"
version = "0.1.0-SNAPSHOT"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

kotlin {
    jvmToolchain(17)
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
        freeCompilerArgs.addAll(
            "-Xjsr305=strict",
            "-Xjvm-default=all"
        )
    }
}

repositories {
    mavenCentral()
    maven {
        url = uri("https://repo.spring.io/milestone")
    }
}

dependencies {
    // Use BOM for consistent versions
    implementation(platform(libs.kotlin.bom))
    implementation(platform(libs.spring.cloud.dependencies))

    // Kotlin libraries - versions managed by BOM
    implementation(libs.kotlin.stdlib)
    implementation(libs.kotlin.reflect)

    // Spring Boot bundles
    implementation(libs.bundles.spring.boot.web)
    implementation(libs.bundles.database)

    // Kotlinx libraries bundle
    implementation(libs.bundles.kotlin.coroutines)
    implementation(libs.kotlinx.serialization.json)

    // Jackson bundle with consistent versions
    implementation(libs.bundles.jackson)

    // Arrow functional programming
    implementation(libs.bundles.arrow)

    // Logging bundle
    implementation(libs.bundles.logging)

    // KSP processors
    ksp(libs.spring.boot.configuration.processor)

    // Test dependencies
    testImplementation(libs.bundles.testing)
    testImplementation(libs.bundles.testcontainers)
}

tasks.test {
    useJUnitPlatform()
}

tasks.bootJar {
    archiveBaseName.set("modern-kotlin-app")
    archiveVersion.set("")
}

application {
    mainClass.set("com.example.modern.ApplicationKt")
}

// This demonstrates best practices:
// 1. All plugins use version catalog
// 2. Consistent Java/Kotlin toolchain configuration
// 3. BOM usage for version management
// 4. Dependency bundles for related libraries
// 5. No version conflicts
// 6. Modern Gradle/Kotlin DSL patterns
