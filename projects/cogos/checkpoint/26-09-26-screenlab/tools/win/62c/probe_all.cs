using System;
using System.Runtime.InteropServices;
using System.Text;

class ProbeAll
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

    [ComImport, Guid("00cddea8-939b-4b83-a340-a685226666cc"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDXGIOutput1
    {
        [PreserveSig] int SetPrivateData(ref Guid name, uint size, IntPtr data);
        [PreserveSig] int SetPrivateDataInterface(ref Guid name, IntPtr unk);
        [PreserveSig] int GetPrivateData(ref Guid name, ref uint size, IntPtr data);
        [PreserveSig] int GetParent(ref Guid riid, out IntPtr parent);
        [PreserveSig] int GetDesc(IntPtr desc);
        [PreserveSig] int GetDisplayModeList(uint fmt, uint flags, ref uint num, IntPtr modes);
        [PreserveSig] int FindClosestMatchingMode(IntPtr wanted, IntPtr closest, IntPtr dev);
        [PreserveSig] int WaitForVBlank();
        [PreserveSig] int TakeOwnership(IntPtr dev, int exclusive);
        [PreserveSig] int ReleaseOwnership();
        [PreserveSig] int GetGammaControlCapabilities(IntPtr caps);
        [PreserveSig] int SetGammaControl(IntPtr gamma);
        [PreserveSig] int GetGammaControl(IntPtr gamma);
        [PreserveSig] int SetDisplaySurface(IntPtr surface);
        [PreserveSig] int GetDisplaySurfaceData(IntPtr surface);
        [PreserveSig] int GetFrameStatistics(IntPtr stats);
        [PreserveSig] int DuplicateOutput(IntPtr device, out IntPtr dupl);
        [PreserveSig] int GetDisplayModeList1(uint fmt, uint flags, ref uint num, IntPtr modes);
        [PreserveSig] int FindClosestMatchingMode1(IntPtr wanted, IntPtr closest, IntPtr dev);
        [PreserveSig] int GetDisplaySurfaceData1(IntPtr resource);
        [PreserveSig] int DuplicateOutput1(IntPtr device, uint flags, uint numFormats, IntPtr formats, out IntPtr dupl);
    }

    [DllImport("dxgi.dll")]
    static extern int CreateDXGIFactory1(ref Guid riid, out IDXGIFactory1 factory);
    [DllImport("d3d11.dll")]
    static extern int D3D11CreateDevice(IntPtr adapter, uint driverType, IntPtr software,
        uint flags, IntPtr featureLevels, uint numFeatureLevels, uint sdkVersion,
        out IntPtr device, out uint featureLevel, out IntPtr context);
    [DllImport("user32.dll")]
    static extern int GetSystemMetrics(int n);
    [DllImport("kernel32.dll")]
    static extern uint WTSGetActiveConsoleSessionId();

    static string Hex(int hr) { return "0x" + ((uint)hr).ToString("X8"); }
    static void P(string s) { Console.WriteLine(s); Console.Out.Flush(); }

    delegate int OneArg(IntPtr self, IntPtr a);
    delegate int GetAdapterDel(IntPtr self, out IntPtr adapter);
    delegate int GetDescDel(IntPtr self, IntPtr desc);

    static int Main(string[] args)
    {
        P("ptrsize|" + IntPtr.Size + "|session|" + System.Diagnostics.Process.GetCurrentProcess().SessionId
          + "|console_session|" + WTSGetActiveConsoleSessionId()
          + "|remote_session|" + GetSystemMetrics(0x1000));
        Guid fiid = new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
        IDXGIFactory1 f;
        int hr = CreateDXGIFactory1(ref fiid, out f);
        Guid aiid = new Guid("29038f61-3839-4626-91fd-086879011a05");
        Guid oiid = new Guid("00cddea8-939b-4b83-a340-a685226666cc");
        for (uint ai = 0; ai < 6; ai++)
        {
            IntPtr ap;
            hr = f.EnumAdapters1(ai, out ap);
            if (hr < 0) { P("adapter" + ai + "|END|" + Hex(hr)); break; }
            IntPtr ap1;
            Marshal.QueryInterface(ap, ref aiid, out ap1);
            IDXGIAdapter1 adapter = (IDXGIAdapter1)Marshal.GetObjectForIUnknown(ap1);
            IntPtr ad = Marshal.AllocHGlobal(512);
            int had = adapter.GetDesc(ad);
            P("adapter" + ai + "|" + Hex(had) + "|" + Marshal.PtrToStringUni(ad));
            IntPtr dev, ctx; uint level = 0;
            int hdev = D3D11CreateDevice(ap1, 0, IntPtr.Zero, 0x20, IntPtr.Zero, 0, 7,
                out dev, out level, out ctx);
            if (hdev >= 0)
            {
                Guid diid = new Guid("54ec77fa-1377-44e6-8c32-88fd5f44c84c");
                IntPtr dip; Marshal.QueryInterface(dev, ref diid, out dip);
                IntPtr dvt = Marshal.ReadIntPtr(dip);
                var ga = (GetAdapterDel)Marshal.GetDelegateForFunctionPointer(
                    Marshal.ReadIntPtr(dvt, 7 * IntPtr.Size), typeof(GetAdapterDel));
                IntPtr devad; ga(dip, out devad);
                IntPtr devad1;
                Marshal.QueryInterface(devad, ref aiid, out devad1);
                IntPtr dd = Marshal.AllocHGlobal(512);
                var gd2 = (GetDescDel)Marshal.GetDelegateForFunctionPointer(
                    Marshal.ReadIntPtr(Marshal.ReadIntPtr(devad1), 8 * IntPtr.Size), typeof(GetDescDel));
                int hdd = gd2(devad1, dd);
                P("  device_adapter|same=" + (devad1 == ap1) + "|" + Hex(hdd) + "|" + Marshal.PtrToStringUni(dd));
            }
            for (uint oi = 0; oi < 5; oi++)
            {
                IntPtr outp;
                hr = adapter.EnumOutputs(oi, out outp);
                if (hr < 0) { P("  output" + oi + "|END|" + Hex(hr)); break; }
                IntPtr o1p;
                Marshal.QueryInterface(outp, ref oiid, out o1p);
                IDXGIOutput1 output = (IDXGIOutput1)Marshal.GetObjectForIUnknown(o1p);
                IntPtr od = Marshal.AllocHGlobal(512);
                int hod = output.GetDesc(od);
                IntPtr dupl;
                int hdup = hdev >= 0 ? output.DuplicateOutput(dev, out dupl) : hdev;
                IntPtr fmtbuf = Marshal.AllocHGlobal(4);
                Marshal.WriteInt32(fmtbuf, 87);
                IntPtr dupl1;
                int hdup1 = hdev >= 0 ? output.DuplicateOutput1(dev, 0, 1, fmtbuf, out dupl1) : hdev;
                P("  output" + oi + "|" + Marshal.PtrToStringUni(od)
                  + "|rect|" + Marshal.ReadInt32(od, 64) + "," + Marshal.ReadInt32(od, 68)
                  + "," + Marshal.ReadInt32(od, 72) + "," + Marshal.ReadInt32(od, 76)
                  + "|attached|" + Marshal.ReadInt32(od, 80)
                  + "|dup|" + Hex(hdup) + "|dup1|" + Hex(hdup1));
            }
        }
        return 0;
    }
}
