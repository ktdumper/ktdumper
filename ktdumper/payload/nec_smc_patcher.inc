/* This disables MMU and patches out the MMU call so it's not called again */
static int once;

if (!once) {
    once = 1;

    int reg;
    __asm__ volatile(
        /* disable mmu which got enabled by the jumper */
        "mrc p15, 0, %0, c1, c0, 0\n"
        "bic %0, %0, #0x1\n"
        "mcr p15, 0, %0, c1, c0, 0\n"
        : "=r"(reg)
    );

    *(uint32_t*)KT_patch = 0;
    __asm__ volatile("mcr p15, 0, %0, c7, c10, 1" :: "r"(KT_patch));
    __asm__ volatile("mcr p15, 0, %0, c7, c5, 0" :: "r"(0));

    return;
}
