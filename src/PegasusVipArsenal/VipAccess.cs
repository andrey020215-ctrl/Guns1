namespace PegasusVipArsenal;

// Local SteamID64 lists, one per line. Never commit real accounts.
public sealed class VipAccess
{
    private readonly Dictionary<ulong, int> _levels = new();

    public static VipAccess Load(string directory)
    {
        var result = new VipAccess();
        for (var level = 1; level <= 3; level++)
        {
            var file = Path.Combine(directory, $"vip{level}.txt");
            if (!File.Exists(file)) continue;
            foreach (var raw in File.ReadAllLines(file))
            {
                var value = raw.Split('#')[0].Trim();
                if (ulong.TryParse(value, out var steamId) && steamId > 0)
                    result._levels[steamId] = Math.Max(level, result.GetTier(steamId));
            }
        }
        return result;
    }

    public int GetTier(ulong steamId) => _levels.GetValueOrDefault(steamId, 0);
    public bool CanUse(ulong steamId, WeaponDefinition weapon) => GetTier(steamId) >= weapon.RequiredVip;
}
