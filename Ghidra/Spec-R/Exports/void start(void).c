
/* WARNING: Removing unreachable block (ram,0x8009af24) */
/* Possible SNMAIN.OBJ/__SN_ENTRY_POINT */

void start(void)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 unaff_s0;
  undefined4 unaff_s1;
  uint uVar3;
  undefined4 unaff_retaddr;
  undefined4 uVar4;
  
  puVar2 = &DAT_800cbac0;
  do {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  } while (puVar2 < &DAT_800d1300);
  uVar3 = DAT_800c45e8 - 8U | 0x80000000;
  DAT_800c45c8 = ((DAT_800c45e8 - 8U) - DAT_800c45e4) - 0xd1300;
  DAT_800c45c4 = &DAT_800d1300;
  DAT_800cbac0 = unaff_retaddr;
  InitHeap((ulong *)&DAT_800d1304,DAT_800c45c8);
  uVar4 = 0x8009aee0;
  main();
  iVar1 = DAT_800c45c0;
  trap(1);
  *(undefined4 *)(uVar3 - 0xc) = unaff_s0;
  *(undefined4 *)(uVar3 - 8) = unaff_s1;
  *(undefined4 *)(uVar3 - 4) = uVar4;
  if (iVar1 == 0) {
    DAT_800c45c0 = 1;
  }
  return;
}

