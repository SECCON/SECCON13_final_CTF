#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <mruby.h>
#include <mruby/irep.h>
#include <mruby/compile.h>
#include <mruby/string.h>
#include <mruby/variable.h>

#define BUFSIZE 256

extern const unsigned char src[];



void panic() {
    fprintf(stderr, "unknown error");
    exit(1);
}

int main(void) {
    char buf[BUFSIZE];
    puts("Input flag:");
    if (!fgets(buf, BUFSIZE, stdin)) {
        panic();
    }

    mrb_state *mrb = mrb_open();
    if (!mrb) {
        panic();
    }

    mrb_value input = mrb_str_new_cstr(mrb, buf);
    mrb_gv_set(mrb, mrb_intern(mrb, "$input", strlen("$input")), input);

    mrb_load_irep(mrb, src);
#ifdef DEBUG
    if (mrb->exc) {
        mrb_print_error(mrb);
    }
#endif
    mrb_close(mrb);
    return 0;
}
