using System.Text.Json;
using System.Text.Json.Serialization;

namespace PegasusVipArsenal;

/// <summary>Settings and data only. 12 weapons; game integration is a separate stage.</summary>
public sealed class WeaponCatalog
{
    [JsonPropertyName("weapons")] public List<WeaponDefinition> Weapons { get; set; } = new();
    public static WeaponCatalog Load(string path)
    {
        var data = JsonSerializer.Deserialize<WeaponCatalog>(File.ReadAllText(path))
                   ?? throw new InvalidDataException("Weapon catalog is empty");
        if (data.Weapons.Count != 12 || data.Weapons.Select(x => x.Id).Distinct().Count() != 12)
            throw new InvalidDataException("Expected exactly 12 unique winter weapons");
        if (data.Weapons.Any(x => x.RequiredVip is < 1 or > 3 || x.PriceSnowflakes < 0
             || string.IsNullOrWhiteSpace(x.BaseWeapon)))
            throw new InvalidDataException("Invalid winter weapon definition");
        return data;
    }
}
public sealed class WeaponDefinition
{
    [JsonPropertyName("id")] public string Id { get; set; } = "";
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("base_weapon")] public string BaseWeapon { get; set; } = "";
    [JsonPropertyName("slot")] public string Slot { get; set; } = "";
    [JsonPropertyName("required_vip")] public int RequiredVip { get; set; }
    [JsonPropertyName("price_snowflakes")] public int PriceSnowflakes { get; set; }
    [JsonPropertyName("ability")] public string Ability { get; set; } = "";
    [JsonPropertyName("cooldown_seconds")] public double CooldownSeconds { get; set; }
}
