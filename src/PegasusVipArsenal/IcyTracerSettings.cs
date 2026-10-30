using System.Text.Json;

namespace PegasusVipArsenal;

public sealed class IcyTracerSettings
{
    public bool Enabled { get; set; } = true;
    public float LifetimeSeconds { get; set; } = .12f;
    public float CoreWidth { get; set; } = .2f;
    public float GlowWidth { get; set; } = .8f;
    public int[] CoreRgb { get; set; } = [190, 250, 255];
    public int[] GlowRgb { get; set; } = [35, 205, 255];
    public int MaxBeamEntities { get; set; } = 192;

    public static IcyTracerSettings Load(string path)
    {
        var value = JsonSerializer.Deserialize<IcyTracerSettings>(File.ReadAllText(path),
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
            ?? throw new InvalidDataException("Empty tracer settings");
        value.Validate(); return value;
    }
    public void Validate()
    {
        if (!float.IsFinite(LifetimeSeconds) || LifetimeSeconds is < .03f or > .3f ||
            !float.IsFinite(CoreWidth) || CoreWidth is <= 0 or > 2 ||
            !float.IsFinite(GlowWidth) || GlowWidth < CoreWidth || GlowWidth > 5 ||
            MaxBeamEntities is < 2 or > 512 || !ValidColor(CoreRgb) || !ValidColor(GlowRgb))
            throw new InvalidDataException("Invalid icy tracer settings");
    }
    private static bool ValidColor(int[]? rgb) => rgb is { Length: 3 } && rgb.All(x => x is >= 0 and <= 255);
}
