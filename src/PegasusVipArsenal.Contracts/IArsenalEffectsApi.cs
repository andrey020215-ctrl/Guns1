using System.Numerics;

namespace PegasusVipArsenal.Contracts;

public sealed record ArsenalWeaponReceipt(Guid GrantId, Guid MapEpoch, uint ControllerHandle,
    uint PawnHandle, uint WeaponHandle, string WeaponId);
public sealed record MuzzleQuery(uint ControllerHandle, uint PawnHandle, uint WeaponHandle, int Tick);

/// <summary>Trusted server-side grant/material integration; never expose registration to players.
/// Share this assembly via CounterStrikeSharp/shared/PegasusVipArsenal.Contracts/.
/// Call only after successful grant, equip and application of the arsenal skin.</summary>
public interface IArsenalEffectsApi
{
    public const string CapabilityName = "pegasus:arsenal-effects:v1";
    Guid MapEpoch { get; }
    // The resolver must return the actual world-space muzzle attachment at the shot tick.
    // Null or an unavailable attachment suppresses the effect; no eye-position approximation.
    bool RegisterGranted(ArsenalWeaponReceipt receipt, Func<MuzzleQuery, Vector3?> resolveMuzzle);
    void Revoke(uint weaponHandle);
    // Weapon Frost Effects must skip its own tracer for these handles to avoid double rendering.
    bool OwnsTracer(uint weaponHandle);
}

/// <summary>Stable shared provider across plugin hot reloads. Lifecycle calls use the game thread.</summary>
public static class ArsenalEffectsProvider
{
    public static IArsenalEffectsApi? Current { get; set; }
    public static bool CapabilityRegistered { get; set; }
    // Method group lives in the shared assembly and never captures an unloaded plugin instance.
    public static IArsenalEffectsApi Resolve() => Current!;
}
