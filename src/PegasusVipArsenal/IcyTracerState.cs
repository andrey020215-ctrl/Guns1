using System.Numerics;
using PegasusVipArsenal.Contracts;

namespace PegasusVipArsenal;

public sealed record TracerFire(uint Controller, uint Pawn, uint Weapon, string BaseWeapon,
    string EventWeapon, int Tick, Vector3 Eye, Vector3 Muzzle, int Bullets = 1, bool Burst = false);
public sealed record IcyTracerSegment(uint Weapon, string WeaponId, Vector3 Eye, Vector3 Start, Vector3 End);

/// <summary>Pure shot attribution. A weapon type or VIP status alone never enables a tracer.</summary>
public sealed class IcyTracerState
{
    private sealed record Binding(ArsenalWeaponReceipt Receipt, string BaseWeapon);
    private sealed class Shot(TracerFire fire, Binding binding, int limit)
    {
        public TracerFire Fire { get; } = fire;
        public Binding Binding { get; } = binding;
        public int Limit { get; } = limit;
        public HashSet<Vector3> Impacts { get; } = new();
    }
    private readonly Dictionary<string, string> _weapons;
    private readonly Dictionary<uint, Binding> _bindings = new();
    private readonly Dictionary<uint, Shot> _shots = new();
    public Guid MapEpoch { get; private set; } = Guid.NewGuid();
    public const int ImpactWindowTicks = 2;

    public IcyTracerState(IEnumerable<WeaponDefinition> weapons) =>
        _weapons = weapons.ToDictionary(x => x.Id, x => x.BaseWeapon, StringComparer.Ordinal);

    public bool Register(ArsenalWeaponReceipt receipt, string actualBaseWeapon)
    {
        if (receipt.GrantId == Guid.Empty || receipt.MapEpoch != MapEpoch ||
            receipt.ControllerHandle is 0 or uint.MaxValue || receipt.PawnHandle is 0 or uint.MaxValue ||
            receipt.WeaponHandle is 0 or uint.MaxValue ||
            !_weapons.TryGetValue(receipt.WeaponId, out var expected) || expected != actualBaseWeapon) return false;
        if (_bindings.TryGetValue(receipt.WeaponHandle, out var existing)) return existing.Receipt == receipt;
        if (_bindings.Values.Any(x => x.Receipt.GrantId == receipt.GrantId)) return false;
        _bindings.Add(receipt.WeaponHandle, new(receipt, expected));
        return true;
    }

    public bool OwnsTracer(uint handle) => _bindings.ContainsKey(handle);
    public void CancelShot(uint controller) => _shots.Remove(controller);
    public void ClearShots() => _shots.Clear();

    public void RemoveEntity(uint rawHandle)
    {
        foreach (var handle in _bindings.Where(x => x.Key == rawHandle ||
                     x.Value.Receipt.ControllerHandle == rawHandle || x.Value.Receipt.PawnHandle == rawHandle)
                     .Select(x => x.Key).ToArray()) _bindings.Remove(handle);
        foreach (var controller in _shots.Where(x => x.Key == rawHandle ||
                     x.Value.Fire.Pawn == rawHandle || x.Value.Fire.Weapon == rawHandle)
                     .Select(x => x.Key).ToArray()) _shots.Remove(controller);
    }

    public void NewMap()
    {
        _bindings.Clear(); _shots.Clear(); MapEpoch = Guid.NewGuid();
    }

    public bool Fire(TracerFire fire)
    {
        // Every fire event, including an ordinary gun, invalidates the preceding shot first.
        _shots.Remove(fire.Controller);
        if (!_bindings.TryGetValue(fire.Weapon, out var binding) ||
            binding.Receipt.ControllerHandle != fire.Controller || binding.Receipt.PawnHandle != fire.Pawn ||
            binding.BaseWeapon != fire.BaseWeapon || Normalize(fire.EventWeapon) != binding.BaseWeapon ||
            !Finite(fire.Eye) || !Finite(fire.Muzzle) ||
            Vector3.DistanceSquared(fire.Eye, fire.Muzzle) > 128 * 128) return false;
        var pellets = binding.BaseWeapon is "weapon_nova" or "weapon_xm1014"
            ? Math.Clamp(fire.Bullets, 1, 16)
            : fire.Burst && binding.BaseWeapon is "weapon_famas" or "weapon_glock"
                ? Math.Clamp(fire.Bullets, 1, 3) : 1;
        _shots[fire.Controller] = new(fire, binding, pellets);
        return true;
    }

    public IcyTracerSegment? Impact(uint controller, uint pawn, int tick, Vector3 end)
    {
        if (!_shots.TryGetValue(controller, out var shot)) return null;
        var elapsed = (long)tick - shot.Fire.Tick;
        var window = shot.Fire.Burst && shot.Binding.BaseWeapon is "weapon_famas" or "weapon_glock"
            ? 16 : ImpactWindowTicks;
        if (pawn != shot.Fire.Pawn || elapsed < 0 || elapsed > window)
        { _shots.Remove(controller); return null; }
        if (!Finite(end) || Vector3.DistanceSquared(end, shot.Fire.Eye) < 1 ||
            Vector3.DistanceSquared(end, shot.Fire.Eye) > 32768f * 32768f || shot.Impacts.Count >= shot.Limit)
            return null;
        // Quantize sub-unit duplicates; keep native shotgun spread endpoints distinct.
        var key = new Vector3(MathF.Round(end.X * 2), MathF.Round(end.Y * 2), MathF.Round(end.Z * 2));
        if (!shot.Impacts.Add(key)) return null;
        return new(shot.Fire.Weapon, shot.Binding.Receipt.WeaponId, shot.Fire.Eye, shot.Fire.Muzzle, end);
    }

    private static string Normalize(string value) => value.StartsWith("weapon_", StringComparison.Ordinal)
        ? value : "weapon_" + value;
    public static bool Finite(Vector3 p) => float.IsFinite(p.X) && float.IsFinite(p.Y) && float.IsFinite(p.Z);
}
