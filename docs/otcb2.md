<img src="img/otcb2/logo.png" width=300>

[Go Back](/README.md)

####    Filetypes

| Extension | Found In | Likely Purpose |
|-----------|----------|-----------------|
| `.MDB` | C0–C4, MODEL, OTHER | Car/model data files |
| `.MBF` | C0–C4 | Car group/format data (paired with `.MDB` files) |
| `.MDT` | CS | Track model/geometry data |
| `.TDT` | CS | Track texture data (paired with `.MDT` files) |
| `.DA` | DA | Audio/data archive files |
| `.DAT` | MODEL | Model/course data (with `_BK` backup variants) |
| `.BIN` | PARTS, PTIM, SHOP, TIM, TIRE1–3, TUNE | Generic binary data (parts, textures, shop menus, tuning) |
| `.VOI` | S0–S3 | Voice/audio clips (driver dialogue, per car) |
| `.VHB` | SE | Sound/voice header bank |
| `.SHB` | SE | Sound header bank (sequence files) |
| `.STR` | STR | Streamed video/FMV files (opening, ending, shop cutscenes) |
| *(none)* | DA | `DUMMY` placeholder file with no extension |

####    Game File Structure

```
    ROOT
    ├── C0 - .car files
    ├── C1 - .car files
    ├── C2 - .car files
    ├── C3 - .car files
    ├── C4 - .car files
    ├── CS - track files
    ├── DA - data archives
    ├── MODEL - 3D model files
    ├── OTHER - misc/unknown files
    ├── PARTS - part data files
    ├── PTIM - part texture .TIM images
    ├── S0 - system/save files
    ├── S1 - system/save files
    ├── S2 - system/save files
    ├── S3 - system/save files
    ├── SE - .SHB & .VHB audio
    ├── SHOP - shop data files
    ├── STR - video files
    ├── TIM - .TIM images
    ├── TIRE1 - tire texture files
    ├── TIRE2 - tire texture files
    ├── TIRE3 - tire texture files
    ├── TUNE - tuning data files
    ├── SLPS_018.57
    ├── SYS.BIN
    ├── SYS512.BIN
    └── SYSTEM.CNF
```

####    Game File Structure (Extended)

```
ROOT
├── C0
│   ├── AE86T.MDB
│   ├── EK9.MDB
│   ├── EUNOS.MDB
│   ├── FGRP0.MBF
│   ├── GLANZA.MDB
│   ├── INTEGRA.MDB
│   ├── JAM86T.MDB
│   ├── LGRP0.MBF
│   ├── REEUNOS.MDB
│   ├── TEK9.MDB
│   ├── TGLANZA.MDB
│   └── TINTEGRA.MDB
│
├── C1
│   ├── 180SX.MDB
│   ├── AUTOS13.MDB
│   ├── EVO4.MDB
│   ├── FGRP1.MBF
│   ├── FKIMR2.MDB
│   ├── HKSEVO4.MDB
│   ├── LGRP1.MBF
│   ├── S13.MDB
│   ├── S14.MDB
│   ├── SW.MDB
│   ├── TOP_S14.MDB
│   └── VS180SX.MDB
│
├── C2
│   ├── CZ32.MDB
│   ├── ESPJZX.MDB
│   ├── EVO5.MDB
│   ├── FGRP2.MBF
│   ├── HKSEVO5.MDB
│   ├── IMPREZA.MDB
│   ├── JZX100.MDB
│   ├── LGRP2.MBF
│   ├── SOARER.MDB
│   ├── TIMPREZA.MDB
│   ├── TSOARER.MDB
│   └── VSZ32.MDB
│
├── C3
│   ├── 80_T_S.MDB
│   ├── AUGTR32.MDB
│   ├── ESPRIT33.MDB
│   ├── FD7.MDB
│   ├── FGRP3.MBF
│   ├── GTR32.MDB
│   ├── GTR33.MDB
│   ├── GTR34.MDB
│   ├── JZA80.MDB
│   ├── LGRP3.MBF
│   ├── MINR34.MDB
│   └── REFD3S.MDB
│
├── C4
│   ├── AE101.MDB
│   ├── ANNV7.MDB
│   ├── BLITZ.MDB
│   ├── DAIS14.MDB
│   ├── DRAGR.MDB
│   ├── EGRP0.MBF
│   ├── EGRP1.MBF
│   ├── EGRP2.MBF
│   ├── EGRP3.MBF
│   ├── N1CELICA.MDB
│   ├── NMKN.MDB
│   ├── R33TAZ.MDB
│   ├── R33WAGON.MDB
│   ├── S15.MDB
│   ├── SIL80.MDB
│   ├── SROC.MDB
│   ├── VMAX.MDB
│   └── VXHL.MDB
│
├── CS
│   ├── CIRCUIT1.MDT
│   ├── CIRCUIT1.TDT
│   ├── CIRCUIT2.MDT
│   ├── CIRCUIT2.TDT
│   ├── HIGHWAY2.MDT
│   ├── HIGHWAY2.TDT
│   ├── HIGHWAY3.MDT
│   ├── HIGHWAY3.TDT
│   ├── SOUKO1.MDT
│   ├── SOUKO1.TDT
│   ├── SOUKO2.MDT
│   ├── SOUKO2.TDT
│   ├── TOUGE2.MDT
│   ├── TOUGE2.TDT
│   ├── TOUGE3.MDT
│   ├── TOUGE3.TDT
│   ├── TOUGE4.MDT
│   ├── TOUGE4.TDT
│   ├── TOUGE5.MDT
│   ├── TOUGE5.TDT
│   ├── TOUGE_N.MDT
│   ├── TOUGE_N.TDT
│   ├── WANGAN1.MDT
│   ├── WANGAN1.TDT
│   ├── WANGAN2.MDT
│   └── WANGAN2.TDT
│
├── DA
│   ├── DUMMY
│   ├── GOAL_BGM.DA
│   ├── OP2_T01.DA
│   ├── OP2_T02.DA
│   ├── OP2_T03.DA
│   ├── OP2_T04.DA
│   ├── OP2_T05.DA
│   └── OP2_T06.DA
│
├── MODEL
│   ├── AMEMIYA.MDB
│   ├── CIRCUIT.DAT
│   ├── CIRC_BK.DAT
│   ├── DAI.MDB
│   ├── HIGH.DAT
│   ├── HIGH_BK.DAT
│   ├── HIRATA.MDB
│   ├── MAEKAWA.MDB
│   ├── MUKAI.MDB
│   ├── NAGATA.MDB
│   ├── NIIKURA.MDB
│   ├── NOMKEN.MDB
│   ├── OTOU.DAT
│   ├── OTOU_BK.DAT
│   ├── SAWA.MDB
│   ├── SOUKO.DAT
│   ├── SOUKO_BK.DAT
│   ├── TARZAN.MDB
│   ├── TOUGE.DAT
│   ├── TOUGE_BK.DAT
│   ├── WANGAN.DAT
│   ├── WAN_BK.DAT
│   ├── YAMASAWA.MDB
│   ├── YOKOMAKU.MDB
│   └── YOKOYAMA.MDB
│
├── OTHER
│   └── PACK.MDB
│
├── PARTS
│   ├── BRKPAT.BIN
│   ├── COLPAT.BIN
│   ├── CPUPAT.BIN
│   ├── DRVPAT.BIN
│   ├── KYUPAT.BIN
│   ├── MECPAT.BIN
│   ├── MUFPAT.BIN
│   ├── PROCPAT.BIN
│   ├── SUSPAT.BIN
│   └── TURBPAT.BIN
│
├── PTIM
│   ├── S9_BRA.BIN
│   ├── S9_COO.BIN
│   ├── S9_DRI.BIN
│   ├── S9_ELE.BIN
│   ├── S9_EXH.BIN
│   ├── S9_KAK.BIN
│   ├── S9_MEC.BIN
│   ├── S9_MUF.BIN
│   ├── S9_SAS.BIN
│   └── S9_TUR.BIN
│
├── S0
│   ├── AE86MF0.VOI
│   ├── AE86MF1.VOI
│   ├── AE86MF2.VOI
│   ├── AE86MF3.VOI
│   ├── BJZ80MF0.VOI
│   ├── BJZ80MF1.VOI
│   ├── BJZ80MF2.VOI
│   ├── BJZ80MF3.VOI
│   ├── EK9MF0.VOI
│   ├── EK9MF1.VOI
│   ├── EK9MF2.VOI
│   ├── EK9MF3.VOI
│   ├── EP91MF0.VOI
│   ├── EP91MF1.VOI
│   ├── EP91MF2.VOI
│   ├── EP91MF3.VOI
│   ├── ER33MF0.VOI
│   ├── ER33MF1.VOI
│   ├── ER33MF2.VOI
│   └── ER33MF3.VOI
│
├── S1
│   ├── EVOMF0.VOI
│   ├── EVOMF1.VOI
│   ├── EVOMF2.VOI
│   ├── EVOMF3.VOI
│   ├── GC8MF0.VOI
│   ├── GC8MF1.VOI
│   ├── GC8MF2.VOI
│   ├── GC8MF3.VOI
│   ├── JZ100MF0.VOI
│   ├── JZ100MF1.VOI
│   ├── JZ100MF2.VOI
│   ├── JZ100MF3.VOI
│   ├── JZ80MF0.VOI
│   ├── JZ80MF1.VOI
│   ├── JZ80MF2.VOI
│   ├── JZ80MF3.VOI
│   ├── MR2MF0.VOI
│   ├── MR2MF1.VOI
│   ├── MR2MF2.VOI
│   └── MR2MF3.VOI
│
├── S2
│   ├── R33MF0.VOI
│   ├── R33MF1.VOI
│   ├── R33MF2.VOI
│   ├── R33MF3.VOI
│   ├── RX7MF0.VOI
│   ├── RX7MF1.VOI
│   ├── RX7MF2.VOI
│   ├── RX7MF3.VOI
│   ├── S13MF0.VOI
│   ├── S13MF1.VOI
│   ├── S13MF2.VOI
│   ├── S13MF3.VOI
│   ├── S14MF0.VOI
│   ├── S14MF1.VOI
│   ├── S14MF2.VOI
│   ├── S14MF3.VOI
│   ├── ZZ30MF0.VOI
│   ├── ZZ30MF1.VOI
│   ├── ZZ30MF2.VOI
│   └── ZZ30MF3.VOI
│
├── S3
│   ├── RV1.VOI
│   ├── RV2.VOI
│   ├── RV3.VOI
│   ├── RV4.VOI
│   └── RV5.VOI
│
├── SE
│   ├── GAME0.VHB
│   ├── RACE0.VHB
│   ├── SEQ03.SHB
│   ├── SEQ04.SHB
│   ├── SEQ05.SHB
│   ├── SEQ06L.SHB
│   ├── SEQ06W.SHB
│   ├── SEQ07.SHB
│   ├── SEQ08.SHB
│   ├── SEQ11.SHB
│   ├── SEQ1212.SHB
│   ├── SEQ123.SHB
│   ├── SEQ13.SHB
│   ├── SEQ14.SHB
│   ├── SEQ16.SHB
│   ├── SEQ17.SHB
│   └── SEQ18.SHB
│
├── SHOP
│   ├── AMAMIYA.BIN
│   ├── AUTOSEL.BIN
│   ├── ESPRIT.BIN
│   ├── FUKUI.BIN
│   ├── HKSKAN.BIN
│   ├── JAM.BIN
│   ├── MINES.BIN
│   ├── TOPFUEL.BIN
│   ├── TOPSEC.BIN
│   └── VEILSIDE.BIN
│
├── STR
│   ├── ENDING.STR
│   ├── JLOGO2.STR
│   ├── MTO.STR
│   ├── OPENING.STR
│   ├── SHOP01.STR
│   ├── SHOP02.STR
│   ├── SHOP03.STR
│   ├── SHOP04.STR
│   ├── SHOP05.STR
│   ├── SHOP06.STR
│   ├── SHOP07.STR
│   ├── SHOP08.STR
│   ├── SHOP09.STR
│   └── SHOP10.STR
│
├── TIM
│   ├── ARCADE.BIN
│   ├── CHALENG.BIN
│   ├── CHOICE.BIN
│   ├── CONFIG.BIN
│   ├── CREDIT.BIN
│   ├── GAME2D.BIN
│   ├── PRESENT.BIN
│   ├── RIVAL.BIN
│   ├── RIVAL1.BIN
│   ├── RIVAL2.BIN
│   ├── RIVAL3.BIN
│   ├── S9_BRA.BIN
│   ├── S9_COO.BIN
│   ├── S9_DRI.BIN
│   ├── S9_ELE.BIN
│   ├── S9_EXH.BIN
│   ├── S9_KAK.BIN
│   ├── S9_MEC.BIN
│   ├── S9_MUF.BIN
│   ├── S9_SAS.BIN
│   ├── S9_TUR.BIN
│   ├── TITLE.BIN
│   └── TUNE.BIN
│
├── TIRE1
│   ├── AE86W.BIN
│   ├── CN9AW.BIN
│   ├── CP9AW.BIN
│   ├── CZ32W.BIN
│   ├── DC2W.BIN
│   ├── EK9W.BIN
│   ├── EP91W.BIN
│   ├── FD3SW.BIN
│   ├── GC8W.BIN
│   ├── J100W.BIN
│   ├── JZ80W.BIN
│   ├── NB8CW.BIN
│   ├── R32W.BIN
│   ├── R33W.BIN
│   ├── R34W.BIN
│   ├── RS13W.BIN
│   ├── S13W.BIN
│   ├── S14W.BIN
│   ├── SW20W.BIN
│   └── ZZ30W.BIN
│
├── TIRE2
│   ├── AM_FD3SW.BIN
│   ├── AM_NB8CW.BIN
│   ├── AS_32RW.BIN
│   ├── AS_S13W.BIN
│   ├── ES_33RW.BIN
│   ├── ES_J100W.BIN
│   ├── GA_SW20W.BIN
│   ├── GA_ZZ30W.BIN
│   ├── HK_CN9AW.BIN
│   ├── HK_CP9AW.BIN
│   ├── JA_AE86W.BIN
│   ├── JA_EP91W.BIN
│   ├── MI_34RW.BIN
│   ├── MI_GC8W.BIN
│   ├── TF_DC2W.BIN
│   ├── TF_EK9W.BIN
│   ├── TS_JZ80W.BIN
│   ├── TS_S14W.BIN
│   ├── VE_CZ32W.BIN
│   └── VE_RS13W.BIN
│
├── TIRE3
│   ├── A_TIRE.BIN
│   ├── CEL_TIRE.BIN
│   ├── DAIS14.BIN
│   ├── S15_TIRE.BIN
│   ├── SIL8_TIR.BIN
│   ├── TAZ_TIRE.BIN
│   ├── TYRE_AN7.BIN
│   ├── TYRE_BLT.BIN
│   ├── TYRE_DGR.BIN
│   ├── TYRE_NMK.BIN
│   ├── TYRE_SRC.BIN
│   ├── TYRE_VMX.BIN
│   ├── TYRE_VXH.BIN
│   └── W_TIRE.BIN
│
├── TUNE
│   ├── AME.BIN
│   ├── DAI.BIN
│   ├── HIR.BIN
│   ├── MAE.BIN
│   ├── MUK.BIN
│   ├── NAG.BIN
│   ├── NIC.BIN
│   ├── NOM.BIN
│   ├── SAW.BIN
│   ├── TARZAN.BIN
│   ├── YAM.BIN
│   ├── YOC.BIN
│   └── YOK.BIN
│
├── SLPS_018.57
├── SYS.BIN
├── SYS512.BIN
└── SYSTEM.CNF
```

[Go Back](/README.md)

###### JejCo 2026