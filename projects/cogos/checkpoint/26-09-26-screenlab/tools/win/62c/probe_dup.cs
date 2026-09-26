using System;
using System.Runtime.InteropServices;

class ProbeDup
{
    [ComImport, Guid("770aae78-f26f-4dba-a829-253c83d1b387"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDXGIFactory1
    {
        int SetPrivateData(ref Guid name, uint size, IntPtr data);
        int SetPrivateDataInterface(ref Guid name, IntPtr unk);
        int GetPrivateData(ref Guid name, ref uint size, IntPtr data);
        int GetParent(ref Guid riid, out IntPtr parent);
        int EnumAdapters(uint i, out IntPtr adapter);
        int MakeWindowAssociation(IntPtr hwnd, uint flags);
        int GetWindowAssociation(out IntPtr hwnd);
        int CreateSwapChain(IntPtr dev, IntPtr desc, out IntPtr sc);
        int CreateSoftwareAdapter(IntPtr mod, out IntPtr adapter);
        int EnumAdapters1(uint i, out IntPtr adapter);
        int IsCurrent();
    }

    [ComImport, Guid("29038f61-3839-4626-91fd-086879011a05"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDXGIAdapter1
    {
        int SetPrivateData(ref Guid name, uint size, IntPtr data);
        int SetPrivateDataInterface(ref Guid name, IntPtr unk);
        int GetPrivateData(ref Guid name, ref uint size, IntPtr data);
        int GetParent(ref Guid riid, out IntPtr parent);
        int EnumOutputs(uint i, out IntPtr output);
        int GetDesc(IntPtr desc);
        int CheckInterfaceSupport(ref Guid riid, out long umd);
        int GetDesc1(IntPtr desc);
    }

    [DllImport("dxgi.dll")]
    static extern int CreateDXGIFactory1(ref Guid riid, out IDXGIFactory1 factory);
    [DllImport("d3d11.dll")]
    static extern int D3D11CreateDevice(IntPtr adapter, uint driverType, IntPtr software,
        uint flags, IntPtr featureLevels, uint numFeatureLevels, uint sdkVersion,
        out IntPtr device, out uint featureLevel, out IntPtr context);

    delegate int GetDescDel(IntPtr self, IntPtr desc);
    delegate int DupDel(IntPtr self, IntPtr device, out IntPtr dupl);
    delegate int OneArgDel(IntPtr self, IntPtr a);

    static string Hex(int hr) { return "0x" + ((uint)hr).ToString("X8"); }
    static void P(string s) { Console.WriteLine(s); Console.Out.Flush(); }

    static int Main(string[] args)
    {
        Guid fiid = new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
        IDXGIFactory1 f;
        int hr = CreateDXGIFactory1(ref fiid, out f);
        P("create_factory|" + Hex(hr));
        IntPtr ap;
        f.EnumAdapters1(0, out ap);
        Guid aiid = new Guid("29038f61-3839-4626-91fd-086879011a05");
        IntPtr ap1;
        Marshal.QueryInterface(ap, ref aiid, out ap1);
        IDXGIAdapter1 adapter = (IDXGIAdapter1)Marshal.GetObjectForIUnknown(ap1);
        IntPtr avt = Marshal.ReadIntPtr(ap1);
        P("adapter|0x" + ap1.ToString("X") + "|vtable|0x" + avt.ToString("X"));
        IntPtr abuf = Marshal.AllocHGlobal(512);
        var agd = (GetDescDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(avt, 8 * IntPtr.Size), typeof(GetDescDel));
        int ahd = agd(ap1, abuf);
        P("raw_adapter_getdesc|" + Hex(ahd) + "|" + Marshal.PtrToStringUni(abuf));
        IntPtr outp;
        adapter.EnumOutputs(0, out outp);
        IntPtr vt = Marshal.ReadIntPtr(outp);
        P("output|0x" + outp.ToString("X") + "|vtable|0x" + vt.ToString("X"));
        P("  adapter_vt==output_vt? " + (avt == vt));
        for (int i = 0; i < 8; i++)
            P("  vt" + i + "|a=0x" + Marshal.ReadIntPtr(avt, i * IntPtr.Size).ToString("X")
              + "|o=0x" + Marshal.ReadIntPtr(vt, i * IntPtr.Size).ToString("X"));
        for (int i = 6; i <= 12; i++)
            P("  slot" + i + "|0x" + Marshal.ReadIntPtr(vt, i * IntPtr.Size).ToString("X"));

        IntPtr dsc = Marshal.AllocHGlobal(512);
        var getDesc = (GetDescDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(vt, 8 * IntPtr.Size), typeof(GetDescDel));
        P("calling raw slot8 with valid buffer...");
        int gd = getDesc(outp, dsc);
        P("raw_getdesc|" + Hex(gd) + "|name|" + Marshal.PtrToStringUni(dsc)
          + "|rect|" + Marshal.ReadInt32(dsc, 64) + "," + Marshal.ReadInt32(dsc, 68)
          + "," + Marshal.ReadInt32(dsc, 72) + "," + Marshal.ReadInt32(dsc, 76)
          + "|attached|" + Marshal.ReadInt32(dsc, 80));

        IntPtr unk = Marshal.GetIUnknownForObject(adapter);
        IntPtr dev, ctx; uint level;
        hr = D3D11CreateDevice(unk, 0, IntPtr.Zero, 0x20, IntPtr.Zero, 0, 7, out dev, out level, out ctx);
        P("d3d11_with_adapter|" + Hex(hr) + "|dev|0x" + dev.ToString("X") + "|level|" + level);

        var dup = (DupDel)Marshal.GetDelegateForFunctionPointer(
            Marshal.ReadIntPtr(vt, 20 * IntPtr.Size), typeof(DupDel));
        P("calling raw slot20 DuplicateOutput...");
        IntPtr dupl;
        int hd = dup(outp, dev, out dupl);
        P("raw_duplicate|" + Hex(hd) + "|dupl|0x" + dupl.ToString("X"));

        if (hd < 0)
        {
            IntPtr dev2, ctx2; uint lvl2;
            hr = D3D11CreateDevice(IntPtr.Zero, 1, IntPtr.Zero, 0x20, IntPtr.Zero, 0, 7, out dev2, out lvl2, out ctx2);
            P("d3d11_hw_only|" + Hex(hr) + "|dev|0x" + dev2.ToString("X") + "|level|" + lvl2);
            IntPtr dupl2;
            int hd2 = dup(outp, dev2, out dupl2);
            P("raw_duplicate_hw|" + Hex(hd2) + "|dupl|0x" + dupl2.ToString("X"));
        }
        return 0;
    }
}
