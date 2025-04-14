#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PLAYER_1 (1 << 0)
#define PLAYER_2 (1 << 1)
#define BOARD_SIZE 6

typedef struct {
  size_t player;
  size_t score[2];
  char board[BOARD_SIZE][BOARD_SIZE];
} game_t;

size_t game_count, reset_count;

typedef struct {
	char *ptr;
	size_t len;
} name_t;
name_t name[2];

void die(const char *s) {
  printf("[ERROR] %s\n", s);
  exit(1);
}

void game_show(game_t *game) {
  for (size_t y = 0; y < BOARD_SIZE; y++) {
    for (size_t x = 0; x < BOARD_SIZE; x++) {
      if (game->board[y][x] == PLAYER_1)
        putchar('o');
      else if (game->board[y][x] == PLAYER_2)
        putchar('x');
      else
        putchar('.');
    }
    putchar('\n');
  }
}

int game_winner(game_t *game) {
  size_t i, j;
  int t;

  for (i = 0; i < BOARD_SIZE; i++) {
    for (t = PLAYER_1 | PLAYER_2, j = 0; j < BOARD_SIZE; t &= game->board[i][j], j++);
    if (t) return t;
    for (t = PLAYER_1 | PLAYER_2, j = 0; j < BOARD_SIZE; t &= game->board[j][i], j++);
    if (t) return t;
  }

  for (t = PLAYER_1 | PLAYER_2, i = 0; i < BOARD_SIZE; t &= game->board[i][i], i++); 
  if (t) return t;
  for (t = PLAYER_1 | PLAYER_2, i = 0; i < BOARD_SIZE; t &= game->board[i][BOARD_SIZE-i-1], i++);
  if (t) return t;

  for (i = 0; i < BOARD_SIZE; i++)
    for (j = 0; j < BOARD_SIZE; j++)
      if (game->board[i][j] == 0)
        return 0;

  return PLAYER_1 | PLAYER_2;
}

void game_turn(game_t *game) {
  size_t offset, top;

  printf("\n--- Player %ld ---\n", game->player);
  game_show(game);

  while (1) {
    printf("Position (1-%d): ", BOARD_SIZE);
    if (scanf("%ld%*c", &offset) != 1)
      exit(1);

    if (offset <= 0 || offset > BOARD_SIZE) {
      puts("[-] Invalid position");
      continue;
    }

    for (size_t y = BOARD_SIZE - 1; y >= 0; y--) {
      if (game->board[y][offset-1] == 0) {
        top = BOARD_SIZE - y - 1;
        break;
      }
    }

    if (top == BOARD_SIZE) {
      puts("[-] This column is full");
      continue;
    }

    game->board[BOARD_SIZE-top-1][offset-1] = game->player;
    break;
  }

  game->player ^= PLAYER_1 | PLAYER_2;
}

int game_main(const char *name1, const char *name2) {
  int winner, y;
  game_t *game = (game_t*)malloc(sizeof(game_t));
  if (!game)
    die("Cannot allocate memory");

  reset_count++;

  do {
  	game_count++;
    printf("\n--- Score ---\n"
           "%s: %ld pt\n"
           "%s: %ld pt\n",
           name1, game->score[0], name2, game->score[1]);

    game->player = 1;
    memset(game->board, 0, sizeof(game->board));

    while ((winner = game_winner(game)) == 0)
      game_turn(game);

    switch (winner) {
      case PLAYER_1:
        printf("\n--- Winner is %s ---\n", name1);
        game->score[0]++;
        break;

      case PLAYER_2:
        printf("\n--- Winner is %s ---\n", name2);
        game->score[1]++;
        break;

      default:
        puts("\n--- Draw ---");
    }

    game_show(game);

    printf("\nContinue? [No=0 / Yes=1 / Reset=2]: ");
    if (scanf("%d%*c", &y) != 1)
      exit(1);
  } while (y == 1);

  free(game);
  return y;
}

int main() {
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  puts(" ___                          _                   __       _ \n"
       "(  _`\\                     _ ( )_                /  \\     ( )\n"
       "| ( (_) _ __   _ _  _   _ (_)| ,_)   _     ___  (_/\\_)   _| |\n"
       "| |___ ( '__)/'_` )( ) ( )| || |   /'_`\\ /' _ `\\       /'_` |\n"
       "| (_, )| |  ( (_| || \\_/ || || |_ ( (_) )| ( ) |      ( (_| |\n"
       "(____/'(_)  `\\__,_)`\\___/'(_)`\\__)`\\___/'(_) (_)      `\\__,_)");

  do {
    printf("\nPlayer 1's name: ");
    getline(&name[0].ptr, &name[0].len, stdin);
    name[0].ptr[strcspn(name[0].ptr, "\n")] = '\0';

    printf("\nPlayer 2's name: ");
    getline(&name[1].ptr, &name[1].len, stdin);
    name[1].ptr[strcspn(name[1].ptr, "\n")] = '\0';
  } while (game_main(name[0].ptr, name[1].ptr) == 2);

  printf("Total count: game -> %ld times, reset -> %ld times\n", game_count, reset_count);

  return 0;
}
