using PegasusVipArsenal;
using System;
using System.Collections.Generic;

// Run with dotnet as a standalone harness after creating a test project.
// Tests execute pure domain logic without CS2 and without connecting to a server.
var store = new MapWeaponStore();
var a = new WeaponDefinition { Id="ak47", RequiredVip=2, PriceSnowflakes=300 };
var b = new WeaponDefinition { Id="mp9", RequiredVip=1, PriceSnowflakes=150 };
var wallet = new Wallet();
const ulong regular = 76561198000000001;
store.StartNewMap("de_dust2");
Check(!store.CanTake(regular, 0, a), "Regular cannot take before buying");
Check(store.CanTake(regular, 1, b), "VIP I has free Tier I");
Check(!store.CanTake(regular, 1, a), "VIP I not free Tier II");
Check(store.CanTake(regular, 2, a), "VIP II free Tier II");
Check(store.CanTake(regular, 3, a), "VIP III free Tier II");
Check(store.Buy(regular, 0, a, wallet).Status == PurchaseStatus.Purchased, "First purchase");
Check(wallet.Balance == 700, "Deduct once");
Check(store.Buy(regular, 0, a, wallet).Status == PurchaseStatus.AlreadyPurchased, "Repeat purchase");
Check(wallet.Balance == 700, "No double debit");
Check(store.CanTake(regular, 0, a), "Can repeatedly take bought item");
store.StartNewMap("de_dust2"); // Same map name should still reset
Check(!store.CanTake(regular, 0, a), "Change map clears purchases even if map name matches");
Check(wallet.Balance == 700, "Changing map does not reset balance");
Console.WriteLine("PASS: map-scoped purchase policy");
static void Check(bool value, string message) { if (!value) throw new Exception(message); }
class Wallet : ISnowflakeWallet
{
    public int Balance { get; private set; } = 1000;
    public int GetBalance(ulong id) => Balance;
    public bool TryDebit(ulong id,int amount)
    {
        if (amount > Balance) return false;
        Balance -= amount; return true;
    }
}
