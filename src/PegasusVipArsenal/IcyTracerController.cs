using System.Numerics;
using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Modules.Utils;
using Microsoft.Extensions.Logging;
using PegasusVipArsenal.Contracts;
using GameTrace = CounterStrikeSharp.API.Modules.Utils.Trace;

namespace PegasusVipArsenal;

internal sealed class IcyTracerController : IArsenalEffectsApi
{
    private readonly IcyTracerState _state;
    private readonly IcyTracerSettings _settings;
    private readonly IcyBeamRenderer _renderer;
    private readonly ILogger _log;
    private readonly Dictionary<uint, Func<MuzzleQuery, Vector3?>> _muzzles = new();
    private bool _active = true;
    private bool _renderFailureLogged;
    public Guid MapEpoch => _state.MapEpoch;

    public IcyTracerController(WeaponCatalog catalog, IcyTracerSettings settings, ILogger log)
    { _state = new(catalog.Weapons); _settings = settings; _renderer = new(settings); _log = log; }

    public bool RegisterGranted(ArsenalWeaponReceipt receipt, Func<MuzzleQuery, Vector3?> resolveMuzzle)
    {
        if (!_active || !_settings.Enabled || resolveMuzzle is null) return false;
        var player = new CHandle<CCSPlayerController>(receipt.ControllerHandle).Value;
        var pawn = player?.PlayerPawn.Value;
        var weapon = new CHandle<CBasePlayerWeapon>(receipt.WeaponHandle).Value;
        if (player is not { IsValid: true, PawnIsAlive: true } || pawn is not { IsValid: true } ||
            weapon is not { IsValid: true } || pawn.EntityHandle.Raw != receipt.PawnHandle ||
            weapon.OwnerEntity.Raw != receipt.PawnHandle ||
            pawn.WeaponServices?.MyWeapons.Any(x => x.Raw == receipt.WeaponHandle) != true ||
            !_state.Register(receipt, weapon.DesignerName)) return false;
        _muzzles.TryAdd(receipt.WeaponHandle, resolveMuzzle);
        return true;
    }

    public bool OwnsTracer(uint weaponHandle) => _active && _settings.Enabled && _state.OwnsTracer(weaponHandle);
    public void Revoke(uint weaponHandle) => RemoveEntity(weaponHandle);

    public void RemoveEntity(uint raw)
    {
        _state.RemoveEntity(raw);
        foreach (var weapon in _muzzles.Keys.Where(x => !_state.OwnsTracer(x)).ToArray()) _muzzles.Remove(weapon);
    }

    public void Fire(EventWeaponFire ev)
    {
        var player = ev.Userid;
        if (player is not { IsValid: true }) return;
        var controller = player.EntityHandle.Raw;
        _state.CancelShot(controller);
        if (!_active || !_settings.Enabled || !player.PawnIsAlive) return;
        var pawn = player.PlayerPawn.Value;
        var weapon = pawn?.WeaponServices?.ActiveWeapon.Value;
        if (pawn is not { IsValid: true } || weapon is not { IsValid: true } ||
            weapon.OwnerEntity.Raw != pawn.EntityHandle.Raw ||
            !_state.OwnsTracer(weapon.EntityHandle.Raw) ||
            !_muzzles.TryGetValue(weapon.EntityHandle.Raw, out var resolver) || pawn.AbsOrigin is not { } origin) return;
        var query = new MuzzleQuery(controller, pawn.EntityHandle.Raw, weapon.EntityHandle.Raw, Server.TickCount);
        Vector3? muzzle;
        try { muzzle = resolver(query); }
        catch (Exception error)
        {
            Revoke(query.WeaponHandle);
            _log.LogWarning(error, "Arsenal muzzle resolver failed; binding revoked"); return;
        }
        if (muzzle is null) return;
        var eye = new Vector3(origin.X + pawn.ViewOffset.X, origin.Y + pawn.ViewOffset.Y, origin.Z + pawn.ViewOffset.Z);
        var csWeapon = new CCSWeaponBase(weapon.Handle);
        var data = csWeapon.VData;
        if (data is null) return;
        var burst = csWeapon.BurstMode && weapon.DesignerName is "weapon_glock" or "weapon_famas";
        var bullets = burst ? data.BurstShotCount : data.NumBullets;
        _state.Fire(new(controller, query.PawnHandle, query.WeaponHandle, weapon.DesignerName,
            ev.Weapon, query.Tick, eye, muzzle.Value, bullets, burst));
    }

    public void Impact(EventBulletImpact ev)
    {
        var player = ev.Userid;
        var pawn = player?.PlayerPawn.Value;
        if (!_active || !_settings.Enabled || player is not { IsValid: true, PawnIsAlive: true } ||
            pawn is not { IsValid: true }) return;
        var segment = _state.Impact(player.EntityHandle.Raw, pawn.EntityHandle.Raw,
            Server.TickCount, new(ev.X, ev.Y, ev.Z));
        if (segment is null) return;
        try
        {
            var options = new TraceOptions { InteractsWith = Masks.Shot };
            // Clip the muzzle against nearby cover, then clip at the first physical obstruction.
            // A penetrating impact must not draw a line through a wall to a hidden target.
            var near = GameTrace.TraceEndShape(IcyBeamRenderer.ToGame(segment.Eye),
                IcyBeamRenderer.ToGame(segment.Start), pawn, options);
            if (near.IsAllSolid) return;
            var start = near.DidHit() ? ToNumerics(near.HitPoint) : segment.Start;
            var hit = GameTrace.TraceEndShape(IcyBeamRenderer.ToGame(start),
                IcyBeamRenderer.ToGame(segment.End), pawn, options);
            if (hit.IsAllSolid) return;
            var end = hit.DidHit() ? ToNumerics(hit.HitPoint) : segment.End;
            if (!IcyTracerState.Finite(start) || !IcyTracerState.Finite(end)) return;
            _renderer.Draw(start, end, Server.CurrentTime);
        }
        catch (Exception error)
        {
            // Never fall back to an unclipped beam or abort the native weapon event.
            if (!_renderFailureLogged)
            { _log.LogWarning(error, "Icy tracer rendering failed; check server API and beam support"); _renderFailureLogged = true; }
        }
    }

    public void Tick() { if (_active) _renderer.Tick(Server.CurrentTime); }
    public void ClearShots() => _state.ClearShots();
    public void MapEnd() { _renderer.Clear(true); _state.NewMap(); _muzzles.Clear(); }
    public void MapStart() { _renderer.Clear(false); _state.NewMap(); _muzzles.Clear(); _renderFailureLogged = false; }
    public void Unload() { _active = false; MapEnd(); }
    private static Vector3 ToNumerics(CounterStrikeSharp.API.Modules.Utils.Vector v) => new(v.X, v.Y, v.Z);
}
