namespace PegasusVipArsenal;

// Local development adapter: file list of SteamID64, one per line.
// Must be integrated with the existing PEGASUS roles service by Codex.
public sealed class VipAccess
{
    private readonly Dictionary<ulong, int> _tiers = new();

    public static VipAccess Load(string roleDirectory)
    {
        var permissions = new VipAccess();
        for (int tier = 1; tier <= 3; tier++)
        {
            var file = Path.Combine(roleDirectory, $"vip{tier}.txt");
            if (!File.Exists(file)) continue;
            foreach (string line in File.ReadAllLines(file))
            {
                string input = line.Split('#', 2)[0].Trim();
                if (ulong.TryParse(input, out var steamId) && steamId != 0)
                    permissions._tiers[steamId] = Math.Max(tier, permissions.GetTier(steamId));
            }
        }
        return permissions;
    }
    public int GetTier(ulong steamId) => _tiers.GetValueOrDefault(steamId);
}
