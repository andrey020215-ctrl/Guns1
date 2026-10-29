using System.Reflection;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Commands;

namespace PegasusVipArsenal;

/// <summary>Read-only development skeleton. Granting/equipping is NOT implemented.</summary>
public sealed class PegasusVipArsenalPlugin : BasePlugin
{
    public override string ModuleName => "PEGASUS VIP Frost Arsenal";
    public override string ModuleAuthor => "PEGASUS";
    public override string ModuleVersion => "0.1.1-dev";
    public override string ModuleDescription => "Read-only 12-weapon VIP catalog; instant grant is specified but not implemented";

    private WeaponCatalog? _catalog;
    private VipAccess? _vip;
    private readonly MapWeaponStore _store = new();

    public override void Load(bool hotReload)
    {
        var baseDirectory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)
            ?? throw new InvalidOperationException("Module directory unavailable");
        _catalog = WeaponCatalog.Load(Path.Combine(baseDirectory, "config", "vip_weapons.concept.json"));
        _vip = VipAccess.Load(Path.Combine(baseDirectory, "config", "roles"));
        Console.WriteLine($"[PEGASUS] Loaded {_catalog.Weapons.Count} concepts; grant service disabled");
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
