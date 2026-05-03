
void FUN_8005b0c4(int *param_1)

{
  bool bVar1;
  int iVar2;
  
  FUN_8002b8d0();
  FUN_80055f3c();
  FUN_8005d200(&DAT_800d1300);
  FUN_8005d23c(&DAT_801f8000);
  FUN_8005d138();
  FUN_800552fc(&DAT_800b54b0);
  FUN_80055f88();
  DAT_800cd5e0 = &DAT_800cd5b0;
  DAT_800cd5c8 = FUN_8005d20c(0x10000);
  DAT_800cd5cc = FUN_8005d20c(0x11000);
  DAT_800cd5d0 = FUN_8005d20c(0x1e000);
  DAT_800cd5d4 = FUN_8005d20c(0x1e000);
  DAT_800cd5d8 = FUN_8005d20c(0x7800);
  DAT_800cd5dc = FUN_8005d20c(0x7800);
  DAT_800cd5b2 = *(undefined2 *)((int)param_1 + 6);
  DAT_800cd5b6 = *(undefined2 *)((int)param_1 + 10);
  DAT_800cd5b4 = (undefined2)param_1[2];
  DAT_800cd5b8 = FUN_800544d8((int)(short)param_1[1]);
  DAT_800cd5bc = *DAT_800cbb64 + (short)param_1[3];
  DAT_800cd5c0 = DAT_800cbb64[2] + *(short *)((int)param_1 + 0xe);
  DAT_800cd5be = DAT_800cbb64[1] + (short)param_1[3];
  DAT_800cd5c2 = DAT_800cbb64[3] + *(short *)((int)param_1 + 0xe);
  FUN_8005adf4();
  DAT_800cd5a0 = &DAT_800cbb7e;
  DAT_800cbba8 = 0;
  FUN_8002b3f4(0x100);
  do {
    FUN_8005af50();
    iVar2 = 0;
    if (DAT_800cd614 == 0) {
      iVar2 = 1000000;
      do {
        if (DAT_800cd604 != 0) break;
        bVar1 = -1 < iVar2;
        iVar2 = iVar2 + -1;
      } while (bVar1);
      DAT_800cd604 = 0;
      DAT_800cd608 = 0xffffffff;
      if (DAT_800cd60c != 0) {
        DAT_800cd614 = -1;
        DecDCToutCallback((func *)0x0);
        FUN_800a867c();
        do {
          iVar2 = CdControlB('\t',(u_char *)0x0,(u_char *)0x0);
        } while (iVar2 == 0);
      }
      iVar2 = -1;
      DAT_800cd610 = DAT_800cd610 + 1;
    }
    if ((*param_1 != 0) && ((DAT_800cd70c & 0x8f0) != 0)) {
      DAT_800cd60c = -1;
    }
    FUN_80055570();
    if (iVar2 == 0) {
      FUN_8002b3f4(1);
      return;
    }
  } while( true );
}

