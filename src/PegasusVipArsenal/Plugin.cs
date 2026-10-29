using System.Reflection;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API.Modules.Commands;

namespace PegasusVipArsenal;

/// <summary>
/// Read-only UI prototype for Codex. Real buy / take / abilities are not implemented here.
/// </summary>
public sealed class PegasusVipArsenalPlugin : BasePlugin
{
    public override string ModuleName => "PEGASUS VIP Frost Arsenal";
    public override string ModuleAuthor => "PEGASUS";
    public override string ModuleVersion => "0.2.0-dev";
    public override string ModuleDescription => "12-weapon catalog with map-purchase policy (integration pending)";
    private WeaponCatalog? _catalog;
    private VipAccess? _vip;
    private readonly MapWeaponStore _store = new();

    public override void Load(bool hotReload)
    {
        var dir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location)
            ?? throw new InvalidOperationException("Plugin directory unavailable");
        _catalog = WeaponCatalog.Load(Path.Combine(dir, "config", "vip_weapons.concept.json"));
        _vip = VipAccess.Load(Path.Combine(dir, "config", "roles"));
        Console.WriteLine($"[PEGASUS] {_catalog.Weapons.Count} winter weapons loaded (read-only catalog; no grants yet)");
    }

    [ConsoleCommand("css_wintershop", "Preview ordinary winter weapon shop")]
    public void ShowWinterShop(CCSPlayerController? player, CommandInfo command)
    {
        if (player is null || !player.IsValid || _catalog is null || _vip is null) return;
        int tier = _vip.GetTier(player.SteamID);
        player.PrintToChat("[PEGASUS] Зимнее оружие — цены за текущую карту (предпросмотр)");
        foreach (var weapon in _catalog.Weapons)
        {
            var quote = _store.Quote(player.SteamID, tier, weapon);
            var label = quote.Kind == AccessKind.FreeVip ? "Бесплатно по VIP"
                      : quote.Kind == AccessKind.PurchasedForMap ? "Куплено на эту карту"
                      : $"Купить за {quote.Price} снежинок";
            player.PrintToChat($"[PEGASUS] {weapon.Name} — {label}");
        }
    }

    [ConsoleCommand("css_vipguns", "Preview VIP weapons available without payment")]
    public void ShowVipWeapons(CCSPlayerController? player, CommandInfo command)
    {
        if (player is null || !player.IsValid || _catalog is null || _vip is null) return;
        int tier = _vip.GetTier(player.SteamID);
        player.PrintToChat($"[PEGASUS] VIP {tier} — бесплатный каталог (предпросмотр)");
        foreach (var weapon in _catalog.Weapons.Where(w => tier >= w.RequiredVip))
            player.PrintToChat($"[PEGASUS] {weapon.Name} — {weapon.Ability}");
    }
}
