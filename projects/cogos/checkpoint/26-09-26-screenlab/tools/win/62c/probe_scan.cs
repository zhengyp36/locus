using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

class ProbeScan
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

    delegate int D5(IntPtr self, IntPtr a, IntPtr b, IntPtr c, IntPtr d);
    static string Hex(int hr) { return "0x" + ((uint)hr).ToString("X8"); }

    static IntPtr GetOutput()
    {
        Guid fiid = new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
        IDXGIFactory1 f;
        CreateDXGIFactory1(ref fiid, out f);
        IntPtr ap;
        f.EnumAdapters1(0, out ap);
        Guid aiid = new Guid("29038f61-3839-4626-91fd-086879011a05");
        IntPtr ap1;
        Marshal.QueryInterface(ap, ref aiid, out ap1);
        IDXGIAdapter1 adapter = (IDXGIAdapter1)Marshal.GetObjectForIUnknown(ap1);
        IntPtr outp;
        adapter.EnumOutputs(0, out outp);
        return outp;
    }

    static void Main(string[] args)
    {
        if (args.Length >= 2 && args[0] == "child")
        {
            int idx = int.Parse(args[1]);
            IntPtr outp = GetOutput();
            IntPtr vt = Marshal.ReadIntPtr(outp);
            IntPtr fn = Marshal.ReadIntPtr(vt, idx * IntPtr.Size);
            IntPtr buf = Marshal.AllocHGlobal(1024);
            for (int i = 0; i < 1024; i++) Marshal.WriteByte(buf, i, 0);
            var d = (D5)Marshal.GetDelegateForFunctionPointer(fn, typeof(D5));
            int hr = d(outp, buf, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
            string nm = Marshal.PtrToStringUni(buf);
            if (nm != null && nm.Length > 40) nm = nm.Substring(0, 40);
            Console.WriteLine("ctx|" + idx + "|" + Hex(hr) + "|str|" + (nm ?? "")
                + "|i64@64|" + Marshal.ReadInt32(buf, 64) + "," + Marshal.ReadInt32(buf, 68)
                + "," + Marshal.ReadInt32(buf, 72) + "," + Marshal.ReadInt32(buf, 76));
            return;
        }

        IntPtr o = GetOutput();
        Console.WriteLine("vt|0x" + Marshal.ReadIntPtr(o).ToString("X"));
        string self = System.Reflection.Assembly.GetExecutingAssembly().Location;
        for (int i = 3; i <= 26; i++)
        {
            var psi = new ProcessStartInfo(self, "child " + i)
            { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
            var p = Process.Start(psi);
            string so = p.StandardOutput.ReadToEnd();
            string se = p.StandardError.ReadToEnd();
            p.WaitForExit();
            so = so.Trim();
            if (so.Length > 0) Console.WriteLine(so);
            else Console.WriteLine("ctx|" + i + "|CRASH|exit=" + p.ExitCode);
        }
    }
}
