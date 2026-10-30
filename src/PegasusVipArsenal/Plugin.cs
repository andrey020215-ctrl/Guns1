using System.Reflection;
using CounterStrikeSharp.API.Core.Capabilities;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Commands;
using PegasusVipArsenal.Contracts;

namespace PegasusVipArsenal;

/// <summary>Read-only shop with instance-scoped tracer integration. Granting/equipping is NOT implemented.</summary>
[MinimumApiVersion(378)]
public sealed class PegasusVipArsenalPlugin : BasePlugin
{
    public override string ModuleName => "PEGASUS VIP Frost Arsenal";
    public override string ModuleAuthor => "PEGASUS";
    public override string ModuleVersion => "0.2.0-dev";
    public override string ModuleDescription => "12-weapon catalog and instance-bound icy tracers; grant integration required";

    private WeaponCatalog? _catalog;
    private VipAccess? _vip;
    private readonly MapWeaponStore _store = new();
    private IcyTracerController? _tracers;

    public override void Load(bool hotReload)
    {
        var baseDirectory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)
            ?? throw new InvalidOperationException("Module directory unavailable");
        _catalog = WeaponCatalog.Load(Path.Combine(baseDirectory, "config", "vip_weapons.concept.json"));
        _vip = VipAccess.Load(Path.Combine(baseDirectory, "config", "roles"));
        _tracers = new(_catalog, IcyTracerSettings.Load(Path.Combine(baseDirectory, "config", "icy_tracers.json")), Logger);
        ArsenalEffectsProvider.Current = _tracers;
        if (!ArsenalEffectsProvider.CapabilityRegistered)
        {
            Capabilities.RegisterPluginCapability(new PluginCapability<IArsenalEffectsApi>(IArsenalEffectsApi.CapabilityName), ArsenalEffectsProvider.Resolve);
            ArsenalEffectsProvider.CapabilityRegistered = true;
        }
        RegisterEventHandler<EventWeaponFire>((ev, _) => { _tracers.Fire(ev); return HookResult.Continue; }, HookMode.Pre);
        RegisterEventHandler<EventBulletImpact>((ev, _) => { _tracers.Impact(ev); return HookResult.Continue; }, HookMode.Pre);
        RegisterEventHandler<EventPlayerDeath>((ev, _) => { ForgetPlayer(ev.Userid); return HookResult.Continue; });
        RegisterEventHandler<EventPlayerDisconnect>((ev, _) => { ForgetPlayer(ev.Userid); return HookResult.Continue; });
        RegisterEventHandler<EventRoundStart>((_, _) => { _tracers.ClearShots(); return HookResult.Continue; });
        RegisterListener<Listeners.OnEntityDeleted>(entity => _tracers.RemoveEntity(entity.EntityHandle.Raw));
        RegisterListener<Listeners.OnMapEnd>(() => _tracers.MapEnd());
        RegisterListener<Listeners.OnMapStart>(_ => _tracers.MapStart());
        RegisterListener<Listeners.OnTick>(() => _tracers.Tick());
        Console.WriteLine($"[PEGASUS] Loaded {_catalog.Weapons.Count} concepts; grant service disabled");
    }

    private void ForgetPlayer(CCSPlayerController? player)
    {
        if (player is { IsValid: true }) _tracers?.RemoveEntity(player.EntityHandle.Raw);
    }

    public override void Unload(bool hotReload)
    {
        _tracers?.Unload();
        if (ReferenceEquals(ArsenalEffectsProvider.Current, _tracers)) ArsenalEffectsProvider.Current = null;
    }

    [ConsoleCommand("css_vipguns", "List available PEGASUS VIP Arsenal weapons (read-only)")]
    public void ShowCatalog(CCSPlayerController? player, CommandInfo command)
    {
        if (player is null || !player.IsValid || _vip is null || _catalog is null) return;
        var tier = _vip.GetTier(player.SteamID);
        player.PrintToChat($"❄ PEGASUS | VIP {tier} · каталог: {_catalog.Weapons.Count} · DEV");
        foreach (var item in _catalog.Weapons.Where(w => tier >= w.RequiredVip))
            player.PrintToChat($"❄ PEGASUS | {item.Name} — {item.Ability}");
    }
    [ConsoleCommand("css_wintershop", "Preview 12 PEGASUS winter weapons in paid snowflake store (read-only)")]
    public void ShowWinterShop(CCSPlayerController? player, CommandInfo command)
    {
        if (player is null || !player.IsValid || _vip is null || _catalog is null) return;
        var tier = _vip.GetTier(player.SteamID);
        player.PrintToChat("❄ PEGASUS | Зимний магазин — предпросмотр; покупка пока недоступна");
        foreach (var weapon in _catalog.Weapons)
        {
            var quote = _store.Quote(player.SteamID, tier, weapon);
            var label = quote.Kind == AccessKind.FreeVip ? "Бесплатно VIP" :
                        quote.Kind == AccessKind.PurchasedForMap ? "Куплено на эту карту" :
                        $"Купить за {quote.Price} снежинок";
            player.PrintToChat($"❄ PEGASUS | {weapon.Name} — {label}");
        }
    }
}
