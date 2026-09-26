using System;
using System.Runtime.InteropServices;

class ProbeDup3
{
    [ComImport, Guid("770aae78-f26f-4dba-a829-253c83d1b387"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDXGIFactory1
    {
        [PreserveSig] int SetPrivateData(ref Guid name, uint size, IntPtr data);
        [PreserveSig] int SetPrivateDataInterface(ref Guid name, IntPtr unk);
        [PreserveSig] int GetPrivateData(ref Guid name, ref uint size, IntPtr data);
        [PreserveSig] int GetParent(ref Guid riid, out IntPtr parent);
        [PreserveSig] int EnumAdapters(uint i, out IntPtr adapter);
        [PreserveSig] int MakeWindowAssociation(IntPtr hwnd, uint flags);
        [PreserveSig] int GetWindowAssociation(out IntPtr hwnd);
        [PreserveSig] int CreateSwapChain(IntPtr dev, IntPtr desc, out IntPtr sc);
        [PreserveSig] int CreateSoftwareAdapter(IntPtr mod, out IntPtr adapter);
        [PreserveSig] int EnumAdapters1(uint i, out IntPtr adapter);
        [PreserveSig] int IsCurrent();
    }

    [ComImport, Guid("29038f61-3839-4626-91fd-086879011a05"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDXGIAdapter1
    {
        [PreserveSig] int SetPrivateData(ref Guid name, uint size, IntPtr data);
        [PreserveSig] int SetPrivateDataInterface(ref Guid name, IntPtr unk);
        [PreserveSig] int GetPrivateData(ref Guid name, ref uint size, IntPtr data);
        [PreserveSig] int GetParent(ref Guid riid, out IntPtr parent);
        [PreserveSig] int EnumOutputs(uint i, out IntPtr output);
        [PreserveSig] int GetDesc(IntPtr desc);
        [PreserveSig] int CheckInterfaceSupport(ref Guid riid, out long umd);
        [PreserveSig] int GetDesc1(IntPtr desc);
    }

    [DllImport("dxgi.dll")]
    static extern int CreateDXGIFactory1(ref Guid riid, out IDXGIFactory1 factory);
    [DllImport("d3d11.dll")]
    static extern int D3D11CreateDevice(IntPtr adapter, uint driverType, IntPtr software,
        uint flags, IntPtr featureLevels, uint numFeatureLevels, uint sdkVersion,
        out IntPtr device, out uint featureLevel, out IntPtr context);

    delegate int GetDescDel(IntPtr self, IntPtr desc);
    delegate int DupDel(IntPtr self, IntPtr device, IntPtr ppDupl);
    delegate int AcquireDel(IntPtr self, uint timeout, IntPtr info, IntPtr ppRes);
    delegate int RectsDel(IntPtr self, uint size, IntPtr buf, IntPtr pNeed);
    delegate int ReleaseFrameDel(IntPtr self);

    static string Hex(int hr) { return "0x" + ((uint)hr).ToString("X8"); }
    static void P(string s) { Console.WriteLine(s); Console.Out.Flush(); }

    static IntPtr Fn(IntPtr vt, int slot, Type t)
    {
        return Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(vt, slot * IntPtr.Size), t) is object
            ? Marshal.ReadIntPtr(vt, slot * IntPtr.Size) : IntPtr.Zero;
    }

    static int Main(string[] args)
    {
        Guid fiid = new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
        IDXGIFactory1 f;
        int hr = CreateDXGIFactory1(ref fiid, out f);
        IntPtr ap;
        f.EnumAdapters1(0, out ap);
        Guid aiid = new Guid("29038f61-3839-4626-91fd-086879011a05");
        IntPtr ap1;
        Marshal.QueryInterface(ap, ref aiid, out ap1);
        IDXGIAdapter1 adapter = (IDXGIAdapter1)Marshal.GetObjectForIUnknown(ap1);
        IntPtr outp;
        adapter.EnumOutputs(0, out outp);
        IntPtr vt = Marshal.ReadIntPtr(outp);

        IntPtr dev, ctx; uint level;
        hr = D3D11CreateDevice(ap1, 0, IntPtr.Zero, 0x20, IntPtr.Zero, 0, 7, out dev, out level, out ctx);
        P("d3d11|" + Hex(hr) + "|dev|0x" + dev.ToString("X"));

        IntPtr pp = Marshal.AllocHGlobal(IntPtr.Size);
        Marshal.WriteIntPtr(pp, IntPtr.Zero);
        P("vt|0x" + vt.ToString("X") + "|slot19|0x" + Marshal.ReadIntPtr(vt, 19 * IntPtr.Size).ToString("X"));
        var dup = (DupDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(vt, 19 * IntPtr.Size), typeof(DupDel));
        int hd;
        try { hd = dup(outp, dev, pp); }
        catch (Exception ex) { P("dup_exc|" + ex.GetType().Name + "|" + ex.Message); return 0; }
        IntPtr dupl = Marshal.ReadIntPtr(pp);
        P("dup_slot19|" + Hex(hd) + "|dupl|0x" + dupl.ToString("X"));

        if (dupl == IntPtr.Zero)
        {
            IntPtr devHw, ctxHw; uint lvlHw;
            int hh = D3D11CreateDevice(IntPtr.Zero, 1, IntPtr.Zero, 0x20, IntPtr.Zero, 0, 7, out devHw, out lvlHw, out ctxHw);
            Marshal.WriteIntPtr(pp, IntPtr.Zero);
            int h2 = dup(outp, devHw, pp);
            dupl = Marshal.ReadIntPtr(pp);
            P("dup_hw|" + Hex(h2) + "|dev|0x" + devHw.ToString("X") + "|dupl|0x" + dupl.ToString("X"));
        }
        if (dupl == IntPtr.Zero) return 0;

        IntPtr dvt = Marshal.ReadIntPtr(dupl);
        var acquire = (AcquireDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(dvt, 8 * IntPtr.Size), typeof(AcquireDel));
        var dirty = (RectsDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(dvt, 9 * IntPtr.Size), typeof(RectsDel));
        var release = (ReleaseFrameDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(dvt, 14 * IntPtr.Size), typeof(ReleaseFrameDel));

        IntPtr info = Marshal.AllocHGlobal(64);
        IntPtr pres = Marshal.AllocHGlobal(IntPtr.Size);
        Marshal.WriteIntPtr(pres, IntPtr.Zero);
        int ha = acquire(dupl, 100, info, pres);
        IntPtr res = Marshal.ReadIntPtr(pres);
        P("acquire|" + Hex(ha) + "|res|0x" + res.ToString("X"));
        IntPtr rbuf = Marshal.AllocHGlobal(1 << 16);
        IntPtr pneed = Marshal.AllocHGlobal(4);
        Marshal.WriteInt32(pneed, 0);
        int hdr = dirty(dupl, (uint)(1 << 16), rbuf, pneed);
        uint need = (uint)Marshal.ReadInt32(pneed);
        P("dirty|" + Hex(hdr) + "|need|" + need + "|n|" + (need / 16));
        if (need > 0)
            P("rect0|" + Marshal.ReadInt32(rbuf, 0) + "," + Marshal.ReadInt32(rbuf, 4)
              + "," + Marshal.ReadInt32(rbuf, 8) + "," + Marshal.ReadInt32(rbuf, 12));
        if (res != IntPtr.Zero) Marshal.Release(res);
        release(dupl);
        return 0;
    }
}
