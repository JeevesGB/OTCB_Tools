
void main(void)

{
  __main();
  FUN_8009bc4c(0);
  ResetCallback();
  FUN_800a166c();
  VSyncCallback((f *)&LAB_80023b40);
  DrawSyncCallback((func *)&LAB_80023b48);
  FUN_800a167c();
  FUN_800543a8();
  FUN_8005e434();
  FUN_8005d0f0();
  FUN_8002b2a8();
  FUN_80059410();
  DAT_800cbac8 = 4;
  do {
    (*(code *)(&PTR_LAB_800ac63c)[DAT_800cbac8])();
  } while( true );
}

