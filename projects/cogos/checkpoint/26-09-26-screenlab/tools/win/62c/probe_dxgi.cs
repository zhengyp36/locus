using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

class ProbeDxgi
{
    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int x, y; }
    [StructLayout(LayoutKind.Sequential)]
    public struct POINTER_POSITION { public POINT Position; public int Visible; }
    [StructLayout(LayoutKind.Sequential)]
    public struct FRAME_INFO
    {
        public long LastPresentTime;
        public long LastMouseUpdateTime;
        public uint AccumulatedFrames;
        public int RectsCoalesced;
        public int ProtectedContentMaskedOut;
        public POINTER_POSITION PointerPosition;
        public uint TotalMetadataBufferSize;
        public uint PointerShapeBufferSize;
    }
    [StructLayout(LayoutKind.Sequential)]
    public struct MODE_DESC
    {
        public uint Width, Height;
        public int RefreshNum, RefreshDen;
        public uint Format, ScanlineOrdering, Scaling;
    }
    [StructLayout(LayoutKind.Sequential)]
    public struct OUTDUPL_DESC
    {
        public MODE_DESC ModeDesc;
        public uint Rotation;
        public int DesktopImageInSystemMemory;
    }

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
        [PreserveSig] int DuplicateOutput1(IntPtr device, uint flags, uint numFormats, IntPtr formats, out IDXGIOutputDuplication dupl);
    }

    [ComImport, Guid("191cfac3-a341-470d-b26e-a864f428319c"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDXGIOutputDuplication
    {
        [PreserveSig] int SetPrivateData(ref Guid name, uint size, IntPtr data);
        [PreserveSig] int SetPrivateDataInterface(ref Guid name, IntPtr unk);
        [PreserveSig] int GetPrivateData(ref Guid name, ref uint size, IntPtr data);
        [PreserveSig] int GetParent(ref Guid riid, out IntPtr parent);
        [PreserveSig] int GetDesc(out OUTDUPL_DESC desc);
        [PreserveSig] int AcquireNextFrame(uint timeout, out FRAME_INFO info, out IntPtr resource);
        [PreserveSig] int GetFrameDirtyRects(uint size, IntPtr buf, out uint required);
        [PreserveSig] int GetFrameMoveRects(uint size, IntPtr buf, out uint required);
        [PreserveSig] int GetFramePointerShape(uint size, IntPtr buf, out uint required, IntPtr info);
        [PreserveSig] int MapDesktopSurface(out IntPtr locked);
        [PreserveSig] int UnMapDesktopSurface();
        [PreserveSig] int ReleaseFrame();
    }

    [DllImport("dxgi.dll")]
    static extern int CreateDXGIFactory1(ref Guid riid, out IDXGIFactory1 factory);

    [DllImport("d3d11.dll")]
    static extern int D3D11CreateDevice(IntPtr adapter, uint driverType, IntPtr software,
        uint flags, IntPtr featureLevels, uint numFeatureLevels, uint sdkVersion,
        out IntPtr device, out uint featureLevel, out IntPtr context);

    [DllImport("user32.dll")]
    static extern bool SetProcessDPIAware();

    const uint D3D11_CREATE_DEVICE_BGRA_SUPPORT = 0x20;
    const uint DXGI_ERROR_WAIT_TIMEOUT = 0x887A0027;
    const uint DXGI_ERROR_ACCESS_LOST = 0x887A0026;

    static string Hex(int hr) { return "0x" + ((uint)hr).ToString("X8"); }

    static int Main(string[] args)
    {
        double dur = args.Length > 0 ? double.Parse(args[0]) : 8.0;
        var sb = new StringBuilder();
        sb.Append("{\n");
        try { SetProcessDPIAware(); } catch { }
        sb.Append("  \"probe\": \"dxgi_csharp\",\n");
        sb.Append("  \"duration_s\": ").Append(dur).Append(",\n");
        try
        {
            Guid fiid = new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
            IDXGIFactory1 factory;
            int hr = CreateDXGIFactory1(ref fiid, out factory);
            sb.Append("  \"create_factory_hr\": \"").Append(Hex(hr)).Append("\",\n");

            IntPtr ap;
            hr = factory.EnumAdapters1(0, out ap);
            Guid aiid = new Guid("29038f61-3839-4626-91fd-086879011a05");
            IntPtr ap1;
            hr = Marshal.QueryInterface(ap, ref aiid, out ap1);
            IDXGIAdapter1 adapter = (IDXGIAdapter1)Marshal.GetObjectForIUnknown(ap1);

            IntPtr outp;
            hr = adapter.EnumOutputs(0, out outp);
            if (hr < 0) { sb.Append("  \"error\": \"enum_outputs\"\n}\n"); Console.Write(sb.ToString()); return 0; }
            Guid oiid = new Guid("00cddea8-939b-4b83-a340-a685226666cc");
            IntPtr o1p;
            hr = Marshal.QueryInterface(outp, ref oiid, out o1p);
            IDXGIOutput1 output = (IDXGIOutput1)Marshal.GetObjectForIUnknown(o1p);

            IntPtr dsc = Marshal.AllocHGlobal(512);
            hr = adapter.GetDesc(dsc);
            sb.Append("  \"adapter_name\": \"").Append(Marshal.PtrToStringUni(dsc)).Append("\",\n");
            hr = output.GetDesc(dsc);
            sb.Append("  \"output_name\": \"").Append(Marshal.PtrToStringUni(dsc)).Append("\",\n");
            sb.Append("  \"output_rect\": [")
              .Append(Marshal.ReadInt32(dsc, 64)).Append(",")
              .Append(Marshal.ReadInt32(dsc, 68)).Append(",")
              .Append(Marshal.ReadInt32(dsc, 72)).Append(",")
              .Append(Marshal.ReadInt32(dsc, 76)).Append("],\n");
            sb.Append("  \"output_attached\": ").Append(Marshal.ReadInt32(dsc, 80)).Append(",\n");

            IntPtr unk = Marshal.GetIUnknownForObject(adapter);
            IntPtr dev, ctx; uint level = 0;
            hr = D3D11CreateDevice(ap1, 0, IntPtr.Zero, D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                IntPtr.Zero, 0, 7, out dev, out level, out ctx);
            sb.Append("  \"d3d11_hr\": \"").Append(Hex(hr)).Append("\",\n");
            sb.Append("  \"d3d11_dev\": \"").Append(dev.ToString("X")).Append("\",\n");
            sb.Append("  \"d3d11_level\": ").Append(level).Append(",\n");

            IntPtr duplp = IntPtr.Zero;
            hr = output.DuplicateOutput(dev, out duplp);
            sb.Append("  \"duplicate_output_hr\": \"").Append(Hex(hr)).Append("\",\n");
            sb.Append("  \"dupl_ptr\": \"").Append(duplp.ToString("X")).Append("\",\n");
            if (hr < 0 || duplp == IntPtr.Zero)
            {
                IntPtr dev2, ctx2; uint level2 = 0;
                int hr2 = D3D11CreateDevice(IntPtr.Zero, 1, IntPtr.Zero, D3D11_CREATE_DEVICE_BGRA_SUPPORT,
                    IntPtr.Zero, 0, 7, out dev2, out level2, out ctx2);
                sb.Append("  \"fallback_hw_hr\": \"").Append(Hex(hr2)).Append("\",\n");
                IntPtr dp2 = IntPtr.Zero;
                int hr3 = hr2 >= 0 ? output.DuplicateOutput(dev2, out dp2) : hr2;
                sb.Append("  \"fallback_duplicate_hr\": \"").Append(Hex(hr3)).Append("\",\n");
                sb.Append("  \"error\": \"duplicate\"\n}\n");
                Console.Write(sb.ToString());
                return 0;
            }
            IDXGIOutputDuplication dupl = (IDXGIOutputDuplication)Marshal.GetObjectForIUnknown(duplp);

            OUTDUPL_DESC dd;
            dupl.GetDesc(out dd);
            sb.Append("  \"dupl_desc\": {\"mode\": ").Append(dd.ModeDesc.Width).Append("x").Append(dd.ModeDesc.Height)
              .Append(", \"rotation\": ").Append(dd.Rotation)
              .Append(", \"sysmem\": ").Append(dd.DesktopImageInSystemMemory).Append("},\n");

            uint BUFSZ = 1u << 20;
            IntPtr bufD = Marshal.AllocHGlobal((int)BUFSZ);
            IntPtr bufM = Marshal.AllocHGlobal((int)BUFSZ);

            var sw = Stopwatch.StartNew();
            var cpu0 = Process.GetCurrentProcess().TotalProcessorTime;
            long acquired = 0, timeout = 0, accessLost = 0, other = 0;
            long dirtyFrames = 0, dirtyTotal = 0, dirtyMax = 0, dirtyMin = -1;
            long moveFrames = 0, moveTotal = 0;
            long coalesced = 0, protectedOut = 0, pointerFrames = 0;
            string dirtyExamples = "", moveExamples = "";
            int exD = 0, exM = 0;
            double ivMin = -1, ivMax = 0, ivSum = 0, last = -1; long ivN = 0;

            while (sw.Elapsed.TotalSeconds < dur)
            {
                FRAME_INFO fi;
                IntPtr res;
                hr = dupl.AcquireNextFrame(100, out fi, out res);
                uint u = (uint)hr;
                if (u == DXGI_ERROR_WAIT_TIMEOUT) { timeout++; continue; }
                if (u == DXGI_ERROR_ACCESS_LOST) { accessLost++; break; }
                if (hr < 0) { other++; break; }
                acquired++;
                if (fi.RectsCoalesced != 0) coalesced++;
                if (fi.ProtectedContentMaskedOut != 0) protectedOut++;
                if (fi.PointerPosition.Visible != 0) pointerFrames++;
                double now = sw.Elapsed.TotalSeconds;
                if (last >= 0) { double iv = (now - last) * 1000.0; ivSum += iv; ivN++; if (ivMin < 0 || iv < ivMin) ivMin = iv; if (iv > ivMax) ivMax = iv; }
                last = now;

                uint need;
                int hrd = dupl.GetFrameDirtyRects(BUFSZ, bufD, out need);
                if (hrd >= 0)
                {
                    int n = (int)(need / 16);
                    if (n > 0)
                    {
                        dirtyFrames++; dirtyTotal += n;
                        if (n > dirtyMax) dirtyMax = n;
                        if (dirtyMin < 0 || n < dirtyMin) dirtyMin = n;
                        if (exD < 6)
                        {
                            var r = new StringBuilder();
                            for (int i = 0; i < n && i < 6; i++)
                            {
                                int off = i * 16;
                                if (i > 0) r.Append(", ");
                                r.Append("[").Append(Marshal.ReadInt32(bufD, off)).Append(",")
                                 .Append(Marshal.ReadInt32(bufD, off + 4)).Append(",")
                                 .Append(Marshal.ReadInt32(bufD, off + 8)).Append(",")
                                 .Append(Marshal.ReadInt32(bufD, off + 12)).Append("]");
                            }
                            if (dirtyExamples.Length > 0) dirtyExamples += ", ";
                            dirtyExamples += "{\"n\": " + n + ", \"rects\": [" + r + "]}";
                            exD++;
                        }
                    }
                }
                uint need2;
                int hrm = dupl.GetFrameMoveRects(BUFSZ, bufM, out need2);
                if (hrm >= 0)
                {
                    int n = (int)(need2 / 16);
                    if (n > 0)
                    {
                        moveFrames++; moveTotal += n;
                        if (exM < 6)
                        {
                            var r = new StringBuilder();
                            for (int i = 0; i < n && i < 6; i++)
                            {
                                int off = i * 16;
                                if (i > 0) r.Append(", ");
                                r.Append("[").Append(Marshal.ReadInt32(bufM, off)).Append(",")
                                 .Append(Marshal.ReadInt32(bufM, off + 4)).Append(",")
                                 .Append(Marshal.ReadInt32(bufM, off + 8)).Append(",")
                                 .Append(Marshal.ReadInt32(bufM, off + 12)).Append("]");
                            }
                            if (moveExamples.Length > 0) moveExamples += ", ";
                            moveExamples += "{\"n\": " + n + ", \"rects\": [" + r + "]}";
                            exM++;
                        }
                    }
                }
                if (res != IntPtr.Zero) Marshal.Release(res);
                dupl.ReleaseFrame();
            }

            sw.Stop();
            var cpu = Process.GetCurrentProcess().TotalProcessorTime - cpu0;
            double wall = sw.Elapsed.TotalSeconds;
            sb.Append("  \"acquired\": ").Append(acquired).Append(",\n");
            sb.Append("  \"timeout\": ").Append(timeout).Append(",\n");
            sb.Append("  \"access_lost\": ").Append(accessLost).Append(",\n");
            sb.Append("  \"other\": ").Append(other).Append(",\n");
            sb.Append("  \"dirty\": {\"frames\": ").Append(dirtyFrames).Append(", \"total\": ").Append(dirtyTotal)
              .Append(", \"max\": ").Append(dirtyMax).Append(", \"min\": ").Append(dirtyMin)
              .Append(", \"examples\": [").Append(dirtyExamples).Append("]},\n");
            sb.Append("  \"move\": {\"frames\": ").Append(moveFrames).Append(", \"total\": ").Append(moveTotal)
              .Append(", \"examples\": [").Append(moveExamples).Append("]},\n");
            sb.Append("  \"coalesced\": ").Append(coalesced).Append(",\n");
            sb.Append("  \"protected\": ").Append(protectedOut).Append(",\n");
            sb.Append("  \"pointer_frames\": ").Append(pointerFrames).Append(",\n");
            sb.Append("  \"frame_interval_ms\": {\"min\": ").Append(ivMin < 0 ? 0 : Math.Round(ivMin, 2))
              .Append(", \"max\": ").Append(Math.Round(ivMax, 2))
              .Append(", \"avg\": ").Append(ivN > 0 ? Math.Round(ivSum / ivN, 2) : 0).Append("},\n");
            sb.Append("  \"wall_s\": ").Append(Math.Round(wall, 3)).Append(",\n");
            sb.Append("  \"cpu_s\": ").Append(Math.Round(cpu.TotalSeconds, 4)).Append(",\n");
            sb.Append("  \"cpu_pct\": ").Append(wall > 0 ? Math.Round(100.0 * cpu.TotalSeconds / wall, 2) : 0).Append("\n");
            sb.Append("}\n");
            Console.Write(sb.ToString());
            return 0;
        }
        catch (Exception ex)
        {
            sb.Append("  \"exception\": \"").Append(ex.GetType().Name).Append(": ")
              .Append(ex.Message.Replace("\"", "'").Replace("\r", " ").Replace("\n", " "))
              .Append("\",\n  \"exception_hr\": \"0x").Append(((uint)ex.HResult).ToString("X8"))
              .Append("\"\n}\n");
            Console.Write(sb.ToString());
            return 1;
        }
    }
}
