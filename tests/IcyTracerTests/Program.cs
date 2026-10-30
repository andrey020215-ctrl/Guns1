using System.Numerics;
using PegasusVipArsenal;
using PegasusVipArsenal.Contracts;

var root = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../../"));
var catalog = WeaponCatalog.Load(Path.Combine(root, "config/vip_weapons.concept.json"));
var state = new IcyTracerState(catalog.Weapons);
var checks = 0;
void Check(bool condition, string name)
{ if (!condition) throw new Exception(name); checks++; }
ArsenalWeaponReceipt Receipt(WeaponDefinition w, uint weapon = 300) =>
    new(Guid.NewGuid(), state.MapEpoch, 100, 200, weapon, w.Id);
TracerFire Fire(WeaponDefinition w, uint weapon = 300, int tick = 100) =>
    new(100, 200, weapon, w.BaseWeapon, w.BaseWeapon[7..], tick, new(0, 0, 64), new(20, 4, 60), w.Id == "nova" ? 9 : w.Id == "xm1014" ? 6 : 1);
Vector3 Target(int n = 0) => new(500, n * 2, 64);
var ak = catalog.Weapons.Single(w => w.Id == "ak47");
var nova = catalog.Weapons.Single(w => w.Id == "nova");

foreach (var w in catalog.Weapons)
{
    state.NewMap();
    Check(!state.Fire(Fire(w)), w.Id + " ordinary instance excluded");
    var receipt = Receipt(w);
    Check(state.Register(receipt, w.BaseWeapon), w.Id + " genuine instance registered");
    Check(state.Register(receipt, w.BaseWeapon), w.Id + " registration idempotent");
    Check(state.Fire(Fire(w)), w.Id + " shot accepted");
    var segment = state.Impact(100, 200, 100, Target());
    Check(segment?.WeaponId == w.Id && segment.Weapon == 300, w.Id + " bound to exact instance");
}
state.NewMap();
var registered = Receipt(ak);
Check(!state.Register(registered with { WeaponId = "not_arsenal" }, ak.BaseWeapon), "unknown skin rejected");
Check(!state.Register(registered, "weapon_aug"), "wrong base rejected");
Check(!state.Register(registered with { MapEpoch = Guid.NewGuid() }, ak.BaseWeapon), "stale epoch rejected");
Check(!state.Register(registered with { GrantId = Guid.Empty }, ak.BaseWeapon), "empty receipt rejected");
Check(state.Register(registered, ak.BaseWeapon), "bind AK");
Check(!state.Register(registered with { WeaponHandle = 301 }, ak.BaseWeapon), "grant cannot bind another entity");
Check(!state.Fire(Fire(ak) with { Weapon = 300 + 32768 }), "reused entity index with new serial rejected");
Check(!state.Fire(Fire(ak) with { Pawn = 201 }), "new pawn cannot inherit old weapon");
Check(!state.Fire(Fire(ak) with { Controller = 101 }), "another owner excluded");
Check(!state.Fire(Fire(ak) with { EventWeapon = "glock" }), "mismatched weapon event excluded");
Check(!state.Fire(Fire(ak) with { Muzzle = new(float.NaN, 0, 0) }), "NaN muzzle excluded");
Check(!state.Fire(Fire(ak) with { Muzzle = new(1000, 0, 0) }), "implausible muzzle excluded");
Check(state.Fire(Fire(ak)), "genuine shot before switch");
Check(!state.Fire(Fire(ak, 301, 101)), "ordinary instance shot after switch excluded");
Check(state.Impact(100, 200, 101, Target()) is null, "ordinary shot clears preceding special shot");
Check(state.Fire(Fire(ak)), "new special shot");
Check(state.Impact(101, 200, 100, Target()) is null, "another player impact excluded");
Check(state.Impact(100, 200, 100, Target()) is not null, "correct player impact accepted");
Check(state.Impact(100, 200, 100, Target()) is null, "duplicate impact suppressed");
Check(state.Impact(100, 200, 100, Target(1)) is null, "penetration does not multiply rifle tracer");
state.Fire(Fire(ak));
Check(state.Impact(100, 200, 103, Target()) is null, "late impact excluded");
state.Fire(Fire(ak));
Check(state.Impact(100, 200, 99, Target()) is null, "out-of-order impact excluded");
state.Fire(Fire(ak));
Check(state.Impact(100, 201, 100, Target()) is null, "respawned pawn impact excluded");
state.Fire(Fire(ak));
Check(state.Impact(100, 200, 100, new(float.NaN, 0, 0)) is null, "invalid impact excluded");
Check(state.Impact(100, 200, 100, Target()) is not null, "invalid impact does not consume shot");
state.Fire(Fire(ak));
state.RemoveEntity(300);
Check(!state.OwnsTracer(300) && state.Impact(100, 200, 100, Target()) is null, "weapon deletion/revoke clears pending shot");
foreach (var deleted in new uint[] { 100, 200 })
{
    state.NewMap(); state.Register(Receipt(ak), ak.BaseWeapon); state.Fire(Fire(ak));
    state.RemoveEntity(deleted);
    Check(!state.OwnsTracer(300) && state.Impact(100, 200, 100, Target()) is null, "death/disconnect deletion clears binding");
}
state.NewMap();
registered = Receipt(ak); state.Register(registered, ak.BaseWeapon); state.Fire(Fire(ak));
state.NewMap();
Check(!state.OwnsTracer(300) && !state.Register(registered, ak.BaseWeapon), "same-name map reload invalidates handles and receipts");
Check(state.Impact(100, 200, 100, Target()) is null, "map change clears pending shots");
state.Register(Receipt(nova), nova.BaseWeapon); state.Fire(Fire(nova));
for (var i = 0; i < 9; i++) Check(state.Impact(100, 200, 100, Target(i)) is not null, "shotgun pellet " + i);
Check(state.Impact(100, 200, 100, Target(9)) is null, "shotgun trace budget follows native bullet count");
state.ClearShots();
Check(state.OwnsTracer(300) && state.Impact(100, 200, 100, Target()) is null, "new round clears shots but preserves surviving instance");
foreach (var id in new[] { "glock18", "famas" })
{
    state.NewMap(); var weapon = catalog.Weapons.Single(x => x.Id == id);
    state.Register(Receipt(weapon), weapon.BaseWeapon);
    state.Fire(Fire(weapon) with { Bullets = 3, Burst = true });
    for (var i = 0; i < 3; i++) Check(state.Impact(100, 200, 100 + i * 5, Target(i)) is not null, id + " native burst bullet " + i);
    Check(state.Impact(100, 200, 111, Target(4)) is null, id + " burst bounded");
    state.Fire(Fire(weapon) with { Bullets = 3, Burst = true });
    state.Fire(Fire(weapon, 301, 101));
    Check(state.Impact(100, 200, 102, Target()) is null, id + " ordinary gun clears burst");
}
var settings = IcyTracerSettings.Load(Path.Combine(root, "config/icy_tracers.json"));
Check(settings.Enabled && settings.LifetimeSeconds == .12f, "reference style loaded");
Func<IArsenalEffectsApi> sharedProvider = ArsenalEffectsProvider.Resolve;
var firstService = new StubEffects(); var reloadedService = new StubEffects();
ArsenalEffectsProvider.Current = firstService;
Check(ReferenceEquals(sharedProvider(), firstService), "shared capability resolves first plugin");
ArsenalEffectsProvider.Current = null;
Check(sharedProvider() is null, "unload does not return stale plugin");
ArsenalEffectsProvider.Current = reloadedService;
Check(ReferenceEquals(sharedProvider(), reloadedService), "hot reload resolves replacement without stale closure");
ArsenalEffectsProvider.Current = null;
foreach (var bad in new[] {
 new IcyTracerSettings { LifetimeSeconds = float.NaN }, new() { LifetimeSeconds = 5 },
 new() { CoreWidth = 5 }, new() { GlowWidth = .1f }, new() { CoreRgb = [300, 0, 0] },
 new() { MaxBeamEntities = 100000 } })
{
    try { bad.Validate(); throw new Exception("Invalid settings accepted"); }
    catch (InvalidDataException) { checks++; }
}
Console.WriteLine($"PASS: {checks} tracer checks; all 12 weapons, exact handles, owners, shot attribution, cleanup and bounds");

sealed class StubEffects : IArsenalEffectsApi
{
    public Guid MapEpoch { get; } = Guid.NewGuid();
    public bool RegisterGranted(ArsenalWeaponReceipt receipt, Func<MuzzleQuery, Vector3?> resolveMuzzle) => false;
    public void Revoke(uint weaponHandle) { }
    public bool OwnsTracer(uint weaponHandle) => false;
}
