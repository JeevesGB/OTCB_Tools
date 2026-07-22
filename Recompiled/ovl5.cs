using RecompOne.Runtime.Context;
using RecompOne.Runtime.Dispatch;
using RecompOne.Runtime.Memory;

namespace Recompiled;

public static partial class Option_Tuning_Car_Battle_Spec_R_JAP_PS1_ZTM
{
}

public sealed class Ovl5DispatchTable : IOverlay
{
    public string Name => "ovl5";
    public int LbaStart => 37225;
    public uint Base => 0x80080000u;
    public uint Size => 0x45u;
    public IReadOnlyDictionary<uint, Action<CpuContext, IMemory>> Functions { get; } =
        new Dictionary<uint, Action<CpuContext, IMemory>>
        {
        };
}
