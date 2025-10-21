plugins {
    kotlin("jvm") version "1.9.20"
    kotlin("plugin.serialization") version "1.9.20"
    kotlin("plugin.spring") version "1.9.20"
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
    id("org.jetbrains.kotlin.plugin.jpa") version "1.9.20"
    id("com.google.devtools.ksp") version "1.9.20-1.0.14"
    id("org.gradle.toolchains") version "0.4.0"
    application
}

group = "com.example.complex"
version = "0.1.0-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_21  // Mismatch: different source/target
}

kotlin {
    jvmToolchain(19)  // Mismatch: toolchain vs sourceCompatibility
}

repositories {
    mavenCentral()
    maven {
        url = uri("https://repo.spring.io/milestone")
    }
    maven {
        url = uri("https://oss.sonatype.org/content/repositories/snapshots/")
    }
}

configurations {
    all {
        exclude(group = "org.springframework.boot", module = "spring-boot-starter-logging")
        resolutionStrategy {
            force("org.jetbrains.kotlin:kotlin-stdlib:1.8.22")  // Force old version
            failOnVersionConflict()
        }
    }
}

dependencies {
    // Kotlin stdlib version mismatch
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.8.22")
    implementation("org.jetbrains.kotlin:kotlin-reflect:1.9.20")

    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-actuator")

    // Jackson with Kotlin module
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.15.2")
    implementation("com.fasterxml.jackson.core:jackson-core:2.14.1")  // Version conflict

    // Kotlinx libraries
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-reactor:1.6.4")  // Version mismatch
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")

    // Database
    implementation("org.springframework.boot:spring-boot-starter-data-r2dbc")
    implementation("io.r2dbc:r2dbc-postgresql:0.8.13.RELEASE")
    implementation("org.postgresql:postgresql:42.6.0")

    // Logging - conflicting with Spring Boot exclusion
    implementation("ch.qos.logback:logback-classic:1.4.8")
    implementation("org.slf4j:slf4j-api:2.0.7")

    // Arrow for functional programming
    implementation("io.arrow-kt:arrow-core:1.2.1")
    implementation("io.arrow-kt:arrow-fx-coroutines:1.2.1")

    // KSP processors
    ksp("org.springframework.boot:spring-boot-configuration-processor")

    // Test dependencies with version conflicts
    testImplementation("org.springframework.boot:spring-boot-starter-test") {
        exclude(group = "org.junit.vintage", module = "junit-vintage-engine")
    }
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5:1.9.0")  // Version mismatch
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("io.mockk:mockk:1.13.5")
    testImplementation("com.ninja-squad:springmockk:4.0.2")
    testImplementation("org.testcontainers:junit-jupiter:1.19.0")
    testImplementation("org.testcontainers:postgresql:1.19.0")
    testImplementation("org.testcontainers:r2dbc:1.19.0")

    // BOM imports that might conflict
    implementation(platform("org.springframework.cloud:spring-cloud-dependencies:2023.0.0"))
    implementation(platform("org.jetbrains.kotlin:kotlin-bom:1.9.10"))  // Different version

    // Annotation processors
    annotationProcessor("org.springframework.boot:spring-boot-configuration-processor")
    kapt("org.springframework.boot:spring-boot-configuration-processor")  // Both kapt and ksp
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        jvmTarget = "17"  // Doesn't match toolchain
        freeCompilerArgs = listOf(
            "-Xjsr305=strict",
            "-Xjvm-default=all",
            "-Xopt-in=kotlin.RequiresOptIn"
        )
        apiVersion = "1.8"  // Doesn't match language version
        languageVersion = "1.9"
    }
}

tasks.test {
    useJUnitPlatform()
    jvmArgs = listOf("-XX:+EnableDynamicAgentLoading")  // Java 21 requirement
}

tasks.jar {
    archiveBaseName.set("complex-kotlin-app")
    archiveVersion.set("")
    enabled = false
}

tasks.bootJar {
    archiveBaseName.set("complex-kotlin-app")
    archiveVersion.set("")
}

application {
    mainClass.set("com.example.complex.ApplicationKt")
}

// Gradle wrapper version mismatch will be in gradle-wrapper.properties
// This build.gradle.kts expects Gradle 8.5+ but wrapper might be older

// Common issues this file demonstrates:
// 1. Kotlin plugin version vs stdlib version mismatch
// 2. Java sourceCompatibility vs targetCompatibility mismatch
// 3. Kotlin toolchain vs Java versions mismatch
// 4. jvmTarget vs toolchain mismatch
// 5. Kotlin API vs language version mismatch
// 6. Conflicting dependency versions (Jackson, Kotlinx coroutines)
// 7. Both kapt and ksp processors
// 8. Forced versions conflicting with BOM
// 9. Exclusions that might cause classpath issues
// 10. SNAPSHOT dependencies in production build
