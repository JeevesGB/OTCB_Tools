<img src="img/otcb1/logo.png" width=300>

[Go Back](/README.md)

####    Filetypes

| Extension | Found In | Likely Purpose |
|-----------|----------|-----------------|
| `.DA` | ROOT | Audio/data archive files |
| `.BIN` | BIN, OPT/C0, OPT/TIM | Generic binary data (course chunks, car models, menu/UI graphics) |
| `.STR` | OPT, STRDAT, STRDAT/OP, STRDAT/SP | Streamed video/FMV files (opening, shop, cutscenes) |
| `.MDT` | OPT/C0 | Track/course model data |
| `.TDT` | OPT/C0 | Track texture data (paired with `.MDT` files) |
| `.VB` | OPT/C0, SND | Sound bank data (engine audio, system sound) |
| `.VHX` | OPT/C0 | Sound header data (paired with `.VB` files) |
| `.TMD` | OPT/C0, OPT/TIM | PlayStation 3D model files |
| `.MSG` | OPT/MSG2 | Message/dialogue text data |
| `.SEP` | SND | System sound effect/sequence data |
| `.VH` | SND | Sound header bank (paired with `.VB` files) |
| *(none)* | ROOT | `MAINMENU` and `SLPM_802.03` files with no extension |

####    Game File Structure

```
    ROOT
    |  ├── BIN
    |  |
    |  ├── OPT
    |  |   |  ├── C0
    |  |   |  ├── MSG2
    |  |   |  └── TIM
    |  |   ├── MTO.STR
    |  |   └── OPTION
    |  |
    |  ├── SND
    |  |    ├── SYSTEM.SEP
    |  |    ├── SYSTEM.VB
    |  |    └── SYSTEM.VH
    |  |     
    |  └── STRDAT
    |       |  ├── SP
    |       |  └── OP
    |       └── MTO.STR
    |
    ├── MAINMENU
    ├── SLPM_802.03
    ├── SYSTEM.CNF
    ├── T02.DA
    ├── T03.DA
    ├── T04.DA
    ├── T05DMY0.DA
    └── T05DMY1.DA
    
```

####    Game File Structure (Extended)

```
ROOT
├── MAINMENU
├── SLPM_802.03
├── SYSTEM.CNF
├── T02.DA
├── T03.DA
├── T04.DA
├── T05DMY0.DA
├── T05DMY1.DA
├── BIN
│   ├── BIN00.BIN
│   ├── BIN01.BIN
│   ├── BIN02.BIN
│   ├── BIN03.BIN
│   ├── BIN04.BIN
│   ├── BIN05.BIN
│   ├── BIN06.BIN
│   ├── BIN07.BIN
│   ├── BIN08.BIN
│   ├── BIN09.BIN
│   ├── BIN10.BIN
│   ├── BIN11.BIN
│   └── BIN12.BIN
│
├── OPT
│   ├── MTO.STR
│   ├── OPTION
│   ├── C0
│   │   ├── COURSE1.MDT
│   │   ├── COURSE1.TDT
│   │   ├── ENGINE02.VB
│   │   ├── ENGINE02.VHX
│   │   ├── ENGINE19.VB
│   │   ├── ENGINE19.VHX
│   │   ├── FD7.BIN
│   │   ├── FD7.MDT
│   │   ├── FD7_AMA.BIN
│   │   ├── FD7_AMA.MDT
│   │   ├── GTR33.BIN
│   │   ├── GTR33.MDT
│   │   ├── MINES33.BIN
│   │   ├── MINES33.MDT
│   │   ├── MYAT.TMD
│   │   ├── SYS_GM1.VB
│   │   ├── SYS_GM1.VHX
│   │   ├── SYS_SUB.VB
│   │   └── SYS_SUB.VHX
│   │
│   ├── MSG2
│   │   ├── KAN33.MSG
│   │   ├── MIN33.MSG
│   │   ├── REAFD.MSG
│   │   ├── SHOP.MSG
│   │   └── VEL33.MSG
│   │
│   └── TIM
│       ├── AMAMIYA.BIN
│       ├── GAME.BIN
│       ├── LOAD.BIN
│       ├── MENU.BIN
│       ├── MINES.BIN
│       ├── REMIX.BIN
│       ├── SHOPSKY.BIN
│       ├── SHOP_G.BIN
│       ├── SHOP_G.TMD
│       ├── SORA.BIN
│       ├── SYS.BIN
│       ├── S_WANGAN.BIN
│       ├── TG.BIN
│       ├── TITLE.BIN
│       └── TUNESEL.BIN
│
├── SND
│   ├── SYSTEM.SEP
│   ├── SYSTEM.VB
│   └── SYSTEM.VH
│
└── STRDAT
    ├── MTO.STR
    ├── OP
    │   ├── CRASH1.STR
    │   ├── CRASH2.STR
    │   ├── DIGEST1.STR
    │   ├── DIGEST2.STR
    │   ├── INADA1.STR
    │   ├── INADA2.STR
    │   ├── YAMADA1.STR
    │   ├── YAMADA2.STR
    │   ├── YATABE1.STR
    │   └── YATABE2.STR
    │
    └── SP
        ├── SHOP01.STR
        ├── SHOP01R.STR
        ├── SHOP02.STR
        ├── SHOP02R.STR
        ├── SHOP03.STR
        ├── SHOP03R.STR
        ├── SHOP04.STR
        ├── SHOP04R.STR
        ├── SHOP05.STR
        ├── SHOP05R.STR
        ├── SHOP06.STR
        ├── SHOP06R.STR
        ├── SHOP07.STR
        ├── SHOP07R.STR
        ├── SHOP08.STR
        ├── SHOP08R.STR
        ├── SHOP09.STR
        ├── SHOP09R.STR
        ├── SHOP10.STR
        ├── SHOP10R.STR
        ├── SHOP11.STR
        └── SHOP11R.STR
    
```

[Go Back](/README.md)

###### JejCo 2026