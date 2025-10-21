---
layout: default
title: Home
---

# 🧰 Stupid Dependencies

## A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense

Ever had your Kotlin build break because of version conflicts? Gradle refusing to play nice with your Android project? Dependencies so tangled you need a PhD in Maven to understand them?

**We've all been there.** 😤

Stupid Dependencies fixes your dependency hell with personality, live API queries, and actual solutions that work.

---

## ⚡ Quick Start

```bash
# Install
pip install stupid-dependencies

# Fix your broken project
stupid check
stupid fix --apply

# See the magic in action
stupid demo --live
```

---

## 🎬 Live Demo

Watch Stupid Dependencies analyze a real Kotlin/Android project with **live data** from Maven Central and GitHub APIs:

```bash
stupid demo --live
```

```
🎬 Welcome to the 'Stupid Dependencies' Reddit Demo!
🌐 LIVE VERSION DEMO - Querying real Maven Central & GitHub APIs!

🎯 LIVE DATA: Found 4 real version issues from Maven Central:
📦 com.google.dagger:hilt-android
   Current: 2.48
   Latest from Maven Central: 2.56.2

❌ LIVE COMPATIBILITY ISSUE:
   • Kotlin 1.8.20 requires Gradle 6.8.3 - 8.1, but found 8.3
   💡 Either downgrade Gradle to 8.1 or upgrade Kotlin
```

---

## 🚀 Key Features

<div class="features-grid">
  <div class="feature">
    <h3>🌐 Live API Queries</h3>
    <p>Real-time version checking from Maven Central, GitHub, and other package repositories. No more outdated data.</p>
  </div>
  
  <div class="feature">
    <h3>🧠 Smart Compatibility</h3>
    <p>Built-in compatibility matrices for Kotlin-Gradle-Android. Knows which versions actually work together.</p>
  </div>
  
  <div class="feature">
    <h3>😎 Personality Plus</h3>
    <p>Sarcastic comments and helpful explanations. Makes debugging dependency hell almost... fun?</p>
  </div>
  
  <div class="feature">
    <h3>🎯 Actionable Fixes</h3>
    <p>Doesn't just tell you what's wrong - shows you exactly how to fix it with copy-paste commands.</p>
  </div>
</div>

---

## 🔥 What Makes This Different?

**Other tools:** *"You have a version conflict."*  
**Stupid Dependencies:** *"Your Kotlin 1.8.20 is having an existential crisis with Gradle 8.3. Here's exactly how to fix it."*

- **Actually works with real projects** - tested on messy, real-world codebases
- **Understands the ecosystem** - knows Kotlin, Gradle, Android, and their weird relationships
- **Saves you hours** - no more Stack Overflow archaeology to fix version conflicts
- **Multi-language ready** - Kotlin today, Zig and Gleam coming soon

---

## 🎯 Perfect For

- **Android developers** drowning in Gradle/Kotlin version hell
- **Teams** tired of "it works on my machine" dependency issues  
- **CI/CD pipelines** that break when dependencies update
- **Anyone** who's ever seen `FAILURE: Build failed with an exception` and wanted to throw their laptop

---

## 📖 Quick Commands

```bash
# Scan your project for issues
stupid check

# Get sarcastic but helpful explanations
stupid explain kotlin

# See what fixes are available
stupid fix

# Actually apply the fixes
stupid fix --apply

# Save your working state before you break it
stupid snapshot

# Multi-language support
stupid check --lang kotlin
stupid check --lang zig
```

---

## 🏆 Battle-Tested

This tool was born from **real pain** - 2023-2024 Kotlin ecosystem chaos, Android Gradle Plugin nightmares, and countless hours lost to version conflicts.

**It solves problems that actually exist.**

---

<div class="cta-section">
  <h2>Ready to fix your dependency hell?</h2>
  <div class="cta-buttons">
    <a href="getting-started.html" class="btn btn-primary">Get Started</a>
    <a href="demo.html" class="btn btn-secondary">See Demo</a>
    <a href="{{ site.project.repo_url }}" class="btn btn-outline">View on GitHub</a>
  </div>
</div>

---

<div class="testimonial">
  <blockquote>
    "Finally, a tool that understands my pain and actually fixes it instead of just complaining about it."
  </blockquote>
  <cite>— Every developer who's fought with Kotlin versions</cite>
</div>

<style>
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.feature {
  padding: 1.5rem;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  background: #f8f9fa;
}

.feature h3 {
  margin-top: 0;
  color: #0366d6;
}

.cta-section {
  text-align: center;
  margin: 3rem 0;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  display: inline-block;
  transition: all 0.2s;
}

.btn-primary {
  background: #0366d6;
  color: white;
}

.btn-primary:hover {
  background: #0256cc;
}

.btn-secondary {
  background: #28a745;
  color: white;
}

.btn-secondary:hover {
  background: #218838;
}

.btn-outline {
  background: transparent;
  color: #0366d6;
  border: 2px solid #0366d6;
}

.btn-outline:hover {
  background: #0366d6;
  color: white;
}

.testimonial {
  text-align: center;
  margin: 3rem 0;
  padding: 2rem;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
}

.testimonial blockquote {
  font-style: italic;
  font-size: 1.2em;
  margin: 0;
}

.testimonial cite {
  display: block;
  margin-top: 1rem;
  color: #666;
  font-weight: 600;
}

@media (max-width: 768px) {
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
}
</style>