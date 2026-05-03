
void PlayIntroAndInit(int *param_1)

{
  bool bVar1;
  int iVar2;
  
  InitGameSystems();
  InitGraphics();
  SetHeapBase(&DAT_800d1300);
  SetVRAMBase(&DAT_801f8000);
  InitMemoryState();
  InitRenderer(&DAT_800b54b0);
  ActivateDisplay();
  DAT_800cd5e0 = &DAT_800cd5b0;
  g_Buffer0 = MemAlloc(0x10000);
  g_Buffer1 = MemAlloc(0x11000);
  g_Buffer2 = MemAlloc(0x1e000);
  g_Buffer3 = MemAlloc(0x1e000);
  g_Buffer4 = MemAlloc(0x7800);
  g_Buffer5 = MemAlloc(0x7800);
  g_StreamType = *(undefined2 *)((int)param_1 + 6);
  g_StreamMaxSector = *(undefined2 *)((int)param_1 + 10);
  g_StreamChannel = (undefined2)param_1[2];
  g_StreamSectorAddr = TrackToSectorAddr((int)(short)param_1[1]);
  g_FramePosX_Base = *g_DisplayConfig + (short)param_1[3];
  g_FramePosY_Base = g_DisplayConfig[2] + *(short *)((int)param_1 + 0xe);
  g_FramePosX_Base2 = g_DisplayConfig[1] + (short)param_1[3];
  g_FramePosY_Base2 = g_DisplayConfig[3] + *(short *)((int)param_1 + 0xe);
  InitFMVStream();
  g_DisplayBufferPtr = &g_DisplayBufferIndex;
  g_DisplayActive = 0;
  FadeAudioVolume(0x100);
  do {
    StreamUpdate();
    iVar2 = 0;
    if (g_StreamDone == 0) {
      iVar2 = 1000000;
      do {
        if (g_StreamFlag1 != 0) break;
        bVar1 = -1 < iVar2;
        iVar2 = iVar2 + -1;
      } while (bVar1);
      g_StreamFlag1 = 0;
      g_StreamFlag2 = 0xffffffff;
      if (g_StreamActive != 0) {
        g_StreamDone = -1;
        DecDCToutCallback((func *)0x0);
        StopCDStream();
        do {
          iVar2 = CdControlB('\t',(u_char *)0x0,(u_char *)0x0);
        } while (iVar2 == 0);
      }
      iVar2 = -1;
      g_StreamRetryCount = g_StreamRetryCount + 1;
    }
    if ((*param_1 != 0) && ((g_PadButtons & 0x8f0) != 0)) {
      g_StreamActive = -1;
    }
    VsyncWait();
    if (iVar2 == 0) {
      FadeAudioVolume(1);
      return;
    }
  } while( true );
}

