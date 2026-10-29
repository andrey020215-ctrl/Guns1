using System.Text.Json;
using System.Text.Json.Serialization;

namespace PegasusVipArsenal;

public sealed class WeaponCatalog
{
    [JsonPropertyName("weapons")]
    public List<WeaponDefinition> Weapons { get; set; } = new();

    public static WeaponCatalog Load(string path)
    {
        var catalog = JsonSerializer.Deserialize<WeaponCatalog>(File.ReadAllText(path))
            ?? throw new InvalidDataException("Catalog is empty");
        if (catalog.Weapons.Count != 12 || catalog.Weapons.Select(x => x.Id).Distinct().Count() != 12)
            throw new InvalidDataException("Expected 12 distinct weapons");
        if (catalog.Weapons.Count(x => x.RequiredVip == 1) != 4 ||
            catalog.Weapons.Count(x => x.RequiredVip == 2) != 4 ||
            catalog.Weapons.Count(x => x.RequiredVip == 3) != 4)
            throw new InvalidDataException("Expected 4 weapons per VIP level");
        if (catalog.Weapons.Any(x => x.PriceSnowflakes <= 0 || x.CooldownSeconds <= 0))
            throw new InvalidDataException("Invalid price or cooldown");
        return catalog;
    }
}

public sealed class WeaponDefinition
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("tier")] public string Tier { get; set; } = "";
    [JsonPropertyName("base_weapon")] public string BaseWeapon { get; set; } = "";
    [JsonPropertyName("slot")] public string Slot { get; set; } = "";
    [JsonPropertyName("ability")] public string Ability { get; set; } = "";
    [JsonPropertyName("required_vip")] public int RequiredVip { get; set; }
    [JsonPropertyName("price_snowflakes")] public int PriceSnowflakes { get; set; }
}
