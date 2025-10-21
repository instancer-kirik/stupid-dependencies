const std = @import("std");

// This build script requires Zig 0.12.1 but you might have 0.13.0 installed
// SDS should detect this version mismatch

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Create the main executable
    const exe = b.addExecutable(.{
        .name = "conflicted-example",
        .root_source_file = .{ .path = "src/main.zig" },
        .target = target,
        .optimize = optimize,
    });

    // Add dependencies that might cause conflicts
    const ziglibc = b.dependency("ziglibc", .{
        .target = target,
        .optimize = optimize,
    });
    exe.root_module.addImport("ziglibc", ziglibc.module("ziglibc"));

    const example_dep = b.dependency("example_dep", .{
        .target = target,
        .optimize = optimize,
    });
    exe.root_module.addImport("example", example_dep.module("example"));

    b.installArtifact(exe);

    // Create run step
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());

    if (b.args) |args| {
        run_cmd.addArgs(args);
    }

    const run_step = b.step("run", "Run the application");
    run_step.dependOn(&run_cmd.step);

    // Create test step
    const unit_tests = b.addTest(.{
        .root_source_file = .{ .path = "src/main.zig" },
        .target = target,
        .optimize = optimize,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_unit_tests.step);
}
