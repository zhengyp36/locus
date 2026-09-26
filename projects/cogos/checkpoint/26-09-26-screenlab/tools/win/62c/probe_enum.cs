using System;
using System.Runtime.InteropServices;

class ProbeEnum
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

    delegate int GetDescDel(IntPtr self, IntPtr desc);

    static string Hex(int hr) { return "0x" + ((uint)hr).ToString("X8"); }
    static void P(string s) { Console.WriteLine(s); Console.Out.Flush(); }

    static int Main(string[] args)
    {
        Guid fiid = new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
        IDXGIFactory1 f;
        CreateDXGIFactory1(ref fiid, out f);
        Guid aiid = new Guid("29038f61-3839-4626-91fd-086879011a05");
        for (uint ai = 0; ai < 4; ai++)
        {
            IntPtr ap;
            int hr = f.EnumAdapters1(ai, out ap);
            if (hr < 0) { P("adapter" + ai + "|enum|" + Hex(hr) + "|END"); break; }
            IntPtr ap1;
            Marshal.QueryInterface(ap, ref aiid, out ap1);
            IDXGIAdapter1 adapter = (IDXGIAdapter1)Marshal.GetObjectForIUnknown(ap1);
            IntPtr ad = Marshal.AllocHGlobal(512);
            int had = 0; try { had = adapter.GetDesc(ad); } catch (Exception ex) { had = ex.HResult; }
            P("adapter" + ai + "|0x" + ap.ToString("X") + "|desc|" + Hex(had) + "|" + Marshal.PtrToStringUni(ad));
            for (uint oi = 0; oi < 4; oi++)
            {
                IntPtr outp;
                hr = adapter.EnumOutputs(oi, out outp);
                if (hr < 0) { P("  output" + oi + "|enum|" + Hex(hr)); break; }
                IntPtr vt = Marshal.ReadIntPtr(outp);
                IntPtr buf = Marshal.AllocHGlobal(512);
                var getDesc = (GetDescDel)Marshal.GetDelegateForFunctionPointer(
                    Marshal.ReadIntPtr(vt, 8 * IntPtr.Size), typeof(GetDescDel));
                int gd = getDesc(outp, buf);
                P("  output" + oi + "|0x" + outp.ToString("X") + "|desc|" + Hex(gd)
                  + "|" + Marshal.PtrToStringUni(buf)
                  + "|rect|" + Marshal.ReadInt32(buf, 64) + "," + Marshal.ReadInt32(buf, 68)
                  + "," + Marshal.ReadInt32(buf, 72) + "," + Marshal.ReadInt32(buf, 76)
                  + "|attached|" + Marshal.ReadInt32(buf, 80));
            }
        }
        return 0;
    }
}
