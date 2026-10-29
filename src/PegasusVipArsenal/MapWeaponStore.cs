namespace PegasusVipArsenal;

/// <summary>
/// Economy contract. This plugin must NOT maintain a second currency balance.
/// Implement this on top of the existing PEGASUS snowflake economy.
/// TryDebit must be atomic and return false on insufficient funds.
/// </summary>
public interface ISnowflakeWallet
{
    int GetBalance(ulong steamId);
    bool TryDebit(ulong steamId, int amount);
}
public enum AccessKind { FreeVip, PurchasedForMap, NeedsPurchase }
public enum PurchaseStatus { AlreadyFree, AlreadyPurchased, Purchased, InsufficientFunds }
public readonly record struct ShopQuote(AccessKind Kind, int Price, int FinishTier);
public readonly record struct PurchaseReceipt(PurchaseStatus Status, int Spent);
/// <summary>
/// A deterministic, thread-safe map-scoped purchase policy.
/// NOT yet wired to CounterStrikeSharp menu, map event or weapon grant.
/// The map event is responsible for invoking StartNewMap ONCE per map load.
/// </summary>
public sealed class MapWeaponStore
{
    private readonly object _mutex = new();
    private readonly Dictionary<ulong, HashSet<string>> _unlocked = new();
    private long _epoch;

    public long MapEpoch { get { lock (_mutex) return _epoch; } }

    public void StartNewMap(string mapName)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(mapName);
        lock (_mutex)
        {
            _epoch++;
            _unlocked.Clear(); // Only unlocks; NEVER currency
        }
    }

    public ShopQuote Quote(ulong steamId, int vipTier, WeaponDefinition weapon)
    {
        ArgumentNullException.ThrowIfNull(weapon);
        lock (_mutex) return QuoteLocked(steamId, vipTier, weapon);
    }

    private ShopQuote QuoteLocked(ulong steamId, int vipTier, WeaponDefinition weapon)
    {
        if (vipTier >= weapon.RequiredVip)
            return new ShopQuote(AccessKind.FreeVip, 0, Math.Clamp(vipTier, 1, 3));
        if (_unlocked.TryGetValue(steamId, out var owned) && owned.Contains(weapon.Id))
            return new ShopQuote(AccessKind.PurchasedForMap, 0,
                vipTier > 0 ? Math.Clamp(vipTier, 1, 3) : weapon.RequiredVip);
        return new ShopQuote(AccessKind.NeedsPurchase, weapon.PriceSnowflakes,
            vipTier > 0 ? Math.Clamp(vipTier, 1, 3) : weapon.RequiredVip);
    }

    public bool CanTake(ulong steamId, int vipTier, WeaponDefinition weapon)
        => Quote(steamId, vipTier, weapon).Kind is not AccessKind.NeedsPurchase;

    public PurchaseReceipt Buy(ulong steamId, int vipTier, WeaponDefinition weapon, ISnowflakeWallet wallet)
    {
        ArgumentNullException.ThrowIfNull(weapon);
        ArgumentNullException.ThrowIfNull(wallet);
        if (steamId == 0) throw new ArgumentOutOfRangeException(nameof(steamId));
        lock (_mutex)
        {
            // Double-purchase requests serialize on this lock and do not double charge.
            var quote = QuoteLocked(steamId, vipTier, weapon);
            if (quote.Kind == AccessKind.FreeVip)
                return new PurchaseReceipt(PurchaseStatus.AlreadyFree, 0);
            if (quote.Kind == AccessKind.PurchasedForMap)
                return new PurchaseReceipt(PurchaseStatus.AlreadyPurchased, 0);
            if (!wallet.TryDebit(steamId, quote.Price))
                return new PurchaseReceipt(PurchaseStatus.InsufficientFunds, 0);
            if (!_unlocked.TryGetValue(steamId, out var owned))
                _unlocked[steamId] = owned = new HashSet<string>(StringComparer.Ordinal);
            owned.Add(weapon.Id);
            return new PurchaseReceipt(PurchaseStatus.Purchased, quote.Price);
        }
    }
}
