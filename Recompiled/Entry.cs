using RecompOne.Runtime.Cdrom;
using RecompOne.Runtime.Context;
using RecompOne.Runtime.Dispatch;
using RecompOne.Runtime.Memory;
using BiosKernel = RecompOne.Runtime.Bios.Bios;

namespace Recompiled;

public static class Entry
{
    public static void Run(IMemory m, string? cuePath = null)
    {
        RecompOne.Runtime.Runtime.Initialize("Option_Tuning_Car_Battle_Spec_R_JAP_PS1_ZTM");
        RecompOne.Runtime.Runtime.WaitForValidDisc();
        using var fs = CueFs.Open(cuePath ?? RecompOne.Runtime.Runtime.CdPath);
        var cd = new CdController(fs, m);
        m.SetCd(cd);
        Dispatcher.Register("main", new MainDispatchTable());
        Dispatcher.Register("ovl5", new Ovl5DispatchTable());
        RecompOne.Runtime.Modding.ModLoader.LoadAll();
        cd.LoadToMemory("SLPS_025.87", 0x80010000u, 0x800, 770048);
        Dispatcher.Load("main");
        var c = new CpuContext();
        c.GP = 0x00000000u;
        c.SP = 0x801FFFF0u;
        c.FP = c.SP;
        c.RA = 0u;
        RecompOne.Runtime.Runtime.SetContext(c, m);
        BiosKernel.Init(m);
        Dispatcher.Call(c, m, 0x8009AE3Cu);
    }
}
