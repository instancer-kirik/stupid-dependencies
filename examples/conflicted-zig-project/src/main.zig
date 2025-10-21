const std = @import("std");

// Example Zig application that demonstrates dependency conflicts
// This is part of the SDS (Stupid Dependency Solver) test suite

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();

    try stdout.print("🧰 SDS Example: Conflicted Zig Project\n");
    try stdout.print("=====================================\n\n");

    try stdout.print("This project is configured to require Zig 0.12.1\n");
    try stdout.print("but you might have a different version installed.\n\n");

    try stdout.print("Run `sds check` to see if there are any conflicts!\n");
    try stdout.print("Run `sds fix` to get suggestions on how to resolve them.\n\n");

    // Display current Zig version info
    try stdout.print("Expected Zig version: 0.12.1 (from build.zig.zon)\n");
    try stdout.print("Your Zig version: Run `zig version` to check\n\n");

    // Some example code that might behave differently across versions
    const numbers = [_]i32{ 1, 2, 3, 4, 5 };

    var sum: i32 = 0;
    for (numbers) |num| {
        sum += num;
    }

    try stdout.print("Calculated sum: {d}\n", .{sum});
    try stdout.print("If you see this message, the basic Zig features are working!\n");

    // Simulate a dependency usage
    try simulateDependencyUsage();
}

fn simulateDependencyUsage() !void {
    const stdout = std.io.getStdOut().writer();

    try stdout.print("\n🔗 Simulating dependency usage...\n");
    try stdout.print("In a real project, this would use imports like:\n");
    try stdout.print("  const ziglibc = @import(\"ziglibc\");\n");
    try stdout.print("  const example = @import(\"example\");\n");
    try stdout.print("\nThese dependencies are defined in build.zig.zon\n");
}

test "basic functionality" {
    const testing = std.testing;

    // Test basic arithmetic
    const result = 2 + 2;
    try testing.expect(result == 4);

    // Test array operations
    const numbers = [_]i32{ 1, 2, 3 };
    try testing.expect(numbers.len == 3);
    try testing.expect(numbers[0] == 1);
}

test "version compatibility" {
    // This test might behave differently across Zig versions
    // SDS should catch when your Zig version doesn't match build.zig.zon
    const testing = std.testing;

    // Test that should work on Zig 0.12.1
    const slice = [_]u8{ 'h', 'e', 'l', 'l', 'o' };
    try testing.expect(slice.len == 5);

    // Features that might not work on older/newer versions
    const optional_value: ?i32 = 42;
    try testing.expect(optional_value.? == 42);
}
