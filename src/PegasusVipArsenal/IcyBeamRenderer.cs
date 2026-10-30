using System.Drawing;
using System.Numerics;
using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Modules.Utils;
using GameVector = CounterStrikeSharp.API.Modules.Utils.Vector;

namespace PegasusVipArsenal;

/// <summary>Two short-lived, depth-tested world beams; no damage, ESP or permanent entities.</summary>
internal sealed class IcyBeamRenderer(IcyTracerSettings settings)
{
    private sealed record Active(CHandle<CBeam> Handle, Color Color, float Created)
    { public int FadeStep { get; set; } }
    private readonly List<Active> _active = new();

    public void Draw(Vector3 start, Vector3 end, float now)
    {
        if (_active.Count + 2 > settings.MaxBeamEntities || Vector3.DistanceSquared(start, end) < 1) return;
        CBeam? glow = null, core = null;
        try
        {
            glow = Create(start, end, settings.GlowWidth, settings.GlowRgb, 95);
            core = Create(start, end, settings.CoreWidth, settings.CoreRgb, 255);
            _active.Add(new(new(glow.EntityHandle.Raw), glow.Render, now));
            _active.Add(new(new(core.EntityHandle.Raw), core.Render, now));
        }
        catch
        {
            if (glow is { IsValid: true }) glow.Remove();
            if (core is { IsValid: true }) core.Remove();
            throw;
        }
    }

    private static CBeam Create(Vector3 start, Vector3 end, float width, int[] rgb, int alpha)
    {
        var beam = Utilities.CreateEntityByName<CBeam>("beam")
            ?? throw new InvalidOperationException("CS2 could not create a beam");
        try
        {
            beam.BeamType = BeamType_t.BEAM_POINTS;
            beam.NumBeamEnts = 2;
            beam.Width = width; beam.EndWidth = width * .65f;
            beam.RenderMode = RenderMode_t.kRenderTransAlpha;
            beam.Render = Color.FromArgb(alpha, rgb[0], rgb[1], rgb[2]);
            beam.Damage = 0; beam.Amplitude = 0;
            beam.Teleport(ToGame(start));
            beam.EndPos.X = end.X; beam.EndPos.Y = end.Y; beam.EndPos.Z = end.Z;
            beam.DispatchSpawn();
            Utilities.SetStateChanged(beam, "CBeam", "m_vecEndPos");
            return beam;
        }
        catch { if (beam.IsValid) beam.Remove(); throw; }
    }

    public void Tick(float now)
    {
        for (var i = _active.Count - 1; i >= 0; i--)
        {
            var active = _active[i];
            var beam = active.Handle.Value;
            if (beam is not { IsValid: true }) { _active.RemoveAt(i); continue; }
            var age = now - active.Created;
            if (age < 0 || age >= settings.LifetimeSeconds)
            { beam.Remove(); _active.RemoveAt(i); continue; }
            var step = (int)(age / settings.LifetimeSeconds * 4);
            if (step == active.FadeStep) continue;
            active.FadeStep = step;
            beam.Render = Color.FromArgb((int)(active.Color.A * (1 - age / settings.LifetimeSeconds)), active.Color);
            Utilities.SetStateChanged(beam, "CBaseModelEntity", "m_clrRender");
        }
    }

    public void Clear(bool removeEntities)
    {
        if (removeEntities)
            foreach (var active in _active)
                if (active.Handle.Value is { IsValid: true } beam) beam.Remove();
        _active.Clear();
    }
    internal static GameVector ToGame(Vector3 point) => new(point.X, point.Y, point.Z);
}
