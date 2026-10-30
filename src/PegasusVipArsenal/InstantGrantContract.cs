namespace PegasusVipArsenal;

/// <summary>
/// Non-executable business contract for Codex's WeaponGrantService implementation.
/// Do NOT turn into an automatic on-spawn queue.
/// </summary>
public enum GrantSource { ShopWithSnowflakes, VipMenu }
public enum GrantFailure { None, InvalidPlayer, DeadPlayer, NoAccess, NotEnoughSnowflakes, InvalidWeapon, EngineRejected, PaymentFailed }
public sealed record GrantRequest(ulong SteamId, string WeaponId, GrantSource Source, string RequestId);
public sealed record GrantResult(bool Success, GrantFailure Failure, string? WeaponName = null)
{
    public string? SuccessChat => Success && WeaponName is not null
        ? $"❄ PEGASUS | Вы взяли {WeaponName}" : null;
}

/// <remarks>
/// Concrete service is NOT yet implemented. It must:
/// 1. Check live player/pawn, access, team, slot, funds and deduplicate request.
/// 2. Atomically grant and equip immediately in current life, replacing same slot only.
/// 3. Charge once for shop (or roll back on any failure), never for VIP take.
/// 4. Report success in chat ONLY after verified grant/equip; no respawn dependency.
/// 5. After applying the arsenal skin, register the exact entity and its real muzzle resolver
///    with IArsenalEffectsApi; revoke that binding on rollback or skin removal.
/// See docs/INSTANT_GRANT_RU.md and docs/TEST_PLAN.md.
/// </remarks>
public interface IImmediateWeaponGrantService
{
    GrantResult TryGrantNow(GrantRequest request);
}
